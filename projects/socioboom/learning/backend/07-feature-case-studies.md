# SocioBoom Backend — Feature Deep-Dives: Review Poster & Pain-Point Discovery

Split out from the original flat `backend-learning.md` (moved to `learning/archive/`). See also
`learning/backend/06-ai-and-agents.md` (the agent techniques these two features apply),
`learning/backend/02-architecture-and-modules.md` (the module pattern they are built on), and
`learning/frontend/06-feature-walkthroughs.md` (the UI side of both features).

This file covers: the Review Poster feature followed end to end from request to generated content,
the Pain-Point Discovery agent followed the same way, and the Axios patterns used for every
external API call in the codebase — timeouts, error shape normalization, and what
`err.response?.data` actually contains when a platform rejects you.

---

## 13. Feature Deep-Dive: Review Poster

The Review Poster feature transforms the problem of writing marketing content into a three-step workflow: fetch → select → generate.

### Step 1: Fetch Reviews from Platforms

**Google Places:**

```ts
static async fetchGoogleReviews(businessName: string): Promise<Review[]> {
  const apiKey = process.env.GOOGLE_PLACES_API_KEY;

  // Step A: Find the place_id for the business name
  const searchRes = await axios.get(
    'https://maps.googleapis.com/maps/api/place/findplacefromtext/json',
    {
      params: {
        input: businessName,
        inputtype: 'textquery',
        fields: 'place_id,name',
        key: apiKey,
      },
    },
  );
  const placeId = searchRes.data.candidates?.[0]?.place_id;
  if (!placeId) return []; // Business not found

  // Step B: Fetch the reviews using the place_id
  const detailRes = await axios.get(
    'https://maps.googleapis.com/maps/api/place/details/json',
    {
      params: {
        place_id: placeId,
        fields: 'reviews,name',
        key: apiKey,
      },
    },
  );

  // Step C: Normalize the response into the Review interface
  const rawReviews = detailRes.data.result?.reviews ?? [];
  return rawReviews.map((r) => ({
    source: 'google' as const,
    businessName: detailRes.data.result?.name ?? businessName,
    reviewerName: r.author_name,
    reviewText: r.text ?? '',
    rating: r.rating,
  }));
}
```

The Google Places API requires two calls: one to find the `place_id` from a text search, and one to fetch details (including reviews) using that `place_id`. The free tier returns up to 5 reviews per business.

**Yelp:**

```ts
static async fetchYelpReviews(businessName: string, location = 'US'): Promise<Review[]> {
  const headers = { Authorization: `Bearer ${process.env.YELP_API_KEY}` };

  // Search for the business
  const searchRes = await axios.get('https://api.yelp.com/v3/businesses/search', {
    headers,
    params: { term: businessName, location, limit: 1 },
  });

  const bizId: string = searchRes.data.businesses?.[0]?.id;
  if (!bizId) return [];

  // Fetch reviews for that specific business
  const reviewsRes = await axios.get(
    `https://api.yelp.com/v3/businesses/${bizId}/reviews`,
    { headers },
  );

  return (reviewsRes.data.reviews ?? []).map((r) => ({
    source: 'yelp' as const,
    businessName: searchRes.data.businesses[0].name,
    reviewerName: r.user?.name,
    reviewText: r.text ?? '',
    rating: r.rating,
  }));
}
```

**Twitter Mentions:**

```ts
static async fetchTwitterMentions(businessName: string): Promise<Review[]> {
  const { data } = await axios.get('https://api.twitter.com/2/tweets/search/recent', {
    params: {
      query: `"${businessName}" -is:retweet lang:en`,
      max_results: 25,
      'tweet.fields': 'author_id,text',
      expansions: 'author_id',    // Include user objects in the response
      'user.fields': 'username',
    },
    headers: { Authorization: `Bearer ${process.env.TWITTER_BEARER_TOKEN}` },
  });

  // Build a lookup from userId → username
  const users: Record<string, string> = {};
  for (const u of data.includes?.users ?? []) users[u.id] = u.username;

  return (data.data ?? []).map((tweet) => ({
    source: 'twitter' as const,
    businessName,
    reviewerName: tweet.author_id ? `@${users[tweet.author_id]}` : undefined,
    reviewText: tweet.text,
  }));
}
```

Twitter's v2 API uses "expansions" — you request `author_id` on tweets and `expansions: 'author_id'` to get user objects included in the same response. Without expansions you would need a second API call per tweet to look up usernames.

### Step 2: AI Post Generation

```ts
static async generatePosts(req: GeneratePostsRequest): Promise<GeneratedPost[]> {
  const { reviews, businessName, tone = 'professional', targetPlatforms = ['twitter', 'instagram', 'linkedin'] } = req;

  // The system prompt defines the AI's persona and constraints
  const system = `You are a social media marketing expert. Convert customer reviews into compelling social media posts.
Tone: ${tone}. Target platforms: ${targetPlatforms.join(', ')}.
Rules: Keep posts concise, highlight the positive, add relevant emojis, include a call-to-action where natural.
If a business name is provided, mention it naturally. Do NOT make up any details not in the review.`;

  const results: GeneratedPost[] = [];

  // Generate one post per review (sequential to avoid rate limits)
  for (const review of reviews) {
    const user = `Business: ${businessName || review.businessName || 'our business'}
Reviewer: ${review.reviewerName ?? 'a customer'}
Rating: ${review.rating ? `${review.rating}/5` : 'not specified'}
Review: "${review.reviewText}"

Write one social media post that celebrates this review and encourages others to try us out. Return only the post text, no labels.`;

    const content = await generateText(system, user);
    results.push({ review, content });
  }

  return results;
}
```

Key prompt engineering decisions:
- The system prompt establishes tone and platform context once, not per review.
- "Return only the post text, no labels" prevents the AI from prefixing with "Here's your post:".
- "Do NOT make up any details" is a grounding constraint to prevent hallucination.
- Sequential `for...of` instead of `Promise.all` avoids hitting rate limits on the AI provider.

### Step 3: Save and Schedule

After the user selects which generated posts they like, they call:
- `POST /api/v1/reviews/save` to persist the selection to the `ReviewPost` table.
- `POST /api/v1/posts/schedule` (the existing post scheduling endpoint) to actually schedule the post for publishing.

The Review Poster reuses the existing post scheduling system — it does not implement its own scheduling logic.

---

## 14. Feature Deep-Dive: Pain-Point Discovery

This is the most algorithmically complex feature. It chains five AI and API calls in a pipeline.

### The Full Pipeline

```
User sends: { appDescription: "SocioBoom schedules social posts", platforms: ["reddit", "twitter"] }

