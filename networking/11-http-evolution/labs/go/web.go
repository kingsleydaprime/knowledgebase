// Package web: the same small site as the TypeScript lab, served by net/http over HTTP/1.1 and HTTP/2. Since Go
// 1.24, net/http speaks HTTP/2 without TLS ("h2c") when asked, on both the server and the client.
package web

import (
	"crypto/sha256"
	"fmt"
	"net"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"time"
)

var (
	asset = []byte("body { color: rebeccapurple; }\n")
	etag  = fmt.Sprintf(`"%x"`, sha256.Sum256(asset))[:17] + `"`
)

func site(w http.ResponseWriter, r *http.Request) {
	switch r.URL.Path {
	case "/fast":
		fmt.Fprint(w, "fast")
	case "/slow":
		time.Sleep(200 * time.Millisecond)
		fmt.Fprint(w, "slow")
	case "/style.css":
		w.Header().Set("ETag", etag)
		if r.Header.Get("If-None-Match") == etag {
			w.WriteHeader(http.StatusNotModified) // headers only
			return
		}
		w.Header().Set("Cache-Control", "max-age=60")
		w.Write(asset)
	case "/stream":
		fmt.Fprint(w, "hello")
		w.(http.Flusher).Flush() // send what we have: without a Content-Length, HTTP/1.1 goes chunked
		time.Sleep(20 * time.Millisecond)
		fmt.Fprint(w, " world")
	default:
		http.NotFound(w, r)
	}
}

// Server starts the site on 127.0.0.1, speaking HTTP/1.1 and h2c, and counts TCP connections.
func Server() (*httptest.Server, *atomic.Int64) {
	var connections atomic.Int64
	server := httptest.NewUnstartedServer(http.HandlerFunc(site))
	server.Config.Protocols = new(http.Protocols)
	server.Config.Protocols.SetHTTP1(true)
	server.Config.Protocols.SetUnencryptedHTTP2(true)
	server.Config.ConnState = func(_ net.Conn, state http.ConnState) {
		if state == http.StateNew {
			connections.Add(1)
		}
	}
	server.Start()
	return server, &connections
}

// Client returns an HTTP client limited to one connection, speaking HTTP/1.1 (with or without keep-alive) or h2c.
func Client(http2, keepAlive bool) *http.Client {
	transport := &http.Transport{MaxConnsPerHost: 1, DisableKeepAlives: !keepAlive, Protocols: new(http.Protocols)}
	if http2 {
		transport.Protocols.SetUnencryptedHTTP2(true) // speak HTTP/2 straight away, with no TLS and no upgrade
	} else {
		transport.Protocols.SetHTTP1(true)
	}
	return &http.Client{Transport: transport}
}
