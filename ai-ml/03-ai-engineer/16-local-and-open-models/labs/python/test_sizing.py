"""Every number here was measured on the laptop the study partner runs on (2026-10-02):
16 GB RAM with about 7 GB free, an i7-8650U, and a 2 GB MX130."""
import unittest

from sizing import (fits, fits_context, generation_seconds, prompt_budget, weights_gb,
                    words_to_tokens)


class SizingTests(unittest.TestCase):
    def test_weights_follow_parameters_times_bits(self):
        self.assertEqual(weights_gb(9.7, "Q4_K_M"), 5.8)   # qwen3.5:latest (9.7B) downloads at 6.6 GB:
        self.assertEqual(weights_gb(4.0, "Q4_K_M"), 2.4)   # the gap is the vision encoder and metadata
        self.assertEqual(weights_gb(4.0, "Q8_0"), 4.2)     # same model, 8-bit: almost twice the memory

    def test_what_fits_in_7_gb_free(self):
        self.assertFalse(fits(9.6, free_ram_gb=7))         # gemma4 8B with its encoders: swaps
        self.assertFalse(fits(6.6, free_ram_gb=7))         # qwen3.5 9.7B: no headroom left
        self.assertTrue(fits(3.4, free_ram_gb=7))          # qwen3.5:4b

    def test_thinking_is_why_two_sentences_took_four_minutes(self):
        self.assertEqual(generation_seconds(1087, 4.59), 236.8)  # measured: 3 min 56.9 s, thinking on
        self.assertEqual(generation_seconds(83, 4.68), 17.7)     # measured: 17.7 s, thinking off

    def test_openclaw_on_a_16k_window_overflows_before_you_type(self):
        overhead = 8786   # OpenClaw's prompt with no messages, from its own log
        reserve = 8384    # what it keeps back for the reply
        self.assertEqual(prompt_budget(16384, reserve), 8000)
        self.assertFalse(fits_context(overhead, 0, 0, 16384, reserve))   # "hi" failed
        lesson = words_to_tokens(5000)                                   # a long lesson, ~6,500 tokens
        self.assertTrue(fits_context(overhead, lesson, 2000, 32768, reserve))


if __name__ == "__main__":
    unittest.main()
