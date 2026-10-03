import base64
import json
import struct
import unittest

from multimodal import HIGH_RES, STANDARD, extract_invoice, fit, image_message, shrink_to, sniff

# Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
PNG = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 1200, 800) + bytes(5)
JPEG = (b"\xff\xd8" + b"\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", 3000, 4000) + b"\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01")
GOOD = {"vendor": "Paper Co", "invoice_number": "INV-7", "currency": "GBP", "due_date": "2026-10-15",
        "line_items": [{"description": "A4 paper", "amount_cents": 1250}, {"description": "Pens", "amount_cents": 480}], "total_cents": 1730}


def reply(value):
    async def see(data, prompt):
        return value if isinstance(value, str) else f"Here you go: {json.dumps(value)}"
    return see


class Multimodal(unittest.IsolatedAsyncioTestCase):
    def test_the_type_comes_from_the_bytes(self):
        self.assertEqual(sniff(PNG), {"type": "image/png", "width": 1200, "height": 800})
        self.assertEqual(sniff(JPEG), {"type": "image/jpeg", "width": 4000, "height": 3000})
        self.assertEqual(sniff(b"GIF89a\x40\x01\xf0\x00"), {"type": "image/gif", "width": 320, "height": 240})
        self.assertIsNone(sniff(b"#!/bin/sh\nrm -rf /\n"))
        self.assertIsNone(sniff(b"<svg onload=alert(1)>"))

    def test_what_a_photo_costs(self):
        self.assertEqual(fit(4000, 3000, HIGH_RES), {"width": 2187, "height": 1640, "tokens": 4783})
        self.assertEqual(fit(4000, 3000, STANDARD), {"width": 1264, "height": 948, "tokens": 1598})
        self.assertEqual(fit(*shrink_to(4000, 3000, 1024), HIGH_RES), {"width": 1024, "height": 768, "tokens": 1049})
        self.assertEqual(fit(1920, 1080, HIGH_RES), {"width": 1920, "height": 1080, "tokens": 2765})

    def test_three_formats(self):
        b64 = base64.b64encode(PNG).decode()
        self.assertEqual(image_message(PNG, "What is this?", "anthropic")["content"][0],
                         {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}})
        self.assertEqual(image_message(PNG, "What is this?", "openai")["content"][1]["image_url"]["url"], f"data:image/png;base64,{b64}")
        self.assertEqual(image_message(PNG, "What is this?", "ollama"), {"role": "user", "content": "What is this?", "images": [b64]})
        with self.assertRaisesRegex(ValueError, "not a supported image"):
            image_message(b"not an image", "?", "openai")

    async def test_checked_extraction(self):
        ok = await extract_invoice(reply(GOOD), PNG)
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["invoice"].total_cents, 1730)
        misread = await extract_invoice(reply({**GOOD, "total_cents": 1780}), PNG)
        self.assertFalse(misread["ok"])
        self.assertIn("line items add up to 1730 cents but total_cents is 1780", misread["reason"])  # Pydantic adds "Value error, "
        self.assertEqual(await extract_invoice(reply({"unreadable": "due_date"}), PNG), {"ok": False, "reason": "unreadable: due_date"})
        self.assertEqual(await extract_invoice(reply("I can't see an invoice."), PNG), {"ok": False, "reason": "no JSON in the reply"})
        self.assertEqual(await extract_invoice(reply(GOOD), b"%PDF-1.7"), {"ok": False, "reason": "not a supported image"})


if __name__ == "__main__":
    unittest.main()
