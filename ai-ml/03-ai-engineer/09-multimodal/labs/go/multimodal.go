// Package multimodal: what an uploaded file really is, what an image costs, the three providers' formats,
// and checked extraction. The same results as the TypeScript lab; reuses the structured-output lab's Parse.
package multimodal

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"errors"
	"math"
	"net/http"
	"strings"

	"invoice"
)

type Info struct {
	Type          string
	Width, Height int
}

// Sniff decides the type from the file's first bytes, never its name or Content-Type.
func Sniff(b []byte) (Info, bool) {
	switch {
	case bytes.HasPrefix(b, []byte("\x89PNG\r\n\x1a\n")) && len(b) >= 24:
		return Info{"image/png", int(binary.BigEndian.Uint32(b[16:])), int(binary.BigEndian.Uint32(b[20:]))}, true
	case bytes.HasPrefix(b, []byte{0xff, 0xd8, 0xff}):
		w, h := jpegSize(b)
		return Info{"image/jpeg", w, h}, true
	case bytes.HasPrefix(b, []byte("GIF8")) && len(b) >= 10:
		return Info{"image/gif", int(binary.LittleEndian.Uint16(b[6:])), int(binary.LittleEndian.Uint16(b[8:]))}, true
	case len(b) >= 12 && string(b[:4]) == "RIFF" && string(b[8:12]) == "WEBP":
		return Info{Type: "image/webp"}, true
	}
	return Info{}, false
}

func jpegSize(b []byte) (width, height int) {
	for i := 2; i+9 < len(b); {
		if b[i] != 0xff {
			return 0, 0
		}
		marker, length := b[i+1], int(binary.BigEndian.Uint16(b[i+2:]))
		if marker >= 0xc0 && marker <= 0xcf && marker != 0xc4 && marker != 0xc8 && marker != 0xcc { // start of frame
			return int(binary.BigEndian.Uint16(b[i+7:])), int(binary.BigEndian.Uint16(b[i+5:]))
		}
		i += 2 + length
	}
	return 0, 0
}

// The standard library's own sniffer reads magic bytes too, but returns only a type, and recognises
// more formats than you may want to accept.
func StdlibType(b []byte) string { return http.DetectContentType(b) }

type Limits struct{ MaxLongEdge, MaxTokens float64 }

var (
	HighRes  = Limits{2576, 4784} // Anthropic, 2026-10: Opus 4.7+ and Sonnet 5+
	Standard = Limits{1568, 1600} // earlier models
)

type Fitted struct{ Width, Height, Tokens int }

// Fit scales to the model's limits; tokens ≈ width × height / 750 (Anthropic's documented approximation).
func Fit(width, height float64, l Limits) Fitted {
	scale := math.Min(1, l.MaxLongEdge/math.Max(width, height))
	if t := width * scale * (height * scale) / 750; t > l.MaxTokens {
		scale *= math.Sqrt(l.MaxTokens / t)
	}
	w, h := math.Floor(width*scale), math.Floor(height*scale)
	return Fitted{int(w), int(h), int(math.Ceil(w * h / 750))}
}

func ShrinkTo(width, height, longEdge float64) (float64, float64) {
	s := math.Min(1, longEdge/math.Max(width, height))
	return math.Round(width * s), math.Round(height * s)
}

// ImageMessage builds the user message in each provider's shape, as a map ready for json.Marshal.
func ImageMessage(b []byte, question, provider string) (map[string]any, error) {
	info, ok := Sniff(b)
	if !ok {
		return nil, errors.New("not a supported image")
	}
	data := base64.StdEncoding.EncodeToString(b)
	switch provider {
	case "anthropic":
		return map[string]any{"role": "user", "content": []any{
			map[string]any{"type": "image", "source": map[string]any{"type": "base64", "media_type": info.Type, "data": data}},
			map[string]any{"type": "text", "text": question},
		}}, nil
	case "openai":
		return map[string]any{"role": "user", "content": []any{
			map[string]any{"type": "text", "text": question},
			map[string]any{"type": "image_url", "image_url": map[string]any{"url": "data:" + info.Type + ";base64," + data}},
		}}, nil
	}
	return map[string]any{"role": "user", "content": question, "images": []string{data}}, nil // Ollama's own /api/chat
}

const ExtractPrompt = `Read this invoice and reply with JSON only, in the invoice schema.
If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.`

type See func(ctx context.Context, image []byte, prompt string) (string, error)

// ExtractInvoice: image in, checked data out. The structured-output lab's Parse checks shape and arithmetic.
func ExtractInvoice(ctx context.Context, see See, b []byte) (invoice.Invoice, error) {
	if _, ok := Sniff(b); !ok {
		return invoice.Invoice{}, errors.New("not a supported image")
	}
	reply, err := see(ctx, b, ExtractPrompt)
	if err != nil {
		return invoice.Invoice{}, err
	}
	var probe struct { // "I can't read this" is an answer, not an error
		Unreadable string `json:"unreadable"`
	}
	if start, end := strings.Index(reply, "{"), strings.LastIndex(reply, "}"); start >= 0 && end > start &&
		json.Unmarshal([]byte(reply[start:end+1]), &probe) == nil && probe.Unreadable != "" {
		return invoice.Invoice{}, errors.New("unreadable: " + probe.Unreadable)
	}
	inv, err := invoice.Parse(reply)
	if err != nil && err.Error() == "no JSON object in the reply" {
		return inv, errors.New("no JSON in the reply")
	}
	return inv, err
}
