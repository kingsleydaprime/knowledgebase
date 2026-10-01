import subprocess
import sys
import unittest


def run(folder, code):
    return subprocess.run([sys.executable, "-c", code], cwd=folder, capture_output=True, text=True)


class CycleTests(unittest.TestCase):
    def test_a_from_import_cycle_fails_at_import_time(self):
        result = run("cycle", "import orders")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImportError: cannot import name 'mark_paid' from", result.stderr)  # wording after this varies by version

    def test_the_event_breaks_the_cycle(self):
        result = run("fixed", "import orders; print(orders.checkout(7))")
        self.assertEqual(result.stdout.strip(), "['order 7 paid']")


if __name__ == "__main__":
    unittest.main()
