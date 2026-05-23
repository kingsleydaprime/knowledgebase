# NoSQL — Comprehensive Reference Guide

> A deep, practical reference covering all four NoSQL database families.
> MongoDB, Redis, Cassandra, Neo4j — from data modelling to production patterns.
> Includes when to use each, how they work internally, and polyglot persistence.

---

## Table of Contents

1. [Why NoSQL Exists — The Problem Space](#1-why-nosql-exists--the-problem-space)
2. [The Four NoSQL Families](#2-the-four-nosql-families)
3. [MongoDB — Document Store](#3-mongodb--document-store)
4. [Redis — Key-Value and Data Structures](#4-redis--key-value-and-data-structures)
5. [Cassandra — Wide-Column Store](#5-cassandra--wide-column-store)
6. [Neo4j — Graph Database](#6-neo4j--graph-database)
7. [Elasticsearch — Search Engine Store](#7-elasticsearch--search-engine-store)
8. [When to Use What — Decision Framework](#8-when-to-use-what--decision-framework)
9. [Polyglot Persistence — Using Multiple Databases](#9-polyglot-persistence--using-multiple-databases)

---

## 1. Why NoSQL Exists — The Problem Space

### 1.1 What Relational Databases Don't Handle Well

Relational databases are exceptional for structured data with clear relationships, complex queries, and strong consistency. They struggle with:

**Scale-out writes** — relational databases scale vertically (bigger machine). Sharding a relational database across multiple servers is complex, often requiring middleware, and still has limitations on write throughput.

**Schema rigidity** — adding a column to a table with 500M rows is an expensive operation. In many applications, the schema evolves rapidly and varies between records.

**Hierarchical or graph data** — storing a deeply nested JSON document in a relational schema requires multiple joins. Representing a social graph (friends of friends) with recursive queries is slow and complex.

**High write throughput at scale** — a single PostgreSQL primary handles thousands of writes per second. Cassandra can handle millions per second across a cluster.

**Object-relational impedance mismatch** — application code works with objects and lists. Mapping these to tables, rows, and foreign keys requires either an ORM or a lot of manual transformation.

### 1.2 What NoSQL Means

NoSQL stands for "Not Only SQL" — not a rejection of SQL, but an acknowledgment that SQL is not always the right tool. NoSQL databases make different tradeoffs:

- Sacrifice some query flexibility for write throughput
- Sacrifice strong consistency for availability and partition tolerance
- Sacrifice rigid schema for flexible data models
- Sacrifice complex joins for simple, fast access patterns

### 1.3 The Core Tradeoff

```
Relational:   Strong consistency + complex queries + rigid schema
NoSQL:        High throughput + flexible schema + horizontal scale
              (at the cost of consistency, complex queries, or both)
```

The right choice depends entirely on your access patterns and consistency requirements. Many production systems use both.

---

## 2. The Four NoSQL Families

### 2.1 Document Stores

Store data as documents (JSON, BSON, XML). Each document is self-contained with flexible schema. Documents in the same collection can have different fields.

```json
// A user document — no fixed schema required
{
  "_id": "ObjectId('...')",
  "username": "kingsleydaprime",
  "email": "k@spectroniq.com",
  "preferences": { "theme": "dark", "notifications": true },
  "tags": ["devops", "systems"],
  "address": { "city": "Accra", "country": "GH" }
}
```

**Examples:** MongoDB, CouchDB, Firestore, DocumentDB
**Best for:** Content management, user profiles, product catalogues, any domain with variable-structure data

### 2.2 Key-Value Stores

The simplest data model — every value is stored and retrieved by a unique key. Like a giant hash map. O(1) access. No query language beyond get/set/delete.

```
SET user:42:session "eyJhbGci..." EX 3600
GET user:42:session → "eyJhbGci..."
```

**Examples:** Redis, DynamoDB, Memcached, etcd
**Best for:** Caching, sessions, counters, rate limiting, pub/sub messaging

### 2.3 Wide-Column Stores

Organise data in tables with rows and columns like relational databases, but columns are dynamic — different rows can have different columns, and columns are organised into column families. Optimised for writing and reading large datasets.

```
Cassandra table: user_events
  Partition key: user_id
  Clustering columns: event_time, event_type

Row: user_id=42, event_time=2026-01-15 14:30:00, event_type=LOGIN, ip=192.168.1.1
Row: user_id=42, event_time=2026-01-15 15:00:00, event_type=PURCHASE, item_id=99
```

**Examples:** Cassandra, HBase, Google BigTable, ScyllaDB
**Best for:** Time-series data, IoT, analytics, write-heavy workloads at extreme scale

### 2.4 Graph Databases

Store data as nodes (entities) and edges (relationships). Edges are first-class citizens with their own properties. Traversal-optimised — finding the shortest path or all connections is built into the query language.

```
(Kingsley)-[:FOLLOWS]->(Alice)
(Kingsley)-[:FOLLOWS]->(Bob)
(Alice)-[:FOLLOWS]->(Bob)
(Bob)-[:WORKS_AT]->(Spectroniq)
```

**Examples:** Neo4j, Amazon Neptune, ArangoDB, TigerGraph
**Best for:** Social graphs, recommendation engines, fraud detection, knowledge graphs, dependency analysis

---

## 3. MongoDB — Document Store

### 3.1 How MongoDB Works Internally

MongoDB stores documents as BSON (Binary JSON) — a binary encoding of JSON that adds additional types (Date, ObjectId, Binary). Documents are grouped into **collections** (like tables), which live in **databases**.

**Storage engine:** WiredTiger (default since 3.2). Uses B-tree indexes, MVCC for concurrency, and snappy/zstd compression. Documents are stored on disk in B-tree leaf nodes.

**No fixed schema** — MongoDB does not enforce a schema by default. Documents in the same collection can have completely different fields. You can add schema validation with JSON Schema validators.

**Document size limit:** 16 MB per document. Use GridFS for larger files.

### 3.2 Core Concepts

```
Database    → container for collections (like a PostgreSQL database)
Collection  → group of documents (like a table, but schema-flexible)
Document    → a JSON object stored in a collection (like a row)
Field       → a key-value pair in a document (like a column)
_id         → unique identifier for each document (auto-generated ObjectId if not provided)
ObjectId    → 12-byte BSON type: 4-byte timestamp + 5-byte random + 3-byte counter
```

### 3.3 CRUD Operations

```javascript
// MongoDB Shell / Compass syntax

// ─── INSERT ───────────────────────────────────────────────────────────────────

// Insert one document
db.users.insertOne({
  username: "kingsleydaprime",
  email: "k@spectroniq.com",
  age: 22,
  role: "admin",
  tags: ["devops", "systems"],
  address: { city: "Accra", country: "GH" },
  createdAt: new Date()
});

// Insert many
db.users.insertMany([
  { username: "alice", email: "alice@example.com" },
  { username: "bob", email: "bob@example.com" }
]);

// ─── FIND ─────────────────────────────────────────────────────────────────────

// Find all documents
db.users.find();

// Find with filter
db.users.find({ role: "admin" });
db.users.find({ "address.city": "Accra" });   // dot notation for nested fields

// Find one
db.users.findOne({ email: "k@spectroniq.com" });

// Projection — only return specific fields (1=include, 0=exclude)
db.users.find({ role: "admin" }, { username: 1, email: 1, _id: 0 });

// Comparison operators
db.users.find({ age: { $gt: 18, $lte: 30 } });       // age > 18 AND age <= 30
db.users.find({ age: { $in: [18, 21, 25] } });        // age is 18, 21, or 25
db.users.find({ age: { $nin: [18, 19] } });           // age NOT in list
db.users.find({ email: { $ne: null } });              // email is not null
db.users.find({ deletedAt: { $exists: false } });     // field does not exist

// Logical operators
db.users.find({
  $and: [{ role: "admin" }, { age: { $gte: 18 } }]
});
db.users.find({
  $or: [{ role: "admin" }, { role: "moderator" }]
});
db.users.find({ $nor: [{ role: "banned" }, { isDeleted: true }] });
db.users.find({ role: { $not: { $eq: "banned" } } });

// Array operators
db.users.find({ tags: "devops" });                    // tags array contains "devops"
db.users.find({ tags: { $all: ["devops", "linux"] } }); // contains both
db.users.find({ tags: { $size: 3 } });               // exactly 3 elements
db.users.find({ "tags.0": "devops" });               // first element is "devops"

// Sort, skip, limit
db.users.find().sort({ createdAt: -1 }).skip(20).limit(10);  // page 3
db.users.find().sort({ age: 1, username: 1 });       // sort by age asc, then username

// Count
db.users.countDocuments({ role: "admin" });
db.users.estimatedDocumentCount();                    // faster, approximate

// ─── UPDATE ───────────────────────────────────────────────────────────────────

// Update one (first match)
db.users.updateOne(
  { email: "k@spectroniq.com" },       // filter
  { $set: { role: "superadmin", updatedAt: new Date() } }  // update
);

// Update many
db.users.updateMany(
  { role: "user" },
  { $set: { isVerified: false } }
);

// Update operators
$set      // set a field value
$unset    // remove a field: { $unset: { temporaryToken: "" } }
$inc      // increment: { $inc: { loginCount: 1, age: -1 } }
$mul      // multiply: { $mul: { score: 1.1 } }
$push     // add to array: { $push: { tags: "newTag" } }
$pull     // remove from array: { $pull: { tags: "oldTag" } }
$addToSet // add to array only if not already present
$pop      // remove first (-1) or last (1) element
$rename   // rename a field: { $rename: { "oldName": "newName" } }
$min      // only update if new value is less than current
$max      // only update if new value is greater than current

// Upsert — insert if not found
db.users.updateOne(
  { email: "new@example.com" },
  { $set: { username: "newuser", createdAt: new Date() } },
  { upsert: true }
);

// findOneAndUpdate — returns the document (before or after update)
const updated = db.users.findOneAndUpdate(
  { _id: ObjectId("...") },
  { $inc: { loginCount: 1 } },
  { returnDocument: "after" }  // return updated document
);

// ─── DELETE ───────────────────────────────────────────────────────────────────

db.users.deleteOne({ _id: ObjectId("...") });
db.users.deleteMany({ isDeleted: true, deletedAt: { $lt: new Date(Date.now() - 30*86400000) } });

// findOneAndDelete — returns deleted document
const deleted = db.users.findOneAndDelete({ _id: ObjectId("...") });
```

### 3.4 Data Modelling — Embed vs Reference

The most important MongoDB design decision: embed related data or reference it.

**Embed when:**
- Data is always accessed together
- The embedded data belongs to exactly one parent (1:1 or 1:few)
- The embedded array won't grow unboundedly
- Data doesn't need to be queried independently

**Reference when:**
- Data is shared between multiple documents
- The relationship is many-to-many
- The embedded array could grow unboundedly
- You need to query the related data independently

```javascript
// ─── EMBED: user with address (always accessed together, belongs to one user) ─

{
  "_id": ObjectId("..."),
  "username": "kingsley",
  "address": {               // embedded — always load with user
    "street": "Independence Ave",
    "city": "Accra",
    "country": "GH"
  },
  "recentPosts": [           // embedded — small, fixed-size array
    { "title": "DevOps guide", "slug": "devops-guide", "publishedAt": "..." },
    { "title": "SQL deep dive", "slug": "sql-deep-dive", "publishedAt": "..." }
  ]
}

// ─── REFERENCE: post with author (author shared across many posts) ──────────

// posts collection
{
  "_id": ObjectId("post1"),
  "title": "DevOps on AWS",
  "authorId": ObjectId("user42"),   // reference to users collection
  "content": "...",
  "tags": ["aws", "devops"]
}

// Application-level join:
const post = db.posts.findOne({ slug: "devops-on-aws" });
const author = db.users.findOne({ _id: post.authorId });

// Or with aggregation $lookup (see Section 3.6)

// ─── HYBRID: bounded embed + reference for overflow ──────────────────────────

// Store first 5 comments embedded, reference the rest
{
  "_id": ObjectId("post1"),
  "title": "...",
  "commentCount": 142,
  "recentComments": [          // last 5 comments embedded
    { "author": "Alice", "text": "Great post!", "createdAt": "..." }
  ]
  // full comment history → separate comments collection, queried separately
}
```

### 3.5 Schema Validation

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "email", "createdAt"],
      properties: {
        username: {
          bsonType: "string",
          minLength: 3,
          maxLength: 30,
          description: "Must be a string between 3 and 30 characters"
        },
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        age: {
          bsonType: "int",
          minimum: 0,
          maximum: 150
        },
        role: {
          enum: ["user", "admin", "moderator"],
          description: "Must be one of the allowed roles"
        }
      }
    }
  },
  validationAction: "error",   // reject invalid documents
  validationLevel: "strict"    // validate all inserts and updates
});
```

### 3.6 Aggregation Pipeline

The aggregation pipeline is MongoDB's most powerful feature — chain stages to transform, filter, group, and reshape data.

```javascript
// ─── Basic structure ──────────────────────────────────────────────────────────
db.collection.aggregate([
  { $stage1: { ... } },
  { $stage2: { ... } },
  ...
]);

// ─── Common stages ────────────────────────────────────────────────────────────
$match      // filter documents (like WHERE) — put early to reduce data
$project    // reshape documents (include/exclude/compute fields)
$group      // group by field and aggregate
$sort       // sort documents
$limit      // limit number of documents
$skip       // skip N documents
$unwind     // deconstruct an array field into multiple documents
$lookup     // join with another collection
$addFields  // add new computed fields
$count      // count documents
$facet      // run multiple aggregation pipelines in parallel
$bucket     // categorise documents into buckets by a field value
$out        // write results to a collection
$merge      // merge results into a collection (upsert)

// ─── Real examples ────────────────────────────────────────────────────────────

// Total orders and revenue per user, for users with > 2 orders
db.orders.aggregate([
  { $match: { status: "completed" } },               // filter first (use index)
  { $group: {
    _id: "$userId",
    orderCount: { $sum: 1 },
    totalRevenue: { $sum: "$amount" },
    avgOrderValue: { $avg: "$amount" },
    firstOrder: { $min: "$createdAt" },
    lastOrder: { $max: "$createdAt" }
  }},
  { $match: { orderCount: { $gt: 2 } } },           // filter on aggregated result
  { $sort: { totalRevenue: -1 } },
  { $limit: 10 },
  { $project: {
    userId: "$_id",
    orderCount: 1,
    totalRevenue: { $round: ["$totalRevenue", 2] },
    avgOrderValue: { $round: ["$avgOrderValue", 2] },
    _id: 0
  }}
]);

// Join posts with their authors ($lookup)
db.posts.aggregate([
  { $match: { publishedAt: { $exists: true } } },
  { $lookup: {
    from: "users",            // the collection to join with
    localField: "authorId",   // field in posts
    foreignField: "_id",      // field in users
    as: "author"              // output array field name
  }},
  { $unwind: "$author" },     // deconstruct the author array into a single object
  { $project: {
    title: 1,
    "author.username": 1,
    "author.avatarUrl": 1,
    publishedAt: 1
  }}
]);

// Unwind and regroup — count tag frequency across all posts
db.posts.aggregate([
  { $unwind: "$tags" },        // {tags:["a","b"]} → two docs each with one tag
  { $group: {
    _id: "$tags",
    count: { $sum: 1 }
  }},
  { $sort: { count: -1 } },
  { $limit: 20 }
]);

// Bucket — group users by age range
db.users.aggregate([
  { $bucket: {
    groupBy: "$age",
    boundaries: [0, 18, 25, 35, 50, 100],
    default: "unknown",
    output: {
      count: { $sum: 1 },
      users: { $push: "$username" }
    }
  }}
]);

// Faceted search — multiple aggregations in one pass
db.products.aggregate([
  { $match: { isActive: true } },
  { $facet: {
    byCategory: [
      { $group: { _id: "$category", count: { $sum: 1 } } }
    ],
    byPriceRange: [
      { $bucket: {
        groupBy: "$price",
        boundaries: [0, 10, 50, 100, 500, 10000],
        default: "expensive"
      }}
    ],
    totalCount: [
      { $count: "total" }
    ]
  }}
]);
```

### 3.7 Indexes

```javascript
// Single field index
db.users.createIndex({ email: 1 });          // 1 = ascending, -1 = descending
db.users.createIndex({ createdAt: -1 });     // newest first — for time-ordered queries

// Unique index
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });

// Compound index — order matters
db.orders.createIndex({ userId: 1, createdAt: -1 });
// Supports: { userId: X }, { userId: X, createdAt: Y }
// Does NOT support: { createdAt: Y } alone (no leading field)

// Text index — full-text search
db.posts.createIndex({ title: "text", content: "text" });
db.posts.createIndex(
  { title: "text", content: "text" },
  { weights: { title: 10, content: 1 } }   // title matches score 10x more
);

// Text search query
db.posts.find({ $text: { $search: "mongodb aggregation" } });
db.posts.find(
  { $text: { $search: "mongodb aggregation" } },
  { score: { $meta: "textScore" } }        // include relevance score
).sort({ score: { $meta: "textScore" } }); // sort by relevance

// Sparse index — only index documents that have the field
db.users.createIndex({ deletedAt: 1 }, { sparse: true });

// Partial index — only index documents matching a condition
db.orders.createIndex(
  { createdAt: 1 },
  { partialFilterExpression: { status: "active" } }  // only active orders
);

// TTL index — automatically delete documents after N seconds
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });
db.otpTokens.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
// expireAfterSeconds: 0 + storing the expiry date = expire AT that date