Step 1: AI extracts search keywords
  → ["can't keep up with social media", "automate instagram posting", "social media scheduling tool"]

Step 2: Search Reddit and/or Twitter with those keywords
  → 50 raw posts

Step 3: AI filters for genuine pain points relevant to the product
  → 12 relevant posts

Step 4: Save session and pain points to database
  → { session: {...}, painPoints: [...] }

Step 5 (later, on demand): AI generates an authentic reply for a specific pain point
  → "I totally get this struggle! I used to spend hours on social media. SocioBoom..."
```

### Step 1: Keyword Extraction

```ts
static async extractKeywords(appDescription: string): Promise<string[]> {
  const system = 'You are a market research expert. Extract search keywords from an app description.';

  const user = `App: "${appDescription}"

Return 5-8 short phrases that people complaining about problems this app solves would likely write.
Examples: "I hate manually posting to instagram", "no time to manage social media"
Return ONLY a JSON array of strings, nothing else.`;

  const raw = await generateText(system, user);

  // Extract JSON from the response (handle case where AI adds surrounding text)
  const match = raw.match(/\[[\s\S]*\]/);
  if (!match) return [appDescription]; // Fallback to the description itself
  return JSON.parse(match[0]) as string[];
}
```

The regex `\[[\s\S]*\]` matches everything from the first `[` to the last `]`, including newlines. This handles cases where the AI puts the JSON array on multiple lines or adds surrounding text. It is a defensive parsing pattern.

### Step 2: Multi-Platform Search

```ts
static async runDiscovery(userId: number, req: SearchRequest) {
  const { appDescription, platforms } = req;

  // Create a session record first (tracks this discovery run)
  const session = await DiscoveryModel.createSession(userId, appDescription, platforms);

  // Get keywords from AI
  const keywords = await DiscoveryService.extractKeywords(appDescription);

  // Search each requested platform in parallel... or sequentially here
  const rawPosts: RawPost[] = [];
  if (platforms.includes('reddit')) {
    const posts = await DiscoveryService.searchReddit(keywords);
    rawPosts.push(...posts);
  }
  if (platforms.includes('twitter')) {
    const posts = await DiscoveryService.searchTwitter(keywords);
    rawPosts.push(...posts);
  }

  // AI filters the results
  const filtered = await DiscoveryService.filterPainPoints(rawPosts, appDescription);

  // Save each filtered post as a PainPoint
  const painPoints: PainPoint[] = [];
  for (const post of filtered) {
    const saved = await DiscoveryModel.savePainPoint(session.id, post);
    painPoints.push(saved);
  }

  return { session, painPoints };
}
```

**Reddit search:**
```ts
static async searchReddit(keywords: string[]): Promise<RawPost[]> {
  const token = await DiscoveryService.getRedditToken();
  const query = keywords.join(' OR '); // Reddit search syntax: keyword1 OR keyword2 OR ...

  const { data } = await axios.get('https://oauth.reddit.com/search', {
    params: { q: query, limit: 25, sort: 'relevance', type: 'link' },
    headers: {
      Authorization: `Bearer ${token}`,
      'User-Agent': 'SocioBoom/1.0', // Reddit requires a User-Agent
    },
  });

  return (data.data?.children ?? []).map((child) => ({
    platform: 'reddit' as DiscoveryPlatform,
    subreddit: child.data.subreddit,
    postUrl: child.data.permalink ? `https://reddit.com${child.data.permalink}` : undefined,
    postAuthor: child.data.author,
    postContent: child.data.selftext || child.data.title || '',
  }));
}
```

**Twitter search:**
```ts
static async searchTwitter(keywords: string[]): Promise<RawPost[]> {
  // Wrap each keyword in quotes for exact phrase matching
  const query = keywords.map((k) => `"${k}"`).join(' OR ');

  const { data } = await axios.get('https://api.twitter.com/2/tweets/search/recent', {
    params: {
      query: `${query} -is:retweet lang:en`, // Exclude retweets, English only
      max_results: 25,
      'tweet.fields': 'author_id,text',
      expansions: 'author_id',
      'user.fields': 'username',
    },
    headers: { Authorization: `Bearer ${process.env.TWITTER_BEARER_TOKEN}` },
  });

  const users: Record<string, string> = {};
  for (const u of data.includes?.users ?? []) {
    users[u.id] = u.username;
  }

  return (data.data ?? []).map((tweet) => ({
    platform: 'twitter' as DiscoveryPlatform,
    postUrl: `https://twitter.com/i/web/status/${tweet.id}`,
    postAuthor: tweet.author_id ? users[tweet.author_id] : undefined,
    postContent: tweet.text,
  }));
}
```

### Step 3: AI Filtering

```ts
static async filterPainPoints(posts: RawPost[], appDescription: string): Promise<RawPost[]> {
  if (posts.length === 0) return [];

  const system = 'You are a market research analyst identifying genuine pain points relevant to a product.';

  const user = `Product: "${appDescription}"

Posts to evaluate:
${posts.map((p, i) => `${i}. "${p.postContent.slice(0, 300)}"`).join('\n')}

Return ONLY a JSON array of the indices (0-based) of posts that express a genuine pain point this product could solve. Example: [0, 2, 5]`;

  const raw = await generateText(system, user);

  // Parse the index array from the AI response
  const match = raw.match(/\[[\s\S]*?\]/); // Non-greedy: first complete array
  if (!match) return posts; // If parsing fails, return all posts (fail open)

  const indices = JSON.parse(match[0]) as number[];
  return indices.map((i) => posts[i]).filter(Boolean); // filter(Boolean) removes any undefined
}
```

Sending all posts in one AI call (batch filtering) is far more efficient than filtering each post individually. The AI sees the full context and can make comparative judgments. The `slice(0, 300)` prevents the prompt from becoming too long if posts are very lengthy.

### Step 4: Generate a Reply (On Demand)

```ts
static async generateResponse(
  painPointContent: string,
  appDescription: string,
  platform: DiscoveryPlatform,
): Promise<string> {
  const system = `You are a savvy growth marketer writing authentic ${platform} replies that help people with their problems while naturally mentioning a relevant product.
Rules: Sound human, not like an ad. Lead with empathy and a useful tip. Mention the product organically, not as a pitch. Keep it under 280 characters for Twitter.`;

  const user = `Our product: "${appDescription}"

Their post: "${painPointContent}"

Write a helpful reply that addresses their pain point and naturally introduces our product as a solution. Return only the reply text.`;

  return generateText(system, user);
}
```

The platform-specific instruction (`Keep it under 280 characters for Twitter`) is built into the prompt. The system prompt instructs the AI to sound human, not like an advertisement, which is critical for this to work — blatant ads get downvoted and banned.

---


## 15. External API Calls with Axios

Axios is an HTTP client. SocioBoom uses it for every external API call.

### Basic Pattern

```ts
import axios from 'axios';

