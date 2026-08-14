# Object Storage & Direct Browser Uploads

S3-compatible object storage, presigned URLs, and the CORS/public-access rules that decide
whether a file upload actually works. Part of the [[devops/README|DevOps curriculum]].

Complements [[devops/minio-guide|the MinIO guide]] (self-hosting the same API) and
[[devops/03-cloud/aws-cloud-reference|the AWS reference]] (S3 within AWS). This file is the
provider-neutral cut: the upload architecture and the two configuration surfaces everyone
gets wrong the first time.

Written 2026-08-12 while building a media pipeline on Cloudflare R2.

---

## 1. The S3 API Is a Standard, Not a Product

S3's HTTP API is implemented by most object stores — Cloudflare R2, Backblaze B2,
DigitalOcean Spaces, MinIO, Wasabi. The AWS SDK talks to all of them; only the endpoint and
credentials change:

```ts
new S3Client({
  region: "auto",                                              // R2 has no AWS-style regions
  endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,  // the only provider-specific line
  credentials: { accessKeyId, secretAccessKey },
});
```

Keep this in one module and switching providers is an env change. Worth doing even if you
never switch — it makes local MinIO viable for tests.

### Choosing: egress is usually the deciding cost

| | Storage | Egress | Notes |
|---|---|---|---|
| AWS S3 | Cheap | **Charged per GB** | Deepest feature set, best ecosystem |
| Cloudflare R2 | Comparable | **Free** | S3-compatible; no lifecycle-rule parity with AWS |
| Backblaze B2 | Cheapest | Free to Cloudflare | Slower |
| MinIO (self-host) | Your disk | Your bandwidth | Full control, you run it |

Storage is rarely the expensive part — **egress is**. Egress means every byte leaving the
bucket, and it's easy to underestimate: a CDN pulling, a mobile app re-downloading, and in
particular **third-party APIs that ingest by URL**. Publishing one video to a platform that
fetches it is a full-size download every time.

If your workload is write-once-read-many with large files, free egress dominates the
comparison. That's the whole reason R2 tends to win for media.

---

## 2. Never Proxy Uploads Through Your API

The naive design — browser POSTs the file to your server, your server forwards it to storage
— breaks in three ways:

1. **Body size limits.** Frameworks cap request bodies for good reason (`express.json` often
   at a few hundred KB). Raising the cap moves the problem rather than solving it.
2. **Process occupancy.** A 500MB upload ties up a request handler for its entire duration.
   Ten concurrent uploads on a single-threaded runtime and the API stops answering anything.
3. **Double bandwidth and double latency.** Bytes travel client → you → storage. You pay
   ingress and egress and add a hop.

### The presigned URL pattern

A presigned URL is a time-limited, cryptographically signed permission slip: *"the bearer may
perform this one operation on this one key, until this timestamp."* It carries its own
authorisation, so the browser can talk to storage directly without ever holding your
credentials.

```
1. POST /media/presign   → your API returns { uploadUrl, key, publicUrl }
2. PUT  <uploadUrl>      → browser → storage.  YOUR SERVER IS NOT INVOLVED.
3. POST /media/confirm   → your API HEADs the object to verify it landed, then records it
```

**Step 3 is not ceremony.** Without it a client can skip step 2 entirely and tell your API
about a file that doesn't exist — or hand you a URL pointing anywhere. Verify server-side
before persisting.

### Constrain the signature

```ts
new PutObjectCommand({
  Bucket, Key: key,
  ContentType: mimeType,     // signed → client cannot upload a different type
  ContentLength: sizeBytes,  // signed → client cannot exceed the declared size
});
```

Putting these *in the signature* makes the storage provider enforce them. Limits checked only
in client-side JavaScript are decoration.

### Key naming

```
uploads/u{userId}/{uuid}.{ext}
```

Namespace by owner so an ownership check is a cheap prefix comparison, and use a UUID rather
than the user's filename — original names bring path traversal, unicode normalisation, and
collisions in exchange for nothing, since nobody sees the key.

---

## 3. CORS — The Failure Everyone Hits Once

**Buckets ship with no CORS policy.** The presign call succeeds (it's your own API, same
origin or already CORS-configured), and then the PUT — a *cross-origin* request to the
storage host — is blocked by the browser before it's even sent.

The signature of this bug: **your server logs look perfectly healthy**, because the failing
request never reaches your server. In the browser you get a cancelled request with no status
code, and JavaScript receives an error with no detail.

```json
[
  {
    "AllowedOrigins": ["http://localhost:3000", "https://app.example.com"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedHeaders": ["content-type"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

- `AllowedOrigins` is an **exact** match — scheme, host and port, no trailing slash.
  `http://localhost:3000`, not `localhost:3000`.
- `AllowedHeaders` must include every header the upload sets. `content-type` is required
  whenever you pin Content-Type into the signature.
- `ExposeHeaders: ["ETag"]` is needed for multipart uploads, which read the ETag per part.
- Preflight responses are cached — **hard-refresh** after changing the policy.

Detect it explicitly in client code, because the generic message is useless:

```ts
xhr.onerror = () => reject(new Error(
  "Could not reach storage. If this is a fresh bucket, check its CORS policy allows PUT from this origin."
));
```

---

## 4. Public Read Is a Separate Setting from CORS

These get conflated constantly. They are unrelated:

- **CORS** governs whether *a browser on your origin* may **write** to the bucket.
- **Public access** governs whether *anonymous clients anywhere* may **read** an object.

You need CORS for uploads, and public read only if something external must fetch the file without
credentials — a CDN, an `<img>` tag, or a third-party API that ingests by URL.

**Development URLs are not production URLs.** R2's `r2.dev` subdomain is rate-limited and
documented as development-only; it also can't sit behind WAF rules or caching. Production
means binding a custom domain to the bucket. Some third parties additionally require you to
**verify the domain** before they'll fetch from it (TikTok does), which forces a real domain
even for testing.

### The alternative to public read

If files are private, don't make the bucket public — issue **presigned GET URLs**, the same
mechanism as upload but for reading, with a short expiry. Public read is for genuinely public
assets only.

---

## 5. Big Files: Multipart and Async Processing

Beyond ~100MB, a single PUT is fragile — one dropped connection and the whole transfer
restarts. Multipart upload splits the object into independently-retryable parts, and you can
presign each part.

For most applications the simpler win is a **size cap** plus clear client-side feedback.
Reach for multipart when you actually have users on unreliable connections uploading large
video.

Also plan for what happens *after* the bytes land — transcoding, thumbnailing, virus
scanning. That belongs in a background job, not the upload request. See
[[backend/README|backend concepts]] on queues.

---

## 6. Checklist for a New Bucket

1. Bucket created, credentials scoped to **that bucket only** (not account-wide)
2. Permission is read+write on objects, not admin
3. CORS policy added for every origin that uploads — including production
4. Public read decided deliberately: enabled with a custom domain, or presigned GETs instead
5. Endpoint and public base URL both in config, never hardcoded
6. Server-side verification (`HEAD`) before persisting a reference
7. Size and MIME type pinned into the presigned signature
8. A cleanup story for orphaned objects — uploads that were never attached to anything

---

## Related
- [[devops/minio-guide|MinIO guide]] — self-hosting an S3-compatible store
- [[devops/03-cloud/aws-cloud-reference|AWS cloud reference]] — S3 specifics within AWS
- [[devops/03-cloud/01-cloud-fundamentals|Cloud fundamentals]]
- [[backend/05-auth/03-oauth-provider-integrations|OAuth provider integrations]] — platforms that ingest media by URL
- [[architecture/system-design-reference|System design reference]]
