package web

import (
	"bufio"
	"io"
	"net"
	"net/http"
	"slices"
	"strings"
	"sync"
	"testing"
	"time"
)

func get(t *testing.T, c *http.Client, url string, header map[string]string) (*http.Response, string) {
	t.Helper()
	req, _ := http.NewRequest("GET", url, nil)
	for k, v := range header {
		req.Header.Set(k, v)
	}
	res, err := c.Do(req)
	if err != nil {
		t.Fatal(err)
	}
	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)
	return res, string(body)
}

func TestKeepAliveTenRequestsOneConnection(t *testing.T) {
	for _, c := range []struct {
		keepAlive bool
		want      int64
	}{{false, 10}, {true, 1}} {
		server, connections := Server()
		client := Client(false, c.keepAlive)
		for range 10 {
			get(t, client, server.URL+"/fast", nil)
		}
		server.Close()
		if connections.Load() != c.want {
			t.Fatalf("keepAlive=%v: %d connections", c.keepAlive, connections.Load())
		}
	}
}

// finishOrder sends /slow, then /fast 20 ms later, and records the order the replies finish in.
func finishOrder(t *testing.T, client *http.Client, base string) []string {
	var mu sync.Mutex
	var order []string
	var wg sync.WaitGroup
	for i, path := range []string{"/slow", "/fast"} {
		wg.Go(func() {
			time.Sleep(time.Duration(i) * 20 * time.Millisecond) // the slow request is always sent first
			_, body := get(t, client, base+path, nil)
			mu.Lock()
			order = append(order, body)
			mu.Unlock()
		})
	}
	wg.Wait()
	return order
}

func TestHeadOfLineBlockingAndMultiplexing(t *testing.T) {
	server, connections := Server()
	defer server.Close()
	// HTTP/1.1 with one connection: the fast request waits until the slow one's response has finished.
	if order := finishOrder(t, Client(false, true), server.URL); !slices.Equal(order, []string{"slow", "fast"}) {
		t.Fatal("HTTP/1.1:", order)
	}
	before := connections.Load()
	// HTTP/2: two streams on one connection, so the fast reply overtakes.
	if order := finishOrder(t, Client(true, true), server.URL); !slices.Equal(order, []string{"fast", "slow"}) {
		t.Fatal("HTTP/2:", order)
	}
	if connections.Load()-before != 1 {
		t.Fatal("HTTP/2 used more than one connection")
	}
}

func TestAnETagTurnsASecondDownloadIntoA304(t *testing.T) {
	server, _ := Server()
	defer server.Close()
	client := Client(false, true)
	first, _ := get(t, client, server.URL+"/style.css", nil)
	again, body := get(t, client, server.URL+"/style.css", map[string]string{"If-None-Match": first.Header.Get("ETag")})
	if first.StatusCode != 200 || first.Header.Get("Cache-Control") != "max-age=60" || again.StatusCode != 304 || body != "" {
		t.Fatal(first.StatusCode, again.StatusCode, body)
	}
}

func TestChunkedEncodingOnTheWire(t *testing.T) {
	server, _ := Server()
	defer server.Close()
	conn, err := net.Dial("tcp", strings.TrimPrefix(server.URL, "http://"))
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()
	io.WriteString(conn, "GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n")
	raw, _ := io.ReadAll(bufio.NewReader(conn))
	head, body, _ := strings.Cut(string(raw), "\r\n\r\n")
	if !strings.Contains(head, "Transfer-Encoding: chunked") || body != "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n" {
		t.Fatalf("%q", raw)
	}
}
