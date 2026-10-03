import asyncio
import unittest

from cache import INF, CacheAside, LruCache, average_read_ms, hit_ratio, jittered, seeded, store_reads_per_second, zipf


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class Caching(unittest.IsolatedAsyncioTestCase):
    def test_a_full_lru_cache_evicts_the_entry_used_longest_ago(self):
        cache = LruCache(3, Clock())
        for key in "abc":
            cache.set(key, key.upper(), 1_000)
        cache.get("a")
        cache.set("d", "D", 1_000)
        self.assertEqual(cache.keys(), ["c", "a", "d"])
        self.assertIsNone(cache.get("b"))

    def test_an_entry_expires_after_its_ttl(self):
        clock = Clock()
        cache = LruCache(10, clock)
        cache.set("price:42", 10, 60_000)
        clock.now = 59_999
        self.assertEqual(cache.get("price:42"), 10)
        clock.now = 60_000
        self.assertIsNone(cache.get("price:42"))

    async def test_cache_aside_first_read_misses_the_rest_hit(self):
        loads = 0

        async def load(key):
            nonlocal loads
            loads += 1
            return "kettle"

        products = CacheAside(LruCache(100, Clock()), load, ttl_ms=60_000)
        for _ in range(5):
            self.assertEqual(await products.get("product:7"), "kettle")
        self.assertEqual((loads, products.hits, products.misses), (1, 4, 1))
        self.assertEqual(hit_ratio(products.hits, products.misses), 0.8)

    def test_the_hit_ratio_decides_what_the_database_sees(self):
        self.assertEqual([round(store_reads_per_second(5_000, h)) for h in [0.8, 0.9, 0.99]], [1_000, 500, 50])
        self.assertEqual([f"{average_read_ms(h, 1, 20):.1f}" for h in [0, 0.8, 0.99]], ["21.0", "5.0", "1.2"])
        self.assertEqual(store_reads_per_second(5_000, 0), 5_000)

    def test_skewed_traffic_a_small_cache_answers_most_reads(self):
        ratios = []
        for size in [500, 2_500, 5_000, 10_000]:
            next_key = zipf(50_000, 1, seeded(1))
            cache, hits, misses = LruCache(size, Clock()), 0, 0
            for i in range(200_000):
                key = str(next_key())
                hit = cache.get(key) is not None
                if not hit:
                    cache.set(key, True, INF)
                if i >= 50_000:
                    hits, misses = hits + hit, misses + (not hit)
            ratios.append(f"{hit_ratio(hits, misses):.2f}")
        self.assertEqual(ratios, ["0.48", "0.65", "0.72", "0.80"])

    async def test_a_stampede_unless_misses_share_one_load(self):
        for coalesce in [False, True]:
            clock, loads = Clock(), 0

            async def load(key):
                nonlocal loads
                loads += 1
                await asyncio.sleep(0.005)
                return "kettle"

            products = CacheAside(LruCache(100, clock), load, ttl_ms=60_000, coalesce=coalesce)
            await products.get("product:7")
            clock.now, loads = 60_000, 0
            names = await asyncio.gather(*(products.get("product:7") for _ in range(100)))
            self.assertTrue(all(n == "kettle" for n in names))
            self.assertEqual(loads, 1 if coalesce else 100)

    async def test_delete_on_write_can_still_leave_a_stale_value(self):
        clock, db = Clock(), {"price:42": 10}
        slow_read, first = asyncio.Event(), [True]

        async def load(key):
            value = db[key]  # the read happens now...
            if first[0]:
                first[0] = False
                await slow_read.wait()  # ...but the answer is delayed
            return value

        async def save(key, value):
            db[key] = value

        prices = CacheAside(LruCache(100, clock), load, ttl_ms=60_000)
        reader = asyncio.ensure_future(prices.get("price:42"))
        await asyncio.sleep(0)  # let the reader start and read 10
        await prices.write("price:42", 12, save)
        slow_read.set()
        self.assertEqual(await reader, 10)
        self.assertEqual(await prices.get("price:42"), 10)  # stale
        clock.now = 60_000
        self.assertEqual(await prices.get("price:42"), 12)

    def test_jitter_spreads_out_expiry(self):
        random = seeded(3)
        expiries = [jittered(60_000, 0.1, random) for _ in range(1_000)]
        self.assertTrue(min(expiries) >= 54_000 and max(expiries) <= 66_000)
        per_second: dict[int, int] = {}
        for ms in expiries:
            per_second[int(ms // 1_000)] = per_second.get(int(ms // 1_000), 0) + 1
        self.assertLess(max(per_second.values()), 120)


if __name__ == "__main__":
    unittest.main()