// GET with query params and headers
const { data } = await axios.get('https://api.example.com/resource', {
  params: { key: 'value' },           // Appended to URL: ?key=value
  headers: { Authorization: 'Bearer token' },
});

// POST with JSON body
const { data } = await axios.post('https://api.example.com/resource', body, {
  headers: { 'Content-Type': 'application/json' },
});

// POST with form-encoded body (for OAuth token endpoints)
await axios.post(
  'https://www.reddit.com/api/v1/access_token',
  'grant_type=client_credentials',    // String body, not object
  {
    auth: { username: clientId, password: clientSecret }, // Basic auth
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  },
);
```

**Why axios instead of the built-in `fetch`?** In Node.js 22, `fetch` is available natively. Axios provides:
- Automatic JSON serialization/deserialization
- Query parameter serialization (`params` option)
- Basic auth shortcut (`auth` option)
- Consistent error handling (throws on 4xx/5xx status codes)
- Better TypeScript types

### Error Handling for External API Calls

External APIs can fail. When they do, the controller's try/catch catches the error and returns a 500 response:

```ts
static async fetchGoogle(req: Request, res: Response) {
  try {
    const reviews = await ReviewService.fetchGoogleReviews(businessName);
    res.json({ reviews });
  } catch (error) {
    // If the Google API is down, or the key is invalid, or the business is not found:
    res.status(500).json({ error: (error as Error).message });
  }
}
```

For production, you would differentiate error types:
- API key invalid → 500 (server misconfiguration)
- Business not found → 404
- Google API temporarily down → 503 with retry advice

---


