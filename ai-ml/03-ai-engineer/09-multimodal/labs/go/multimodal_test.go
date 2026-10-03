package multimodal

import (
	"context"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"strings"
	"testing"
)

// Just enough of each format's header to identify it and read its size. (The TypeScript lab builds a whole PNG.)
func pngHeader(w, h uint32) []byte {
	b := append([]byte("\x89PNG\r\n\x1a\n"), 0, 0, 0, 13)
	b = append(b, "IHDR"...)
	b = binary.BigEndian.AppendUint32(b, w)
	b = binary.BigEndian.AppendUint32(b, h)
	return append(b, 8, 0, 0, 0, 0)
}

func jpegHeader(w, h uint16) []byte {
	b := []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 'J', 'F', 'I', 'F', 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0xff, 0xc0, 0x00, 0x11, 0x08}
	b = binary.BigEndian.AppendUint16(b, h)
	b = binary.BigEndian.AppendUint16(b, w)
	return append(b, 3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1)
}

func TestTheTypeComesFromTheBytes(t *testing.T) {
	if info, _ := Sniff(pngHeader(1200, 800)); info != (Info{"image/png", 1200, 800}) {
		t.Error(info)
	}
	if info, _ := Sniff(jpegHeader(4000, 3000)); info != (Info{"image/jpeg", 4000, 3000}) {
		t.Error(info)
	}
	if info, _ := Sniff([]byte("GIF89a\x40\x01\xf0\x00")); info != (Info{"image/gif", 320, 240}) {
		t.Error(info)
	}
	for _, bad := range []string{"#!/bin/sh\nrm -rf /\n", "<svg onload=alert(1)>"} {
		if _, ok := Sniff([]byte(bad)); ok {
			t.Errorf("accepted %q", bad)
		}
	}
	if got := StdlibType(pngHeader(1, 1)); got != "image/png" {
		t.Error(got) // the standard library agrees on the type, but doesn't give the size
	}
}

func TestWhatAPhotoCosts(t *testing.T) {
	cases := map[Fitted]Fitted{
		Fit(4000, 3000, HighRes):  {2187, 1640, 4783},
		Fit(4000, 3000, Standard): {1264, 948, 1598},
		Fit(1920, 1080, HighRes):  {1920, 1080, 2765},
	}
	for got, want := range cases {
		if got != want {
			t.Errorf("got %v, want %v", got, want)
		}
	}
	if w, h := ShrinkTo(4000, 3000, 1024); Fit(w, h, HighRes) != (Fitted{1024, 768, 1049}) {
		t.Error(w, h)
	}
}

func TestThreeFormats(t *testing.T) {
	png := pngHeader(4, 4)
	data := base64.StdEncoding.EncodeToString(png)
	anthropic, _ := ImageMessage(png, "What is this?", "anthropic")
	openai, _ := ImageMessage(png, "What is this?", "openai")
	ollama, _ := ImageMessage(png, "What is this?", "ollama")
	a, _ := json.Marshal(anthropic["content"].([]any)[0])
	o, _ := json.Marshal(openai["content"].([]any)[1])
	l, _ := json.Marshal(ollama)
	if string(a) != `{"source":{"data":"`+data+`","media_type":"image/png","type":"base64"},"type":"image"}` { // json.Marshal sorts map keys
		t.Error(string(a))
	}
	if string(o) != `{"image_url":{"url":"data:image/png;base64,`+data+`"},"type":"image_url"}` {
		t.Error(string(o))
	}
	if string(l) != `{"content":"What is this?","images":["`+data+`"],"role":"user"}` {
		t.Error(string(l))
	}
	if _, err := ImageMessage([]byte("not an image"), "?", "openai"); err == nil {
		t.Error("should refuse")
	}
}

func TestCheckedExtraction(t *testing.T) {
	good := `{"vendor":"Paper Co","invoice_number":"INV-7","currency":"GBP","due_date":"2026-10-15",` +
		`"line_items":[{"description":"A4 paper","amount_cents":1250},{"description":"Pens","amount_cents":480}],"total_cents":1730}`
	reply := func(text string) See {
		return func(context.Context, []byte, string) (string, error) { return "Here you go: " + text, nil }
	}
	png, ctx := pngHeader(8, 8), context.Background()
	if inv, err := ExtractInvoice(ctx, reply(good), png); err != nil || inv.TotalCents != 1730 {
		t.Fatal(inv, err)
	}
	misread := strings.Replace(good, `"total_cents":1730`, `"total_cents":1780`, 1)
	for text, want := range map[string]string{
		misread:                      "line items add up to 1730 cents but total_cents is 1780",
		`{"unreadable": "due_date"}`: "unreadable: due_date",
		"I can't see an invoice.":    "no JSON in the reply",
	} {
		if _, err := ExtractInvoice(ctx, reply(text), png); err == nil || err.Error() != want {
			t.Errorf("got %v, want %q", err, want)
		}
	}
	if _, err := ExtractInvoice(ctx, reply(good), []byte("%PDF-1.7")); err == nil || err.Error() != "not a supported image" {
		t.Error(err)
	}
}
