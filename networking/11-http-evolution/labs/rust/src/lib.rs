//! A minimal HTTP/1.1 server written by hand over std's TcpListener: Rust's standard library has no HTTP at all
//! (hyper and axum are the usual crates, and they add HTTP/2). Writing it shows what a framework does for you:
//! read a request line and headers, decide where the body ends, and keep the connection for the next request.
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;

const ASSET: &str = "body { color: rebeccapurple; }\n";
const ETAG: &str = "\"v1-rebeccapurple\""; // any fingerprint of the content works

/// Starts the site on 127.0.0.1 and returns its port and a count of accepted TCP connections.
pub fn start() -> (u16, Arc<AtomicUsize>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let port = listener.local_addr().expect("address").port();
    let connections = Arc::new(AtomicUsize::new(0));
    let counter = connections.clone();
    std::thread::spawn(move || {
        for stream in listener.incoming().flatten() {
            counter.fetch_add(1, Ordering::SeqCst);
            std::thread::spawn(move || serve_connection(stream));
        }
    });
    (port, connections)
}

/// Answers requests on one connection until the client closes it or asks to (keep-alive is HTTP/1.1's default).
fn serve_connection(stream: TcpStream) {
    let mut reader = BufReader::new(stream.try_clone().expect("clone"));
    let mut out = stream;
    loop {
        let mut request_line = String::new();
        if reader.read_line(&mut request_line).unwrap_or(0) == 0 {
            return; // the client closed the connection
        }
        let path = request_line
            .split_whitespace()
            .nth(1)
            .unwrap_or("/")
            .to_string();
        let (mut if_none_match, mut close) = (None, false);
        loop {
            let mut header = String::new();
            reader.read_line(&mut header).expect("a header line");
            let header = header.trim_end();
            if header.is_empty() {
                break; // a blank line ends the headers; these GETs have no body
            }
            let (name, value) = header.split_once(':').unwrap_or((header, ""));
            match name.to_ascii_lowercase().as_str() {
                "if-none-match" => if_none_match = Some(value.trim().to_string()),
                "connection" => close = value.trim().eq_ignore_ascii_case("close"),
                _ => {}
            }
        }
        let response = match path.as_str() {
            "/fast" => text("200 OK", "fast"),
            "/slow" => {
                std::thread::sleep(Duration::from_millis(200));
                text("200 OK", "slow")
            }
            "/style.css" if if_none_match.as_deref() == Some(ETAG) => {
                format!("HTTP/1.1 304 Not Modified\r\nETag: {ETAG}\r\n\r\n")
            }
            "/style.css" => format!(
                "HTTP/1.1 200 OK\r\nETag: {ETAG}\r\nCache-Control: max-age=60\r\nContent-Length: {}\r\n\r\n{ASSET}",
                ASSET.len()
            ),
            "/stream" => {
                // No Content-Length: frame the body as chunks, each its length in hex, ended by a zero-length chunk.
                let chunks = ["hello", " world"]
                    .iter()
                    .map(|c| format!("{:x}\r\n{c}\r\n", c.len()))
                    .collect::<String>();
                format!("HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n{chunks}0\r\n\r\n")
            }
            _ => text("404 Not Found", ""),
        };
        if out.write_all(response.as_bytes()).is_err() || close {
            return;
        }
    }
}

fn text(status: &str, body: &str) -> String {
    format!(
        "HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {}\r\n\r\n{body}",
        body.len()
    )
}

/// Sends one GET on an open connection and reads exactly one response, using its Content-Length.
pub fn get(stream: &mut TcpStream, path: &str, extra_header: &str) -> (u16, String) {
    write!(
        stream,
        "GET {path} HTTP/1.1\r\nHost: shop\r\n{extra_header}\r\n"
    )
    .expect("send");
    let mut reader = BufReader::new(stream.try_clone().expect("clone"));
    let mut status_line = String::new();
    reader.read_line(&mut status_line).expect("status line");
    let status = status_line
        .split_whitespace()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .expect("a status code");
    let mut length = 0;
    loop {
        let mut header = String::new();
        reader.read_line(&mut header).expect("header");
        if header.trim_end().is_empty() {
            break;
        }
        if let Some(value) = header.to_ascii_lowercase().strip_prefix("content-length:") {
            length = value.trim().parse().expect("a length");
        }
    }
    let mut body = vec![0; length];
    reader.read_exact(&mut body).expect("body");
    (status, String::from_utf8(body).expect("utf-8"))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn connect(port: u16) -> TcpStream {
        TcpStream::connect(("127.0.0.1", port)).expect("connect")
    }

    #[test]
    fn keep_alive_ten_requests_one_connection() {
        for (reuse, expected) in [(false, 10), (true, 1)] {
            let (port, connections) = start();
            let mut shared = reuse.then(|| connect(port));
            for _ in 0..10 {
                let mut fresh = None;
                let stream = match shared.as_mut() {
                    Some(stream) => stream,
                    None => fresh.insert(connect(port)), // a new TCP connection for each request
                };
                assert_eq!(get(stream, "/fast", "").1, "fast");
            }
            // Each response arrived after the server accepted (and counted) its connection: no waiting needed.
            assert_eq!(connections.load(Ordering::SeqCst), expected);
        }
    }

    #[test]
    fn head_of_line_blocking_on_one_connection() {
        let (port, _) = start();
        let mut stream = connect(port);
        stream.write_all(b"GET /slow HTTP/1.1\r\nHost: shop\r\n\r\nGET /fast HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n").unwrap();
        let mut all = String::new();
        stream.read_to_string(&mut all).unwrap();
        assert!(all.find("slow").unwrap() < all.find("fast").unwrap()); // answered in order: fast waited
    }

    #[test]
    fn an_etag_turns_a_second_download_into_a_304() {
        let (port, _) = start();
        let mut stream = connect(port);
        assert_eq!(get(&mut stream, "/style.css", "").0, 200);
        assert_eq!(
            get(
                &mut stream,
                "/style.css",
                &format!("If-None-Match: {ETAG}\r\n")
            ),
            (304, String::new())
        );
    }

    #[test]
    fn chunked_encoding_on_the_wire() {
        let (port, _) = start();
        let mut stream = connect(port);
        stream
            .write_all(b"GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n")
            .unwrap();
        let mut raw = String::new();
        stream.read_to_string(&mut raw).unwrap();
        let (head, body) = raw.split_once("\r\n\r\n").unwrap();
        assert!(head.contains("Transfer-Encoding: chunked"));
        assert_eq!(body, "5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n");
    }
}