// Wildcard index — index all fields (or all fields under a prefix)
db.products.createIndex({ "attributes.$**": 1 });

// List indexes
db.users.getIndexes();

// Drop index
db.users.dropIndex({ email: 1 });
db.users.dropIndex("email_1");   // by index name
```

### 3.8 Transactions

MongoDB supports multi-document ACID transactions since version 4.0 (replica sets) and 4.2 (sharded clusters).

```javascript
const session = client.startSession();
try {
  await session.withTransaction(async () => {
    // All operations in this block are atomic
    await db.collection('accounts').updateOne(
      { _id: fromAccountId },
      { $inc: { balance: -amount } },
      { session }
    );

    const from = await db.collection('accounts').findOne(
      { _id: fromAccountId },
      { session }
    );
    if (from.balance < 0) {
      throw new Error('Insufficient funds');  // triggers rollback
    }

    await db.collection('accounts').updateOne(
      { _id: toAccountId },
      { $inc: { balance: amount } },
      { session }
    );

    await db.collection('transactions').insertOne({
      from: fromAccountId, to: toAccountId,
      amount, createdAt: new Date()
    }, { session });
  });
} finally {
  await session.endSession();
}
```

### 3.9 Replication — Replica Sets

```
Replica Set: 3+ MongoDB instances (1 primary, 2+ secondaries)

