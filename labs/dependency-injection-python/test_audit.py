import asyncio
import unittest

from audit import compose, current_user


class ScopeBugTests(unittest.IsolatedAsyncioTestCase):
    async def test_bug_a_per_request_field_records_the_wrong_user(self):
        log, buggy, _, _ = compose()

        async def handle(user):
            buggy.current_user = user
            await buggy.record("viewed invoice")

        await asyncio.gather(handle("ada"), handle("bayo"))
        self.assertEqual(log.entries, ["bayo: viewed invoice", "bayo: viewed invoice"])

    async def test_fix_1_pass_it_as_an_argument(self):
        log, _, audit, _ = compose()
        await asyncio.gather(audit.record("ada", "viewed invoice"), audit.record("bayo", "viewed invoice"))
        self.assertEqual(sorted(log.entries), ["ada: viewed invoice", "bayo: viewed invoice"])

    async def test_fix_2_a_context_variable_per_task(self):
        log, _, _, context_audit = compose()

        async def handle(user):
            current_user.set(user)  # gather runs each coroutine in its own task, with its own context
            await context_audit.record("viewed invoice")

        await asyncio.gather(handle("ada"), handle("bayo"))
        self.assertEqual(sorted(log.entries), ["ada: viewed invoice", "bayo: viewed invoice"])


if __name__ == "__main__":
    unittest.main()
