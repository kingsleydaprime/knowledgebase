# Design Twitter

**LeetCode 355** · Heap / Priority Queue · concepts: [[08-heaps|heaps]], [[03-hash-maps|hash-maps]]

## Problem

Design Twitter with `postTweet`, `getNewsFeed` (the 10 most recent tweets from the user and everyone they follow), `follow`, and `unfollow`.

## Approach — timestamped tweets + heap merge of followees' feeds

Store each user's tweets as a list of `(timestamp, tweetId)` (a global counter gives ordering), and a follow set per user. `getNewsFeed` is a **k-way merge** of the recent tweets across all followees — a [[08-heaps|heap]] pulling the newest tweet each step, exactly like [[044-merge-k-sorted-lists|Merge K Sorted Lists]].

```python
import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self.time = 0
        self.tweets = defaultdict(list)         # user -> [(time, tweetId), ...]
        self.following = defaultdict(set)

    def postTweet(self, userId, tweetId):
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1

    def follow(self, followerId, followeeId):
        self.following[followerId].add(followeeId)

    def unfollow(self, followerId, followeeId):
        self.following[followerId].discard(followeeId)

    def getNewsFeed(self, userId):
        users = self.following[userId] | {userId}    # self + followees
        heap = []
        for u in users:
            for t, tid in self.tweets[u][-10:]:      # only the last 10 per user matter
                heapq.heappush(heap, (-t, tid))      # max-heap by time
        return [heapq.heappop(heap)[1] for _ in range(min(10, len(heap)))]
```

**`getNewsFeed` O(followees · log …); other ops O(1).**

## Why a heap merge

Each followee's tweets are already newest-last; the feed is the 10 newest across all of them — a merge of sorted streams. A max-heap by timestamp yields them in order without materializing and sorting everything. Only the last 10 tweets per user can ever reach a top-10 feed, bounding the work.

## Key insight

**A "combined recent feed from many sources" is a k-way merge → heap.** This is a system-design-flavored problem whose core is the same heap merge as Merge K Lists; the rest is bookkeeping with hash maps (tweets per user, follow sets).

## Related
- concepts: [[08-heaps|heaps]], [[03-hash-maps|hash-maps]]
- relative: [[044-merge-k-sorted-lists|Merge K Sorted Lists]]
- prev: [[068-task-scheduler|Task Scheduler]] · next: [[070-find-median-from-data-stream|Find Median from Data Stream]]
