//! DNS on the wire with only std: building and reading packets, a tiny authoritative UDP server on a thread, and
//! search lists. The same results as the TypeScript lab. (std has no DNS client that can be pointed at a server;
//! crates such as hickory-resolver can.)
use std::collections::HashMap;
use std::net::UdpSocket;

pub const A: u16 = 1;
pub const CNAME: u16 = 5;

pub fn encode_name(name: &str) -> Vec<u8> {
    let mut out = Vec::new();
    for label in name
        .trim_end_matches('.')
        .split('.')
        .filter(|l| !l.is_empty())
    {
        assert!(label.len() <= 63, "label too long: {label}");
        out.push(label.len() as u8);
        out.extend_from_slice(label.as_bytes());
    }
    out.push(0);
    out
}

pub fn build_query(id: u16, name: &str, qtype: u16) -> Vec<u8> {
    let mut msg = Vec::new();
    for field in [id, 0x0100, 1, 0, 0, 0] {
        msg.extend_from_slice(&field.to_be_bytes()); // to_be_bytes: big-endian, network byte order
    }
    msg.extend(encode_name(name));
    msg.extend_from_slice(&qtype.to_be_bytes());
    msg.extend_from_slice(&1u16.to_be_bytes());
    msg
}

fn u16_at(buf: &[u8], at: usize) -> u16 {
    u16::from_be_bytes([buf[at], buf[at + 1]])
}

/// Reads a name and returns it with the offset just past it, following compression pointers.
fn read_name(buf: &[u8], mut offset: usize) -> (String, usize) {
    let (mut labels, mut end, mut jumps) = (Vec::new(), None, 0);
    loop {
        let length = buf[offset] as usize;
        if length == 0 {
            return (labels.join("."), end.unwrap_or(offset + 1));
        }
        if length & 0xc0 == 0xc0 {
            end.get_or_insert(offset + 2);
            offset = (u16_at(buf, offset) & 0x3fff) as usize;
            jumps += 1;
            assert!(jumps <= 20, "compression loop");
            continue;
        }
        labels.push(String::from_utf8_lossy(&buf[offset + 1..offset + 1 + length]).into_owned());
        offset += 1 + length;
    }
}

#[derive(Debug, PartialEq)]
pub struct Answer {
    pub name: String,
    pub rtype: u16,
    pub ttl: u32,
    pub data: String,
}

#[derive(Debug)]
pub struct Message {
    pub id: u16,
    pub truncated: bool,
    pub authoritative: bool,
    pub rcode: u16,
    pub question: (String, u16),
    pub answers: Vec<Answer>,
}

pub fn parse_message(buf: &[u8]) -> Message {
    let flags = u16_at(buf, 2);
    let (qname, mut offset) = read_name(buf, 12);
    let qtype = u16_at(buf, offset);
    offset += 4;
    let mut answers = Vec::new();
    for _ in 0..u16_at(buf, 6) {
        let (name, next) = read_name(buf, offset);
        let rtype = u16_at(buf, next);
        let ttl = u32::from_be_bytes(buf[next + 4..next + 8].try_into().expect("four bytes"));
        let (length, rdata) = (u16_at(buf, next + 8) as usize, next + 10);
        let data = if rtype == A {
            buf[rdata..rdata + 4]
                .iter()
                .map(u8::to_string)
                .collect::<Vec<_>>()
                .join(".")
        } else {
            read_name(buf, rdata).0
        };
        answers.push(Answer {
            name,
            rtype,
            ttl,
            data,
        });
        offset = rdata + length;
    }
    Message {
        id: u16_at(buf, 0),
        truncated: flags & 0x0200 != 0,
        authoritative: flags & 0x0400 != 0,
        rcode: flags & 0xf,
        question: (qname, qtype),
        answers,
    }
}

pub type Zone = HashMap<String, Vec<(u16, u32, String)>>;