Primary:    accepts all writes, propagates to secondaries
Secondary:  async replication from primary, can serve reads
Arbiter:    no data, only votes in elections (use to get odd number of votes cheaply)

Election:
  Primary goes down → secondaries detect via heartbeat (10s timeout)
  Election: secondaries vote, majority wins, new primary elected
  Typical failover: < 30 seconds
```

```javascript
// Read preference — control where reads go
db.users.find().readPreference("secondaryPreferred");
// Options: primary, primaryPreferred, secondary, secondaryPreferred, nearest

// Write concern — control durability
db.users.insertOne(doc, { writeConcern: { w: "majority", j: true } });
// w: "majority" = wait for majority of members to acknowledge
// j: true = wait for journal write (on-disk durability)
```

### 3.10 Sharding

MongoDB sharding distributes data across multiple replica sets (shards). The **mongos** router directs queries to the right shard.

```javascript
// Shard key choice is critical — same rules as SQL sharding:
// High cardinality, even distribution, queries target one shard

// Good shard keys:
sh.shardCollection("mydb.orders", { userId: 1, _id: 1 });  // hashed for even dist
sh.shardCollection("mydb.events", { userId: "hashed" });   // hashed shard key

// Bad shard keys:
// status (low cardinality)
// createdAt (monotonically increasing → all writes go to one shard)

// Hashed shard key — MongoDB hashes the field value for even distribution
// Range shard key — preserve order, good for range queries on the shard key
```

### 3.11 Node.js with MongoDB (Mongoose)

```typescript
// npm install mongoose

import mongoose, { Schema, Document } from 'mongoose';

// Connect
await mongoose.connect(process.env.MONGODB_URI!);

// Define schema and model
const userSchema = new Schema({
  username: { type: String, required: true, unique: true, minlength: 3 },
  email:    { type: String, required: true, unique: true, lowercase: true },
  role:     { type: String, enum: ['user', 'admin'], default: 'user' },
  tags:     [String],
  address:  {
    city:    String,
    country: String
  },
  createdAt: { type: Date, default: Date.now },
  deletedAt: Date
}, {
  timestamps: true,     // auto-manage createdAt and updatedAt
  toJSON: { virtuals: true }
});

// Virtual field — not stored in DB
userSchema.virtual('fullProfile').get(function() {
  return `${this.username} (${this.email})`;
});

// Middleware (hooks)
userSchema.pre('save', async function(next) {
  if (this.isModified('password')) {
    this.password = await argon2.hash(this.password);
  }
  next();
});

// Static methods
userSchema.statics.findByEmail = function(email: string) {
  return this.findOne({ email: email.toLowerCase() });
};

// Instance methods
userSchema.methods.isAdmin = function() {
  return this.role === 'admin';
};

const User = mongoose.model('User', userSchema);

// CRUD operations
const user = await User.create({ username: 'kingsley', email: 'k@example.com' });
const found = await User.findById(id).select('username email -_id');
const updated = await User.findByIdAndUpdate(id, { $set: { role: 'admin' } }, { new: true });
await User.findByIdAndDelete(id);

// Population — resolve references
const postSchema = new Schema({
  author: { type: Schema.Types.ObjectId, ref: 'User' },
  title: String
});
const post = await Post.findById(id).populate('author', 'username avatarUrl');
// post.author is now the full user document
```

---

## 4. Redis — Key-Value and Data Structures

### 4.1 How Redis Works Internally

Redis is an **in-memory data structure store**. All data lives in RAM. This makes reads and writes microseconds fast — 100,000+ operations per second on a single instance.

**Persistence:** Redis optionally persists to disk using:
- **RDB (Redis Database Backup)** — periodic snapshots. Compact. Fast restart. May lose recent writes.
- **AOF (Append-Only File)** — log every write command. Durable. Larger file. Slower restart.
- **AOF + RDB** — use both. AOF for durability, RDB for fast restart.

**Single-threaded** — Redis processes commands in a single thread. No locking needed. No race conditions. Commands are atomic by definition.

**Eviction:** When memory is full, Redis can evict keys based on configured policy (LRU, LFU, TTL-based, random).

### 4.2 Data Structures

Redis is not just a key-value store — it has multiple data structures, each optimised for specific use cases.

#### Strings

```bash
# SET with options
SET key value
SET key value EX 3600          # expire in 3600 seconds
SET key value PX 60000         # expire in 60000 milliseconds
SET key value NX               # only set if key does NOT exist (distributed lock)
SET key value XX               # only set if key already exists
SET key value GET              # return old value before setting (Redis 6.2+)
SETNX key value                # set if not exists (older syntax — prefer SET NX)

# GET
GET key                        # return value or nil
GETEX key EX 3600              # get and reset TTL
MGET key1 key2 key3            # get multiple keys atomically

# Numeric operations (value must be a number)
INCR counter                   # increment by 1 (atomic)
INCRBY counter 10              # increment by 10
DECR counter
DECRBY counter 5
INCRBYFLOAT price 0.99

# String operations
APPEND key " more text"
STRLEN key
GETRANGE key 0 9               # substring

# TTL management
TTL key                        # remaining TTL in seconds (-1=no TTL, -2=doesn't exist)
PTTL key                       # remaining TTL in milliseconds
EXPIRE key 3600                # set TTL
PERSIST key                    # remove TTL (make permanent)
EXPIREAT key 1705320000        # expire at Unix timestamp

# Real-world string patterns:
SET session:abc123 '{"userId":42,"role":"admin"}' EX 3600
SET rate:user:42:2026-01-15-14 0 EX 60    # rate limit counter
SET idempotency:payment:uuid123 '{"status":"completed"}' EX 86400
SET lock:resource:order_42 "worker-1-uuid" NX EX 30  # distributed lock
```

#### Lists

Ordered collections. Implemented as a doubly-linked list. O(1) push/pop from both ends. O(N) for index access.

```bash
# Push
LPUSH queue job1 job2 job3     # push to left (head) — job3 is now at head
RPUSH queue job1 job2 job3     # push to right (tail)
LPUSHX key value               # only push if key exists

# Pop
LPOP queue                     # pop from left (head)
RPOP queue                     # pop from right (tail)
BLPOP queue 30                 # blocking pop — wait up to 30 seconds for an item
BRPOP queue1 queue2 30         # blocking pop from multiple queues

# Inspect
LLEN queue                     # number of elements
LRANGE queue 0 -1              # all elements (0=first, -1=last)
LRANGE queue 0 9               # first 10 elements
LINDEX queue 0                 # element at index 0
LSET queue 2 "newValue"        # set element at index 2

# Queue pattern (FIFO): RPUSH to add, BLPOP to consume
# Stack pattern (LIFO): LPUSH to add, LPOP to consume

# Trim — keep only a range of elements
LTRIM recentEvents 0 999       # keep only the 1000 most recent events

# Move between lists (atomic)
LMOVE source destination LEFT RIGHT   # pop from left of source, push to right of dest
```

#### Sets

Unordered collections of unique strings. O(1) add, remove, membership check.

```bash
SADD tags "devops" "linux" "aws"
SREM tags "linux"
SMEMBERS tags                  # all members (unordered)
SISMEMBER tags "devops"        # is "devops" in the set? → 1 or 0
SMISMEMBER tags "devops" "java"  # check multiple (Redis 6.2+)
SCARD tags                     # number of members
SRANDMEMBER tags 3             # 3 random members
SPOP tags                      # pop and remove a random member

# Set operations
SUNION set1 set2               # union
SINTER set1 set2               # intersection
SDIFF set1 set2                # difference (in set1 but not set2)
SUNIONSTORE dest set1 set2     # store result in dest
SINTERSTORE dest set1 set2

# Real-world: track unique visitors per day
SADD visitors:2026-01-15 user:42 user:99 user:123
SCARD visitors:2026-01-15        # unique visitor count
EXPIRE visitors:2026-01-15 86400 # expire after 24 hours

# Real-world: mutual followers
SINTER followers:alice followers:bob   # who follows both Alice and Bob?
SINTER following:alice following:bob   # who do both Alice and Bob follow?
```

#### Sorted Sets (ZSets)

Like sets but every member has a score (float). Members are unique, scores are not. Ordered by score. O(log N) for most operations. The most powerful Redis data structure.

```bash
# Add members with scores
ZADD leaderboard 850 "alice"
ZADD leaderboard 920 "bob" 780 "carol" 940 "dave"
ZADD leaderboard NX 1000 "eve"        # only add if not exists
ZADD leaderboard XX 1050 "alice"      # only update if exists
ZADD leaderboard GT 900 "alice"       # only update if new score > current

# Get members
ZRANGE leaderboard 0 -1                           # all, lowest to highest score
ZRANGE leaderboard 0 -1 REV                       # all, highest to lowest (Redis 6.2+)
ZRANGE leaderboard 0 -1 WITHSCORES                # include scores
ZREVRANGE leaderboard 0 9                         # top 10 (highest first, older syntax)
ZRANGEBYSCORE leaderboard 800 1000                # score between 800 and 1000
ZRANGEBYSCORE leaderboard -inf +inf WITHSCORES    # all with scores
ZRANGEBYSCORE leaderboard 500 +inf LIMIT 0 10     # paginate

# Rank and score
ZRANK leaderboard "alice"              # 0-indexed rank (lowest score = 0)
ZREVRANK leaderboard "alice"           # rank from highest (0 = highest)
ZSCORE leaderboard "alice"             # get score

# Count
ZCARD leaderboard                      # total members
ZCOUNT leaderboard 800 1000            # members with score in range

# Remove
ZREM leaderboard "alice"
ZPOPMIN leaderboard 3                  # remove and return 3 lowest-score members
ZPOPMAX leaderboard 1                  # remove and return highest-score member
BZPOPMAX leaderboard 30                # blocking pop

# Increment score
ZINCRBY leaderboard 100 "alice"        # alice score += 100

# Real-world patterns:

# Rate limiting (sliding window)
ZADD ratelimit:user:42 1705320000100 "req-uuid-1"  # score=timestamp in ms
ZREMRANGEBYSCORE ratelimit:user:42 -inf (now-60000) # remove older than 60s
ZCARD ratelimit:user:42                # current request count in window

# Delayed job queue (score = scheduled_at timestamp)
ZADD scheduled_jobs 1705320000 "job:send-email:42"
ZRANGEBYSCORE scheduled_jobs -inf $(date +%s) LIMIT 0 10  # jobs due now

# Trending content (time-decay scoring)
ZINCRBY trending:posts:hourly 1 "post:42"  # increment on each view
# Background job decays scores every hour: ZINCRBY trending:posts:hourly -0.5 "post:42"
```

#### Hashes

A map of field-value pairs stored under one key. Like a mini-document. O(1) field access.

```bash
# Set fields
HSET user:42 username "kingsley" email "k@example.com" role "admin"
HMSET user:42 field1 val1 field2 val2  # older syntax (HSET now accepts multiple)
HSETNX user:42 createdAt "2026-01-15"  # only set if field doesn't exist

# Get fields
HGET user:42 username              # get one field
HMGET user:42 username email       # get multiple fields
HGETALL user:42                    # get all fields and values
HKEYS user:42                      # all field names
HVALS user:42                      # all values
HLEN user:42                       # number of fields
HEXISTS user:42 username           # does field exist?

# Delete
HDEL user:42 temporaryToken

# Numeric operations on hash fields
HINCRBY user:42 loginCount 1       # increment integer field
HINCRBYFLOAT user:42 balance 50.00

# Real-world: user session
HSET session:abc123 userId 42 role admin loginAt 1705320000 lastSeen 1705323600
HGET session:abc123 userId
EXPIRE session:abc123 3600

# Real-world: rate limit with metadata
HSET ratelimit:user:42 count 5 windowStart 1705320000 banned 0
HINCRBY ratelimit:user:42 count 1
```

#### HyperLogLog

Probabilistic data structure for counting unique elements. Uses ~12 KB of memory regardless of the number of unique elements. Error rate ~0.81%.

```bash
PFADD unique_visitors:2026-01-15 user:1 user:2 user:3 user:1  # user:1 counted once
PFCOUNT unique_visitors:2026-01-15       # approximate unique count
PFMERGE total unique_visitors:2026-01-15 unique_visitors:2026-01-16  # merge two

# Use when: you need unique counts at scale and ~1% error is acceptable
# Counting unique IP addresses, unique searches, unique page visitors
```

#### Streams

Append-only log data structure. Like Kafka inside Redis. Each entry has a unique ID.

```bash
# Add to stream
XADD events * action "login" userId "42"     # * = auto-generate ID
XADD events 1705320000000-0 action "login"   # explicit ID (timestamp-sequence)

# Read from stream
XRANGE events - +                             # all entries (- = min, + = max)
XRANGE events 1705320000000 +                # entries after timestamp
XREAD COUNT 10 STREAMS events 0              # read up to 10 from beginning
XREAD COUNT 10 BLOCK 1000 STREAMS events $  # block 1s waiting for new entries

# Consumer groups (multiple consumers, each processes different entries)
XGROUP CREATE events myGroup 0               # create consumer group at beginning
XREADGROUP GROUP myGroup worker1 COUNT 5 STREAMS events >  # read 5 unprocessed
XACK events myGroup entry-id                 # acknowledge processed

XLEN events                                  # number of entries
XTRIM events MAXLEN 10000                    # keep only last 10000 entries
```

### 4.3 Pub/Sub

Redis pub/sub allows messages published to a channel to be delivered to all subscribers. Not persistent — if no one is subscribed when a message is published, it's lost.

```bash
# Publisher
PUBLISH chat:room:42 '{"user":"kingsley","message":"hello"}'

# Subscriber (blocks waiting for messages)
SUBSCRIBE chat:room:42
PSUBSCRIBE chat:room:*     # pattern subscribe — all room channels

# In Node.js:
const subscriber = redis.duplicate();  // must use separate connection for subscribe
await subscriber.subscribe('chat:room:42', (message) => {
  console.log('Received:', JSON.parse(message));
});
await publisher.publish('chat:room:42', JSON.stringify({ user: 'alice', msg: 'hi' }));
```

### 4.4 Lua Scripting

Lua scripts run atomically on the Redis server — no other command executes between your script's operations. This is how you implement compound operations without race conditions.

```bash
# EVAL script numkeys [key...] [arg...]
EVAL "
  local count = redis.call('INCR', KEYS[1])
  if count > tonumber(ARGV[1]) then
    redis.call('DEL', KEYS[1])
    return -1
  end
  redis.call('EXPIRE', KEYS[1], ARGV[2])
  return count