/// Serves `zone` on 127.0.0.1 from a background thread, which ends with the process.
pub fn serve(zone: Zone) -> u16 {
    let socket = UdpSocket::bind("127.0.0.1:0").expect("bind");
    let port = socket.local_addr().expect("address").port();
    std::thread::spawn(move || {
        let mut buf = [0u8; 512];
        while let Ok((n, peer)) = socket.recv_from(&mut buf) {
            let query = parse_message(&buf[..n]);
            let (name, qtype) = (query.question.0.to_lowercase(), query.question.1);
            let mut records = Vec::new();
            for (t, ttl, data) in zone.get(&name).into_iter().flatten() {
                records.push((name.clone(), *t, *ttl, data.clone()));
                if *t == CNAME && qtype != CNAME {
                    records.extend(
                        zone.get(data)
                            .into_iter()
                            .flatten()
                            .map(|(t2, ttl2, d2)| (data.clone(), *t2, *ttl2, d2.clone())),
                    );
                }
            }
            records.retain(|r| r.1 == qtype || r.1 == CNAME);
            let mut body = Vec::new();
            for (owner, t, ttl, data) in &records {
                let rdata: Vec<u8> = if *t == A {
                    data.split('.')
                        .map(|p| p.parse().expect("an octet"))
                        .collect()
                } else {
                    encode_name(data)
                };
                body.extend(encode_name(owner));
                for field in [*t, 1] {
                    body.extend_from_slice(&field.to_be_bytes());
                }
                body.extend_from_slice(&ttl.to_be_bytes());
                body.extend_from_slice(&(rdata.len() as u16).to_be_bytes());
                body.extend(rdata);
            }
            let question_end = read_name(&buf, 12).1 + 4; // exactly the question; anything after it (EDNS0) is dropped
            let truncated = question_end + body.len() > 512;
            let flags = 0x8400
                | if truncated { 0x0200 } else { 0 }
                | if zone.contains_key(&name) { 0 } else { 3 };
            let count = if truncated { 0 } else { records.len() as u16 };
            let mut reply = Vec::new();
            for field in [query.id, flags, 1, count, 0, 0] {
                reply.extend_from_slice(&field.to_be_bytes());
            }
            reply.extend_from_slice(&buf[12..question_end]);
            if !truncated {
                reply.extend(body);
            }
            let _ = socket.send_to(&reply, peer);
        }
    });
    port
}

pub fn search_candidates(name: &str, ndots: usize, search: &[&str]) -> Vec<String> {
    if let Some(exact) = name.strip_suffix('.') {
        return vec![exact.to_string()];
    }
    let expanded = search.iter().map(|d| format!("{name}.{d}"));
    if name.matches('.').count() >= ndots {
        std::iter::once(name.to_string()).chain(expanded).collect()
    } else {
        expanded.chain(std::iter::once(name.to_string())).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    fn ask(port: u16, id: u16, name: &str) -> Message {
        let client = UdpSocket::bind("127.0.0.1:0").unwrap();
        client
            .set_read_timeout(Some(Duration::from_secs(2)))
            .unwrap();
        client
            .send_to(&build_query(id, name, A), ("127.0.0.1", port))
            .unwrap();
        let mut buf = [0u8; 4096];
        let n = client.recv(&mut buf).unwrap();
        parse_message(&buf[..n])
    }

    #[test]
    fn names_and_queries_on_the_wire() {
        let hex: String = encode_name("www.example.com")
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect();
        assert_eq!(hex, "03777777076578616d706c6503636f6d00");
        assert_eq!(build_query(0xbeef, "example.com", A).len(), 29);
    }

    #[test]
    fn the_server_follows_the_cname_says_nxdomain_and_truncates() {
        let mut zone = Zone::new();
        zone.insert("example.com".into(), vec![(A, 300, "93.184.216.34".into())]);
        zone.insert(
            "www.example.com".into(),
            vec![(CNAME, 3600, "example.com".into())],
        );
        zone.insert(
            "big.example.com".into(),
            (1..=40).map(|i| (A, 60, format!("10.0.0.{i}"))).collect(),
        );
        let port = serve(zone);
        let reply = ask(port, 42, "www.example.com");
        assert_eq!((reply.id, reply.authoritative), (42, true));
        assert_eq!(
            reply.answers,
            [
                Answer {
                    name: "www.example.com".into(),
                    rtype: CNAME,
                    ttl: 3600,
                    data: "example.com".into()
                },
                Answer {
                    name: "example.com".into(),
                    rtype: A,
                    ttl: 300,
                    data: "93.184.216.34".into()
                },
            ]
        );
        assert_eq!(ask(port, 43, "nope.example.com").rcode, 3);
        let big = ask(port, 7, "big.example.com");
        assert!(big.truncated && big.answers.is_empty());
    }

    #[test]
    fn ndots_turns_one_lookup_into_four_queries() {
        let search = [
            "default.svc.cluster.local",
            "svc.cluster.local",
            "cluster.local",
        ];
        let candidates = search_candidates("api.example.com", 5, &search);
        assert_eq!(
            (candidates.len(), candidates[3].as_str()),
            (4, "api.example.com")
        );
        assert_eq!(
            search_candidates("api.example.com.", 5, &search),
            ["api.example.com"]
        );
    }
}