" 1 "rate:user:42" 100 60

# Load script for reuse (saves bandwidth — send SHA not the whole script)
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
EVALSHA abc123sha 1 mykey

# In Node.js with ioredis:
const checkRateLimit = redis.defineCommand('checkRateLimit', {
  numberOfKeys: 1,
  lua: `
    local count = redis.call('INCR', KEYS[1])
    if count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
    if count > tonumber(ARGV[2]) then return 0 end
    return 1
  `
});
const allowed = await redis.checkRateLimit('rate:user:42', 60, 100);
```

### 4.5 Distributed Lock (Redlock)

```javascript
// Simple distributed lock
async function acquireLock(redis, resource, ttlMs) {
  const token = crypto.randomUUID();
  const key = `lock:${resource}`;
  // NX = only set if not exists, PX = expire in milliseconds
  const result = await redis.set(key, token, 'NX', 'PX', ttlMs);
  return result === 'OK' ? token : null;
}

async function releaseLock(redis, resource, token) {
  const key = `lock:${resource}`;
  // Lua script: only delete if we own the lock (token matches)
  const script = `
    if redis.call("GET", KEYS[1]) == ARGV[1] then
      return redis.call("DEL", KEYS[1])
    else
      return 0
    end
  `;
  return redis.eval(script, 1, key, token);
}

// Usage
const token = await acquireLock(redis, 'order:42', 30000);
if (!token) throw new Error('Could not acquire lock — another process holds it');
try {
  await processOrder(42);
} finally {
  await releaseLock(redis, 'order:42', token);
}
```

### 4.6 Persistence Configuration

```bash
# redis.conf

# RDB snapshots — save if N writes happened in M seconds
save 900 1      # save if 1 write in 900 seconds
save 300 10     # save if 10 writes in 300 seconds
save 60 10000   # save if 10000 writes in 60 seconds
dbfilename dump.rdb

# AOF — append-only file (more durable)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec   # fsync every second (good balance of durability and performance)
# appendfsync always   # fsync on every write (safest, slowest)
# appendfsync no       # OS decides when to fsync (fastest, least durable)

# AOF rewrite — compact the AOF when it gets too large
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Both RDB and AOF — recommended for production
# On restart: Redis uses AOF (more complete) if available, else RDB
```

### 4.7 Redis Cluster

Redis Cluster shards data across multiple nodes. Data is partitioned into 16,384 **hash slots**. Each node is responsible for a range of slots. Clients are redirected to the correct node.

```
Node 1: slots 0-5460     (contains keys where CRC16(key) % 16384 in 0-5460)
Node 2: slots 5461-10922
Node 3: slots 10923-16383

Each node has replicas:
Node 1 Primary + Node 1 Replica (different machine)
Node 2 Primary + Node 2 Replica
Node 3 Primary + Node 3 Replica

Minimum cluster: 6 nodes (3 primary + 3 replica)
```

### 4.8 Eviction Policies

```
noeviction        — return error when memory is full (default, bad for cache)
allkeys-lru       — evict least recently used key across all keys
volatile-lru      — evict LRU among keys with TTL set
allkeys-lfu       — evict least frequently used (Redis 4.0+)
volatile-lfu      — evict LFU among keys with TTL
allkeys-random    — evict random key
volatile-random   — evict random key with TTL
volatile-ttl      — evict key with shortest remaining TTL

For a cache: allkeys-lru or allkeys-lfu
For a persistent store: noeviction
```

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 4.9 Node.js with ioredis

```typescript
import Redis from 'ioredis';

// Single instance
const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  db: 0,
  keyPrefix: 'myapp:',        // prefix all keys automatically
  retryStrategy: (times) => Math.min(times * 100, 3000),
  lazyConnect: true,
});

// Cluster
const redis = new Redis.Cluster([
  { host: 'node1.redis.internal', port: 6379 },
  { host: 'node2.redis.internal', port: 6379 },
  { host: 'node3.redis.internal', port: 6379 },
]);

// Pipeline — batch commands (one round trip)
const pipeline = redis.pipeline();
pipeline.set('key1', 'val1');
pipeline.set('key2', 'val2');
pipeline.get('key1');
const results = await pipeline.exec();
// results: [[null, 'OK'], [null, 'OK'], [null, 'val1']]

// Transaction (MULTI/EXEC)
const results = await redis.multi()
  .incr('counter')
  .expire('counter', 60)
  .exec();

// NestJS cache module with Redis
import { CacheModule } from '@nestjs/cache-manager';
import { redisStore } from 'cache-manager-ioredis-yet';

CacheModule.registerAsync({
  useFactory: () => ({
    store: redisStore,
    host: process.env.REDIS_HOST,
    port: 6379,
    ttl: 300,
  }),
})
```

---

## 5. Cassandra — Wide-Column Store

### 5.1 How Cassandra Works Internally

Cassandra is a **distributed wide-column store** designed for write-heavy workloads at extreme scale. It has no single point of failure — all nodes are equal (peer-to-peer). Data is partitioned across nodes using consistent hashing.

**Key properties:**
- Write-optimised — writes are append-only to a commit log and a MemTable (in-memory). Eventually flushed to SSTables on disk.
- Tunable consistency — you choose per-query whether to prioritise consistency or availability
- No joins, no foreign keys, no subqueries — queries must be by partition key
- Linear scalability — adding nodes linearly increases throughput and storage

### 5.2 Data Modelling — Query-First Design

Cassandra's most important design principle: **model your tables around your queries, not your entities.** Unlike relational databases where you normalise first and build queries, in Cassandra you start with the queries and build tables to answer them.

```
Relational approach: model entities → join tables at query time
Cassandra approach:  define queries → create a table per query
```

This often means **denormalisation** — duplicating data across tables so each query has exactly what it needs without a join.

### 5.3 Primary Keys

The primary key is everything in Cassandra. It determines:
- Which node stores the data (partition key)
- How data is sorted on disk (clustering columns)
- What queries you can efficiently run

```sql
CREATE TABLE orders_by_user (
  user_id    UUID,        -- partition key: all orders for one user on one node
  created_at TIMESTAMP,  -- clustering column: sorted by creation time on disk
  order_id   UUID,        -- clustering column: unique within a user+time
  total      DECIMAL,
  status     TEXT,
  PRIMARY KEY ((user_id), created_at, order_id)
  --           ^partition  ^clustering columns^
) WITH CLUSTERING ORDER BY (created_at DESC, order_id ASC);
```

**Partition key** — determines which node(s) store this partition. All rows with the same partition key are stored together on the same node. Choose for even distribution and query locality.

**Clustering columns** — sort rows within a partition. Allow range queries within a partition.

### 5.4 CQL — Cassandra Query Language

```sql
-- Create keyspace (like a database/namespace)
CREATE KEYSPACE myapp
  WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3    -- 3 replicas in us-east datacenter
  };

USE myapp;

-- Create table
CREATE TABLE users_by_email (
  email       TEXT,
  user_id     UUID,
  username    TEXT,
  created_at  TIMESTAMP,
  is_active   BOOLEAN,
  PRIMARY KEY (email)   -- partition key = email (simple primary key)
);

-- Create table for time-series user events
CREATE TABLE user_events (
  user_id    UUID,
  event_time TIMESTAMP,
  event_type TEXT,
  metadata   MAP<TEXT, TEXT>,
  PRIMARY KEY ((user_id), event_time, event_type)
) WITH CLUSTERING ORDER BY (event_time DESC);

-- Insert (always an upsert in Cassandra — no duplicate detection)
INSERT INTO users_by_email (email, user_id, username, created_at, is_active)
VALUES ('k@example.com', uuid(), 'kingsley', toTimestamp(now()), true)
USING TTL 86400;   -- optional TTL on individual rows

-- Select — MUST include partition key in WHERE
SELECT * FROM users_by_email WHERE email = 'k@example.com';  -- OK: partition key
SELECT * FROM user_events WHERE user_id = ? LIMIT 20;         -- OK: partition key
SELECT * FROM user_events                                      -- BAD: full scan (ALLOW FILTERING)
  WHERE user_id = ? AND event_time > '2026-01-01';            -- OK: range on clustering col

-- ALLOW FILTERING — dangerous, do not use in production
SELECT * FROM users_by_email WHERE is_active = true ALLOW FILTERING;  -- full cluster scan

-- Update
UPDATE users_by_email SET username = 'kingsleydaprime' WHERE email = 'k@example.com';

-- Delete
DELETE FROM users_by_email WHERE email = 'k@example.com';
DELETE metadata['key'] FROM user_events WHERE user_id = ? AND event_time = ?;

-- Batch (same partition only — no cross-partition transactions)
BEGIN BATCH
  INSERT INTO users_by_email ...;
  INSERT INTO users_by_username ...;  -- same logical write, different table
APPLY BATCH;

-- TTL on insert (data auto-deleted after N seconds)
INSERT INTO sessions (session_id, user_id, data)
VALUES (?, ?, ?)
USING TTL 3600;   -- session expires in 1 hour

-- Counter tables (atomic increments)
CREATE TABLE post_stats (
  post_id UUID PRIMARY KEY,
  view_count COUNTER,
  like_count COUNTER
);
UPDATE post_stats SET view_count = view_count + 1 WHERE post_id = ?;
```

### 5.5 Data Modelling Patterns

```sql
-- Problem: fetch user by ID or by email (two access patterns)
-- Solution: two tables (one per query pattern)

CREATE TABLE users_by_id (
  user_id  UUID PRIMARY KEY,
  email    TEXT,
  username TEXT
);

CREATE TABLE users_by_email (
  email    TEXT PRIMARY KEY,
  user_id  UUID,
  username TEXT
);
-- Write to BOTH tables on user creation (dual write)

-- Problem: get all orders for a user, sorted by date
CREATE TABLE orders_by_user (
  user_id    UUID,
  created_at TIMESTAMP,
  order_id   UUID,
  total      DECIMAL,
  status     TEXT,
  PRIMARY KEY ((user_id), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Problem: get all active orders across all users (admin view)
-- This requires a separate table — you can't query across partitions efficiently
CREATE TABLE orders_by_status (
  status     TEXT,
  created_at TIMESTAMP,
  order_id   UUID,
  user_id    UUID,
  total      DECIMAL,
  PRIMARY KEY ((status), created_at, order_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

### 5.6 Consistency Levels

Cassandra's consistency level controls how many replicas must agree for a read or write to succeed.

```
RF = Replication Factor (how many copies of each partition)
CL = Consistency Level (how many replicas must respond)

Common consistency levels:
  ONE     — 1 replica must respond (fastest, least consistent)
  QUORUM  — majority (RF/2 + 1) must respond (balanced)
  ALL     — all replicas must respond (slowest, strongest)
  LOCAL_QUORUM — quorum within local datacenter (for multi-DC setups)

Strong consistency: write CL + read CL > RF
  Example: RF=3, write QUORUM (2), read QUORUM (2) → 2+2 > 3 ✓
  Any node that saw the write will be in the read quorum

Eventual consistency: write ONE, read ONE → fast but may read stale data
```

```java
// Java with DataStax driver
Session session = cluster.connect("myapp");

// Per-query consistency
ResultSet rs = session.execute(
    SimpleStatement.builder("SELECT * FROM users_by_email WHERE email = ?")
        .addPositionalValue(email)
        .setConsistencyLevel(ConsistencyLevel.QUORUM)
        .build()
);
```

### 5.7 Node.js with Cassandra

```typescript
import { Client } from 'cassandra-driver';

const client = new Client({
  contactPoints: ['cassandra1.internal', 'cassandra2.internal'],
  localDataCenter: 'us-east',
  keyspace: 'myapp',
  credentials: { username: 'appuser', password: process.env.CASSANDRA_PASSWORD },
});

await client.connect();

// Prepared statement (use for all repeated queries — compiled once, reused)
const getUserStmt = await client.prepare(
  'SELECT user_id, username FROM users_by_email WHERE email = ?'
);
const result = await client.execute(getUserStmt, ['k@example.com'], {
  prepare: true,
  consistency: types.consistencies.localQuorum,
});
const user = result.first();

// Batch insert
const batch = [
  {
    query: 'INSERT INTO users_by_id (user_id, email) VALUES (?, ?)',
    params: [userId, email]
  },
  {
    query: 'INSERT INTO users_by_email (email, user_id) VALUES (?, ?)',
    params: [email, userId]
  }
];
await client.batch(batch, { prepare: true });
```

---

## 6. Neo4j — Graph Database

### 6.1 How Graph Databases Work

A graph database stores data as **nodes** (entities) and **edges** (relationships between entities). Unlike relational databases where relationships are implicit (foreign keys), in a graph database relationships are first-class objects with their own properties.

**Why graphs for connected data:**

```
SQL: "Find all friends of friends of Kingsley who work at a tech company"
  SELECT DISTINCT u3.name FROM users u1
  JOIN follows f1 ON u1.id = f1.follower_id
  JOIN users u2 ON f1.following_id = u2.id
  JOIN follows f2 ON u2.id = f2.follower_id
  JOIN users u3 ON f2.following_id = u3.id
  JOIN user_companies uc ON u3.id = uc.user_id
  JOIN companies c ON uc.company_id = c.id
  WHERE u1.username = 'kingsley' AND c.industry = 'tech'

Neo4j Cypher: 
  MATCH (k:User {name:'Kingsley'})-[:FOLLOWS*2]->(fof:User)-[:WORKS_AT]->(c:Company {industry:'tech'})
  RETURN DISTINCT fof.name
```

The graph query is faster because it traverses relationships rather than scanning tables.

### 6.2 Neo4j Concepts

```
Node:         A circle. Represents an entity. Has labels and properties.
              (User {name: 'Kingsley', age: 22})
              (Company {name: 'Spectroniq', industry: 'tech'})

Relationship: An arrow. Connects two nodes. Has a type and optional properties.
              -[:FOLLOWS]->
              -[:WORKS_AT {since: 2025, role: 'founder'}]->

Label:        A tag on a node, like a type. A node can have multiple labels.
              :User, :Admin, :VIPUser (one node with three labels)

Property:     Key-value pair on a node or relationship.

Path:         A sequence of nodes and relationships. The unit of traversal.
```

### 6.3 Cypher Query Language

```cypher
// ─── CREATE ────────────────────────────────────────────────────────────────

// Create a node
CREATE (k:User {name: 'Kingsley', email: 'k@spectroniq.com', age: 22})
CREATE (s:Company {name: 'Spectroniq', industry: 'tech', country: 'GH'})

// Create a relationship
MATCH (k:User {name: 'Kingsley'}), (s:Company {name: 'Spectroniq'})
CREATE (k)-[:WORKS_AT {role: 'Founder', since: 2024}]->(s)

// Create node and relationship together
CREATE (alice:User {name: 'Alice'})-[:FOLLOWS]->(bob:User {name: 'Bob'})

// MERGE — create only if doesn't already exist (like UPSERT)
MERGE (u:User {email: 'k@spectroniq.com'})
ON CREATE SET u.name = 'Kingsley', u.createdAt = datetime()
ON MATCH  SET u.lastSeen = datetime()

// ─── MATCH (SELECT) ────────────────────────────────────────────────────────

// Find a node
MATCH (u:User {name: 'Kingsley'}) RETURN u

// Find all users
MATCH (u:User) RETURN u.name, u.email ORDER BY u.name

// Find relationships
MATCH (u:User {name: 'Kingsley'})-[r:FOLLOWS]->(following:User)
RETURN following.name, r

// Find incoming relationships
MATCH (follower:User)-[:FOLLOWS]->(u:User {name: 'Kingsley'})
RETURN follower.name

// Variable-length paths (traverse multiple hops)
// Direct follows
MATCH (k:User {name:'Kingsley'})-[:FOLLOWS]->(u:User) RETURN u.name

// Follows of follows (2 hops)
MATCH (k:User {name:'Kingsley'})-[:FOLLOWS*2]->(u:User) RETURN DISTINCT u.name

// 1 to 3 hops
MATCH (k:User {name:'Kingsley'})-[:FOLLOWS*1..3]->(u:User) RETURN DISTINCT u.name

// Shortest path
MATCH path = shortestPath(
  (k:User {name:'Kingsley'})-[*..6]->(target:User {name:'Bob'})
)
RETURN path, length(path)

// All shortest paths
MATCH paths = allShortestPaths(
  (k:User {name:'Kingsley'})-[*]->(target:User {name:'Bob'})
)
RETURN paths

// ─── WHERE AND FILTERING ───────────────────────────────────────────────────

MATCH (u:User)
WHERE u.age >= 18 AND u.country = 'GH'
  AND u.name STARTS WITH 'K'
  AND NOT (u)-[:BLOCKED]->()    -- filter out blocked users
RETURN u.name

MATCH (u:User)
WHERE u.email IN ['k@example.com', 'alice@example.com']
RETURN u

// ─── AGGREGATION ───────────────────────────────────────────────────────────

// Count followers per user
MATCH (follower:User)-[:FOLLOWS]->(u:User)
RETURN u.name, count(follower) AS followerCount
ORDER BY followerCount DESC
LIMIT 10

// Most common companies
MATCH (u:User)-[:WORKS_AT]->(c:Company)
RETURN c.name, count(u) AS employeeCount
ORDER BY employeeCount DESC

// Average age by country
MATCH (u:User)
RETURN u.country, avg(u.age) AS avgAge, count(u) AS userCount

// ─── UPDATE ────────────────────────────────────────────────────────────────

// Set properties
MATCH (u:User {name: 'Kingsley'})
SET u.age = 23, u.updatedAt = datetime()

// Add a label
MATCH (u:User {name: 'Kingsley'})
SET u:Admin

// Remove a label
MATCH (u:User:Admin {name: 'Kingsley'})
REMOVE u:Admin

// Remove a property
MATCH (u:User {name: 'Kingsley'})
REMOVE u.temporaryToken

// ─── DELETE ────────────────────────────────────────────────────────────────

// Delete a relationship
MATCH (a:User)-[r:FOLLOWS]->(b:User {name: 'Kingsley'})
DELETE r

// Delete a node (must delete relationships first)
MATCH (u:User {name: 'Kingsley'})-[r]-()
DELETE r, u

// Delete node and all relationships (DETACH DELETE)
MATCH (u:User {name: 'Kingsley'})
DETACH DELETE u

// ─── ADVANCED PATTERNS ─────────────────────────────────────────────────────

// Mutual follows (friends)
MATCH (a:User {name: 'Kingsley'})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(a)
RETURN b.name AS mutualFriend

// Friends of friends NOT already followed
MATCH (k:User {name: 'Kingsley'})-[:FOLLOWS]->(friend:User)-[:FOLLOWS]->(fof:User)
WHERE NOT (k)-[:FOLLOWS]->(fof) AND fof <> k
RETURN fof.name, count(friend) AS mutualFriendsCount
ORDER BY mutualFriendsCount DESC
LIMIT 10

// Fraud detection: who shares an IP address with known fraudsters?
MATCH (fraud:User {isFraud: true})-[:USED_IP]->(ip:IPAddress)<-[:USED_IP]-(suspect:User)
WHERE suspect.isFraud = false
RETURN suspect.email, collect(ip.address) AS sharedIPs

// Recommendation: products bought by similar users
MATCH (u:User {id: 42})-[:PURCHASED]->(p:Product)<-[:PURCHASED]-(similar:User)
MATCH (similar)-[:PURCHASED]->(rec:Product)
WHERE NOT (u)-[:PURCHASED]->(rec)
RETURN rec.name, count(similar) AS score
ORDER BY score DESC LIMIT 10
```

### 6.4 Indexes in Neo4j

```cypher
// Create index on node property
CREATE INDEX user_email FOR (u:User) ON (u.email)
CREATE INDEX user_name FOR (u:User) ON (u.name)

// Composite index
CREATE INDEX user_country_age FOR (u:User) ON (u.country, u.age)

// Full-text index
CREATE FULLTEXT INDEX post_search FOR (p:Post) ON EACH [p.title, p.content]
CALL db.index.fulltext.queryNodes('post_search', 'machine learning') YIELD node, score
RETURN node.title, score ORDER BY score DESC

// Unique constraint (also creates an index)
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE
CREATE CONSTRAINT user_id_unique FOR (u:User) REQUIRE u.id IS UNIQUE

// List all indexes
SHOW INDEXES
```

### 6.5 Neo4j with Node.js

```typescript
import neo4j from 'neo4j-driver';

const driver = neo4j.driver(
  'neo4j://neo4j.internal:7687',
  neo4j.auth.basic('neo4j', process.env.NEO4J_PASSWORD)
);

// Execute a query
async function getFollowers(username: string) {
  const session = driver.session({ database: 'neo4j' });
  try {
    const result = await session.run(
      `MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
       RETURN follower.username AS username, follower.avatarUrl AS avatarUrl
       ORDER BY follower.username
       LIMIT 100`,
      { username }
    );
    return result.records.map(record => ({
      username: record.get('username'),
      avatarUrl: record.get('avatarUrl'),
    }));
  } finally {
    await session.close();
  }
}

// Write transaction
async function followUser(followerId: string, targetId: string) {
  const session = driver.session();
  try {
    await session.writeTransaction(tx =>
      tx.run(
        `MATCH (a:User {id: $followerId}), (b:User {id: $targetId})
         MERGE (a)-[r:FOLLOWS]->(b)
         ON CREATE SET r.createdAt = datetime()
         RETURN r`,
        { followerId, targetId }
      )
    );
  } finally {
    await session.close();
  }
}
```

---

## 7. Elasticsearch — Search Engine Store

### 7.1 What Elasticsearch Is

Elasticsearch is a distributed search and analytics engine built on Apache Lucene. Stores data as JSON documents. Designed for:
- Full-text search with relevance ranking
- Log aggregation and analysis (ELK stack)
- Faceted search (filter by multiple attributes simultaneously)
- Analytics on large datasets

### 7.2 Core Concepts

```
Index       → collection of documents (like a table, but search-optimised)
Document    → a JSON object (like a row)
Shard       → a Lucene index (a piece of an Elasticsearch index)
Replica     → copy of a shard for redundancy and read scaling

Index settings:
  number_of_shards: 5     (set at creation, cannot change)
  number_of_replicas: 1   (can change at any time)
```

### 7.3 Indexing and Querying

```bash
# Index a document (PUT with specific ID, or POST to auto-generate)
PUT /posts/_doc/1
{
  "title": "Getting Started with DevOps",
  "content": "DevOps is a practice that combines...",
  "author": "Kingsley",
  "tags": ["devops", "linux", "aws"],
  "publishedAt": "2026-01-15T14:30:00Z",
  "viewCount": 1500
}

# Get a document
GET /posts/_doc/1

# Delete a document
DELETE /posts/_doc/1

# Search — full-text (match)
GET /posts/_search
{
  "query": {
    "match": {
      "content": "devops kubernetes docker"
    }
  }
}

# Search — exact match (term — not analyzed)
GET /posts/_search
{
  "query": {
    "term": { "author.keyword": "Kingsley" }
  }
}

# Multi-field search (most relevance wins)
GET /posts/_search
{
  "query": {
    "multi_match": {
      "query": "devops automation",
      "fields": ["title^3", "content", "tags"],  // title weighted 3x
      "type": "best_fields"
    }
  }
}

# Bool query (combine conditions)
GET /posts/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "content": "kubernetes" } }
      ],
      "filter": [
        { "term": { "author.keyword": "Kingsley" } },
        { "range": { "publishedAt": { "gte": "2026-01-01" } } },
        { "terms": { "tags": ["devops", "linux"] } }
      ],
      "must_not": [
        { "term": { "status": "draft" } }
      ],
      "should": [
        { "match": { "title": "kubernetes" } }   // boost score if title matches
      ]
    }
  },
  "sort": [
    { "_score": "desc" },
    { "publishedAt": "desc" }
  ],
  "from": 0,
  "size": 20,
  "_source": ["title", "author", "publishedAt"]  // only return these fields
}

# Aggregations — analytics
GET /posts/_search
{
  "size": 0,    // don't return documents, only aggregations
  "aggs": {
    "tags": {
      "terms": { "field": "tags", "size": 10 }
    },
    "avgViews": {
      "avg": { "field": "viewCount" }
    },
    "postsPerMonth": {
      "date_histogram": {
        "field": "publishedAt",
        "calendar_interval": "month"
      }
    }
  }
}

# Highlight matching terms in results
GET /posts/_search
{
  "query": { "match": { "content": "kubernetes" } },
  "highlight": {
    "fields": {
      "content": { "fragment_size": 150, "number_of_fragments": 3 }
    },
    "pre_tags": ["<em>"],
    "post_tags": ["</em>"]
  }
}
```

### 7.4 Mapping (Schema)

```bash
# Define mapping before indexing (or Elasticsearch will infer it)
PUT /posts
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "custom_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title":       { "type": "text", "analyzer": "custom_analyzer",
                       "fields": { "keyword": { "type": "keyword" } } },
      "content":     { "type": "text", "analyzer": "custom_analyzer" },
      "author":      { "type": "keyword" },
      "tags":        { "type": "keyword" },
      "publishedAt": { "type": "date" },
      "viewCount":   { "type": "integer" },
      "location":    { "type": "geo_point" }  // for geo queries
    }
  }
}
```

### 7.5 Sync Pattern with PostgreSQL

```typescript
// Keep Elasticsearch in sync with PostgreSQL via event-driven updates

// Option 1: Update on write (dual write)
async function createPost(data: CreatePostDto) {
  // Write to PostgreSQL (source of truth)
  const post = await postRepository.save(data);
  
  // Index in Elasticsearch (async, can retry on failure)
  await elasticsearchClient.index({
    index: 'posts',
    id: post.id,
    document: {
      title: post.title,
      content: post.content,
      author: post.author.username,
      tags: post.tags,
      publishedAt: post.publishedAt,
    }
  });
  
  return post;
}

// Option 2: CDC with Debezium (more reliable, decoupled)
// Debezium reads PostgreSQL WAL → publishes to Kafka → consumer indexes in ES
// Lag: < 1 second typically. Guaranteed delivery via Kafka.
```

---

## 8. When to Use What — Decision Framework

### 8.1 Start Here

```
Is your data highly relational with complex queries? → PostgreSQL
Is your schema completely unknown or changes every week? → MongoDB
Do you need sub-millisecond access to cached data? → Redis
Is write throughput > 100K writes/sec? → Cassandra
Is your problem fundamentally about relationships (graphs)? → Neo4j
Do you need full-text search with relevance? → Elasticsearch
```

### 8.2 Decision Tree

```
What is your primary access pattern?

Key lookup (GET user by ID, GET session, GET cached value)
  → Redis (if sub-millisecond in-memory) or DynamoDB (if larger than RAM)

Document fetch (get a user profile with all its nested data)
  → MongoDB (if schema varies) or PostgreSQL JSONB (if mostly relational)

Complex multi-table queries and transactions
  → PostgreSQL or MySQL

Time-series, append-only, massive write volume
  → Cassandra, InfluxDB, or TimescaleDB

Graph traversal (friends of friends, recommendations, fraud detection)
  → Neo4j or Amazon Neptune

Full-text search with relevance ranking
  → Elasticsearch or Typesense or PostgreSQL FTS (smaller scale)

Analytics on historical data
  → BigQuery, Redshift, Snowflake (data warehouse) or
    Spark + S3 (data lake)
```

### 8.3 Scale Decision Points

| Writes/sec | Recommendation |
|---|---|
| < 1,000 | PostgreSQL handles this easily |
| 1,000–10,000 | PostgreSQL with connection pooling and read replicas |
| 10,000–100,000 | Consider Cassandra for the write-heavy tables, PostgreSQL for transactional |
| > 100,000 | Cassandra, DynamoDB, or purpose-built systems |

### 8.4 Consistency Requirements

| Requirement | Technology |
|---|---|
| Strong ACID (money, orders, inventory) | PostgreSQL, MySQL |
| Eventual is fine (likes, view counts, feed) | Cassandra, DynamoDB, MongoDB |
| Cache (can reconstruct from DB) | Redis |
| Search (can re-index from source) | Elasticsearch |
| Relationship traversal | Neo4j |

### 8.5 The "Just Use Postgres" Argument

For most applications, PostgreSQL can do everything:
- JSONB columns handle semi-structured data
- Full-text search handles simple text search
- pg_vector handles ML embeddings
- TimescaleDB extension handles time-series
- Row-level security handles multi-tenancy
- Logical replication handles read scaling

Only reach for a specialised NoSQL database when:
- You have a concrete, measured scaling problem PostgreSQL can't solve
- Your access patterns are genuinely better served by a different model
- Your team can operate the additional database in production

Two databases are twice the operational complexity, failure modes, and cost.

---

## 9. Polyglot Persistence — Using Multiple Databases

### 9.1 What Polyglot Persistence Is

Using different databases for different parts of your application, each chosen for its strengths. Common combinations:

```
PostgreSQL  → source of truth, transactional data, relational queries
Redis       → caching, sessions, rate limiting, pub/sub, queues
Elasticsearch → full-text search, log analytics
MongoDB     → flexible-schema data (user events, product attributes)
Cassandra   → time-series, IoT, activity feeds at scale
Neo4j       → social graph, recommendation engine
```

### 9.2 Real-World Architecture: Social Platform

```
User Service:
  PostgreSQL  → users, follows, settings (transactional, relational)
  Redis       → session tokens, online presence, follow counts
  Elasticsearch → user search by name, bio, location

Content Service:
  PostgreSQL  → posts, metadata, ownership (source of truth)
  Redis       → feed cache, trending posts
  Cassandra   → post activity feeds (high write, time-ordered)

Search Service:
  Elasticsearch → full-text search across posts, users, tags

Graph Service:
  Neo4j       → friend recommendations (friends of friends)
               → mutual connection discovery

Analytics Service:
  Cassandra   → raw event stream (every click, view, interaction)
  BigQuery    → aggregated analytics, reporting
```

### 9.3 Data Synchronisation Patterns

**Dual write** — application writes to multiple databases. Simple but risks inconsistency if one write fails.

```typescript
async function createPost(data: CreatePostDto) {
  const post = await db.posts.create(data);        // PostgreSQL (source of truth)
  await elasticsearch.index('posts', post);        // Elasticsearch (search)
  await redis.del(`feed:${post.userId}`);          // Redis (invalidate cached feed)
  return post;
}
```

**Event-driven sync** — application writes to the primary DB and publishes an event. Consumers update secondary stores asynchronously.

```
Write to PostgreSQL
  → Debezium reads WAL → publishes to Kafka
    → Elasticsearch consumer → indexes document
    → Redis consumer → invalidates cache
    → Analytics consumer → writes to BigQuery
```

More complex but more reliable — each consumer can retry independently.

**Change Data Capture (CDC)** — intercept database change logs directly rather than relying on application-level events. Debezium (for PostgreSQL/MySQL) reads the WAL and publishes every insert/update/delete to Kafka. Downstream consumers handle each change. Zero changes to application code.

### 9.4 The Operational Cost

Every additional database means:
- Another service to monitor, patch, and back up
- Another set of credentials to manage
- Another failure mode (what if Elasticsearch is down?)
- Another skill set your team needs
- Another monthly bill

Start with PostgreSQL. Add Redis when you need caching (almost always worth it). Add Elasticsearch when full-text search becomes a bottleneck. Add Cassandra or Mongo only when you have a proven need at measured scale.

### 9.5 Consistency Across Databases

The fundamental challenge of polyglot persistence: how do you keep two databases consistent when writes can fail at any point?

```
Options:

1. Accept eventual consistency
   Write to primary → async sync to secondary
   Secondary may be briefly stale → acceptable for most use cases

2. Saga pattern
   Coordinate writes across services via compensating transactions
   If Elasticsearch write fails: queue it for retry
   If it fails after N retries: log for manual intervention

3. Outbox pattern
   Write to primary DB + an outbox table in the same transaction
   Relay process reads outbox → publishes events → marks as published
   Guarantees at-least-once delivery to secondary stores
```

```sql
-- Outbox pattern in PostgreSQL
CREATE TABLE outbox (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,             -- 'post.created', 'user.updated'
  payload    JSONB NOT NULL,
  published  BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- In application: single transaction writes data + outbox entry
BEGIN;
  INSERT INTO posts (title, author_id, content) VALUES (...) RETURNING id INTO post_id;
  INSERT INTO outbox (event_type, payload)
    VALUES ('post.created', jsonb_build_object('id', post_id, 'title', title));
COMMIT;

-- Relay process: poll outbox, publish to Kafka, mark published
SELECT * FROM outbox WHERE published = FALSE ORDER BY created_at LIMIT 100;
-- publish each to Kafka...
UPDATE outbox SET published = TRUE WHERE id IN (...);
```

---

*Last updated: 2026 — Built from real NoSQL production experience across document, key-value, wide-column, and graph workloads.*
