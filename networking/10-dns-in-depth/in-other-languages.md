# DNS in Depth in Other Languages

**[Intermediate]** — A companion to [[networking/10-dns-in-depth/index|DNS in depth]], which builds DNS packets by hand, runs a tiny authoritative server over UDP, and puts numbers on caching and search lists. This page does the same in Python, Go, Java, Rust and C#. Every language builds the same bytes and gets the same answers. Two things differ more than you'd expect. One is how each language writes a 16-bit number in network byte order. The other is whether its *own* resolver can be pointed at a DNS server you choose: Go's and Java's can, while Python's, Rust's and C#'s always ask the operating system.

## Before you start

You can already:

- Read a DNS message's header, question and answers, and explain TTLs, truncation and search lists → [[networking/10-dns-in-depth/index|the main lesson]].
- Send a UDP datagram in at least one of the languages here.

After this lesson you will be able to:

1. Write and read big-endian ("network byte order") fields in your language.
2. Run a UDP server on 127.0.0.1 in your language and answer a datagram.
3. Say whether your language's standard resolver can query a server you choose, and what library to use if not.

## The kid version

Five people write the same letter in five handwritings. The post office only cares that the address is in the right boxes, in the right order. One writer puts the house number before the street, as their country does, and the letter goes astray. Computers have the same problem with numbers: some store the "big end" of a number first, some the "little end", and DNS insists on the big end first.

**Where the analogy stops working.** You can see a muddled address. A 16-bit number in the wrong byte order is just a different, perfectly valid number: query ID 42 becomes 10,752, and the reply simply never matches, with no error. That's why every language here uses an explicitly big-endian call.

## 1. The tools, by ecosystem

| Language | Writing big-endian fields | UDP server | The standard resolver, pointed at your server |
|---|---|---|---|
| TypeScript | `Buffer.writeUInt16BE` | `node:dgram` | **yes**: `new Resolver()` and `setServers([…])` |
| Python | `struct.pack("!H", …)` | `socket.socket(AF_INET, SOCK_DGRAM)` | no: `getaddrinfo` asks the system (use dnspython) |
| Go | `binary.BigEndian.AppendUint16` | `net.ListenUDP` | **yes**: `net.Resolver{PreferGo: true, Dial: …}` |
| Java | `ByteBuffer` (big-endian by default) | `DatagramSocket` | **yes**: JNDI's DNS provider, `dns://127.0.0.1:port` |
| Rust | `u16::to_be_bytes` | `std::net::UdpSocket` | no: std has no DNS client (use hickory-resolver) |
| C# | `BinaryPrimitives.WriteUInt16BigEndian` | `UdpClient` | no: `Dns` asks the system (use DnsClient.NET) |

C would use `htons` to convert to network byte order, the BSD sockets API for UDP, and `res_query` or a library like c-ares (which is what Node's resolver uses); no lab here.

## 2. What changes between languages

### Byte order, said out loud

Every language makes you say "big-endian" somewhere, which is good: x86 and ARM machines store numbers little-endian, so the native order would be wrong. Python's `struct` format starts with `!`, meaning network order. Java's `ByteBuffer` is big-endian unless told otherwise. Go, Rust and C# have explicit big-endian functions. Reading needs the same care, plus one Java-specific trap: Java's `byte` is *signed*, so a length byte of 200 reads as −56 unless masked with `& 0xff`. The Java lab masks every byte it reads as a number, and uses `Short.toUnsignedInt` for 16-bit fields.

### A bug the other resolvers exposed

The lab's first servers echoed everything after the 12-byte header back as "the question". Node's resolver sends exactly one question, so the TypeScript lab passed. **Go's resolver adds an EDNS0 record after the question**, announcing it can take bigger replies, so the echoed reply contained an extra record that the header said wasn't there, and every answer after it was misread. Go reported "no such host". The fix, now in every language: copy exactly the question section, up to the end of its name plus four bytes. It's a good example of why a protocol implementation needs testing against more than one client.

### Pointing the standard resolver at your server

- **Go's** `net.Resolver` takes a `Dial` function, so the lab sends its queries to 127.0.0.1. `PreferGo: true` matters: without it, Go may use the C library's resolver, which ignores `Dial`. Go's resolver reports "no such host" as a `*net.DNSError` with `IsNotFound`.
- **Java's** JNDI has a DNS provider in the JDK. With the URL `dns://127.0.0.1:port`, `getAttributes(name, {"A"})` asks the lab's server, and NXDOMAIN arrives as `NameNotFoundException`.
- **Python's** `socket.getaddrinfo`, **Rust's** `ToSocketAddrs` and **C#'s** `Dns.GetHostAddressesAsync` all go through the operating system's resolver, configured by `/etc/resolv.conf`. Talking to a specific server needs a library: dnspython, hickory-resolver, DnsClient.NET.

### A server in the background

Each lab runs its server alongside the test. Python uses a daemon thread, which ends when closing the socket makes `recvfrom` raise. Go uses a goroutine, which ends when the connection is closed. Java uses a virtual thread, C# a `Task`, and Rust a `std::thread` that simply lives as long as the test process.

## 3. The same results, in every language

| Check | Expected in every language |
|---|---|
| `www.example.com` encoded | `03777777076578616d706c6503636f6d00` |
| a query for `example.com`, type A | 29 bytes |
| `www.example.com`, type A | ID echoed, authoritative; a CNAME (TTL 3,600) then an A record (TTL 300) |
| `nope.example.com` | response code 3, NXDOMAIN |
| 40 A records | truncated, with no answers |
| `api.example.com` with `ndots:5` and three search domains | 4 queries, the real name last; with a trailing dot, 1 |

Python's lab also replays the migration (86,340 stale seconds against 0). The iterative walk and negative caching are in the TypeScript lab only.

## Terms used in this lesson

1. **Byte order**: This is also called **endianness**. It's the order in which a number's bytes are stored: big-endian puts the most significant byte first, little-endian the least.
2. **Network byte order**: This is big-endian, the byte order internet protocols use on the wire.
3. **EDNS0**: This is the extension that lets a DNS client say it can accept larger replies, sent as an extra record after the question.
4. **Signed byte**: This is a byte read as a number from −128 to 127. Java's `byte` is always signed.

## 4. Python

`struct.pack("!HHHHHH", …)` writes the header in one call; `!` means network byte order and `H` an unsigned 16-bit field. The server runs in a daemon thread on a UDP socket.

```python
"""DNS on the wire, with the standard library only: building and reading packets with struct, a tiny authoritative
server on a UDP socket, and the caching and search-list behaviour of resolvers. The same results as the TypeScript lab.
(Python's own resolver, socket.getaddrinfo, always asks the system's configured server; dnspython can ask any.)"""
import socket
import struct
import threading
from dataclasses import dataclass, field

A, CNAME = 1, 5


def encode_name(name: str) -> bytes:
    out = bytearray()
    for label in filter(None, name.rstrip(".").split(".")):
        if len(label) > 63:
            raise ValueError(f"label too long: {label}")
        out += bytes([len(label)]) + label.encode("ascii")
    return bytes(out + b"\x00")


def build_query(id_: int, name: str, qtype: int) -> bytes:
    # !: network byte order (big-endian). H: an unsigned 16-bit field. ID, flags (RD), one question, no other records.
    return struct.pack("!HHHHHH", id_, 0x0100, 1, 0, 0, 0) + encode_name(name) + struct.pack("!HH", qtype, 1)


def read_name(buf: bytes, offset: int) -> tuple[str, int]:
    labels, end, jumps = [], None, 0
    while True:
        length = buf[offset]
        if length == 0:
            return ".".join(labels), end if end is not None else offset + 1
        if length & 0xC0 == 0xC0:  # a compression pointer: the rest of the name is elsewhere in the message
            if end is None:
                end = offset + 2
            offset = struct.unpack_from("!H", buf, offset)[0] & 0x3FFF
            jumps += 1
            if jumps > 20:
                raise ValueError("compression loop")
            continue
        labels.append(buf[offset + 1 : offset + 1 + length].decode("ascii"))
        offset += 1 + length


@dataclass
class Message:
    id: int
    truncated: bool
    authoritative: bool
    rcode: int
    question: tuple[str, int]
    answers: list[tuple[str, int, int, str]] = field(default_factory=list)  # name, type, ttl, data


def parse_message(buf: bytes) -> Message:
    id_, flags, _, ancount, _, _ = struct.unpack_from("!HHHHHH", buf, 0)
    qname, offset = read_name(buf, 12)
    qtype = struct.unpack_from("!H", buf, offset)[0]
    message = Message(id_, bool(flags & 0x0200), bool(flags & 0x0400), flags & 0x000F, (qname, qtype))
    offset += 4
    for _ in range(ancount):
        name, offset = read_name(buf, offset)
        rtype, _, ttl, length = struct.unpack_from("!HHIH", buf, offset)
        rdata = offset + 10
        data = ".".join(map(str, buf[rdata : rdata + 4])) if rtype == A else read_name(buf, rdata)[0]
        message.answers.append((name, rtype, ttl, data))
        offset = rdata + length
    return message


def serve(zone: dict[str, list[tuple[int, int, str]]]) -> tuple[socket.socket, threading.Thread]:
    """An authoritative server on 127.0.0.1 in a background thread. Records are (type, ttl, data)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))

    def loop():
        while True:
            try:
                query, peer = sock.recvfrom(512)
            except OSError:
                return  # the socket was closed: stop
            msg = parse_message(query)
            name, qtype = msg.question
            records, current = [], name.lower()
            for rtype, ttl, data in zone.get(current, []):
                records.append((current, rtype, ttl, data))
                if rtype == CNAME and qtype != CNAME:
                    records += [(data, t, tt, d) for t, tt, d in zone.get(data, [])]
            body = b"".join(
                encode_name(n) + struct.pack("!HHIH", t, 1, ttl, 4 if t == A else len(encode_name(d)))
                + (bytes(map(int, d.split("."))) if t == A else encode_name(d))
                for n, t, ttl, d in records if t in (qtype, CNAME))
            question = query[12 : read_name(query, 12)[1] + 4]  # exactly the question: anything after it (EDNS0) isn't echoed
            truncated = 12 + len(question) + len(body) > 512
            count = 0 if truncated else sum(1 for r in records if r[1] in (qtype, CNAME))
            flags = 0x8400 | (0x0200 if truncated else 0) | (0 if name.lower() in zone else 3)
            header = struct.pack("!HHHHHH", msg.id, flags, 1, count, 0, 0)
            sock.sendto(header + question + (b"" if truncated else body), peer)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return sock, thread


def ask(port: int, query: bytes) -> Message:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(2)
        client.sendto(query, ("127.0.0.1", port))
        return parse_message(client.recv(4096))


class CachingResolver:
    def __init__(self, now, upstream):
        self._now, self._upstream, self._cache, self.upstream_queries = now, upstream, {}, 0

    def lookup(self, name: str):
        hit = self._cache.get(name)
        if hit and hit[1] > self._now():
            return hit[0]
        self.upstream_queries += 1
        address, ttl = self._upstream(name)
        self._cache[name] = (address, self._now() + ttl * 1000)
        return address


def search_candidates(name: str, ndots: int, search: list[str]) -> list[str]:
    if name.endswith("."):
        return [name[:-1]]
    expanded = [f"{name}.{domain}" for domain in search]
    return [name, *expanded] if name.count(".") >= ndots else [*expanded, name]
```

```python
import unittest

from dns import A, CNAME, CachingResolver, ask, build_query, encode_name, parse_message, search_candidates, serve

ZONE = {
    "example.com": [(A, 300, "93.184.216.34")],
    "www.example.com": [(CNAME, 3600, "example.com")],
    "big.example.com": [(A, 60, f"10.0.0.{i + 1}") for i in range(40)],
}


class Dns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sock, _ = serve(ZONE)
        cls.port = cls.sock.getsockname()[1]

    @classmethod
    def tearDownClass(cls):
        cls.sock.close()

    def test_names_and_queries_on_the_wire(self):
        self.assertEqual(encode_name("www.example.com").hex(), "03777777076578616d706c6503636f6d00")
        query = build_query(0xBEEF, "example.com", A)
        self.assertEqual(len(query), 29)
        self.assertEqual(parse_message(query).question, ("example.com", A))

    def test_the_server_follows_the_cname_and_says_nxdomain(self):
        reply = ask(self.port, build_query(42, "www.example.com", A))
        self.assertEqual((reply.id, reply.authoritative), (42, True))
        self.assertEqual(reply.answers, [("www.example.com", CNAME, 3600, "example.com"), ("example.com", A, 300, "93.184.216.34")])
        self.assertEqual(ask(self.port, build_query(43, "nope.example.com", A)).rcode, 3)

    def test_too_big_for_udp_comes_back_truncated(self):
        reply = ask(self.port, build_query(7, "big.example.com", A))
        self.assertEqual((reply.truncated, reply.answers), (True, []))

    def test_a_migration_lower_the_ttl_a_day_ahead(self):
        for old_ttl, stale_seconds in [(86_400, 86_340), (60, 0)]:
            state = {"now": 0, "address": "198.51.100.1", "ttl": old_ttl}
            resolver = CachingResolver(lambda: state["now"], lambda name: (state["address"], state["ttl"]))
            resolver.lookup("shop.example")
            state.update(now=60_000, address="203.0.113.9", ttl=60)
            stale = 0
            for t in range(60, 86_400 + 60, 60):
                state["now"] = t * 1000
                if resolver.lookup("shop.example") == "198.51.100.1":
                    stale += 60
            self.assertEqual(stale, stale_seconds)

    def test_ndots_turns_one_lookup_into_four_queries(self):
        search = ["default.svc.cluster.local", "svc.cluster.local", "cluster.local"]
        self.assertEqual(len(search_candidates("api.example.com", 5, search)), 4)
        self.assertEqual(search_candidates("api.example.com", 5, search)[-1], "api.example.com")
        self.assertEqual(search_candidates("api.example.com.", 5, search), ["api.example.com"])


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/10-dns-in-depth/labs/python). `python3 labs/run.py dns-in-depth/python`.

## 5. Go

`binary.BigEndian.AppendUint16` builds the message, and `net.IP` formats addresses. `Resolver` returns a `net.Resolver` whose `Dial` sends every query to the lab's server, and the test checks Go's own lookup against it. The lab runs with `-race`.

```go
// Package dns: DNS on the wire with encoding/binary, a tiny authoritative UDP server, and resolver caching and
// search lists. The same results as the TypeScript lab.
package dns

import (
	"context"
	"encoding/binary"
	"errors"
	"fmt"
	"net"
	"strings"
)

const (
	TypeA     = 1
	TypeCNAME = 5
)

func EncodeName(name string) ([]byte, error) {
	var out []byte
	for _, label := range strings.Split(strings.TrimSuffix(name, "."), ".") {
		if label == "" {
			continue
		}
		if len(label) > 63 {
			return nil, fmt.Errorf("label too long: %s", label)
		}
		out = append(append(out, byte(len(label))), label...)
	}
	return append(out, 0), nil
}

func BuildQuery(id uint16, name string, qtype uint16) ([]byte, error) {
	encoded, err := EncodeName(name)
	if err != nil {
		return nil, err
	}
	msg := binary.BigEndian.AppendUint16(nil, id)
	msg = binary.BigEndian.AppendUint16(msg, 0x0100) // RD: recursion desired
	msg = binary.BigEndian.AppendUint16(msg, 1)      // one question
	msg = append(msg, 0, 0, 0, 0, 0, 0)              // no answers, authority or additional records
	msg = append(msg, encoded...)
	msg = binary.BigEndian.AppendUint16(msg, qtype)
	return binary.BigEndian.AppendUint16(msg, 1), nil // class IN
}

func readName(buf []byte, offset int) (string, int, error) {
	var labels []string
	end := -1
	for jumps := 0; ; {
		if offset >= len(buf) {
			return "", 0, errors.New("name runs past the message")
		}
		length := int(buf[offset])
		switch {
		case length == 0:
			if end == -1 {
				end = offset + 1
			}
			return strings.Join(labels, "."), end, nil
		case length&0xc0 == 0xc0: // a compression pointer
			if end == -1 {
				end = offset + 2
			}
			offset = int(binary.BigEndian.Uint16(buf[offset:]) & 0x3fff)
			if jumps++; jumps > 20 {
				return "", 0, errors.New("compression loop")
			}
		default:
			labels = append(labels, string(buf[offset+1:offset+1+length]))
			offset += 1 + length
		}
	}
}

type Answer struct {
	Name string
	Type uint16
	TTL  uint32
	Data string
}

type Message struct {
	ID                       uint16
	Truncated, Authoritative bool
	Rcode                    int
	Question                 string
	QType                    uint16
	Answers                  []Answer
}

func ParseMessage(buf []byte) (Message, error) {
	if len(buf) < 12 {
		return Message{}, errors.New("shorter than a header")
	}
	flags := binary.BigEndian.Uint16(buf[2:])
	m := Message{ID: binary.BigEndian.Uint16(buf), Truncated: flags&0x0200 != 0, Authoritative: flags&0x0400 != 0, Rcode: int(flags & 0xf)}
	name, offset, err := readName(buf, 12)
	if err != nil {
		return m, err
	}
	m.Question, m.QType = name, binary.BigEndian.Uint16(buf[offset:])
	offset += 4
	for range binary.BigEndian.Uint16(buf[6:]) {
		var a Answer
		if a.Name, offset, err = readName(buf, offset); err != nil {
			return m, err
		}
		a.Type, a.TTL = binary.BigEndian.Uint16(buf[offset:]), binary.BigEndian.Uint32(buf[offset+4:])
		length, rdata := int(binary.BigEndian.Uint16(buf[offset+8:])), offset+10
		if a.Type == TypeA {
			a.Data = net.IP(buf[rdata : rdata+4]).String()
		} else if a.Data, _, err = readName(buf, rdata); err != nil {
			return m, err
		}
		m.Answers = append(m.Answers, a)
		offset = rdata + length
	}
	return m, nil
}

type Record struct {
	Type uint16
	TTL  uint32
	Data string
}

// Serve answers from zone on 127.0.0.1 until the returned connection is closed.
func Serve(zone map[string][]Record) (*net.UDPConn, error) {
	conn, err := net.ListenUDP("udp", &net.UDPAddr{IP: net.IPv4(127, 0, 0, 1)})
	if err != nil {
		return nil, err
	}
	go func() {
		buf := make([]byte, 512)
		for {
			n, peer, err := conn.ReadFromUDP(buf)
			if err != nil {
				return // closed
			}
			query, err := ParseMessage(buf[:n])
			if err != nil {
				continue
			}
			name := strings.ToLower(query.Question)
			var body []byte
			count := uint16(0)
			add := func(owner string, r Record) {
				if r.Type != query.QType && r.Type != TypeCNAME {
					return
				}
				encoded, _ := EncodeName(owner)
				rdata := net.ParseIP(r.Data).To4()
				if r.Type != TypeA {
					rdata, _ = EncodeName(r.Data)
				}
				body = append(body, encoded...)
				body = binary.BigEndian.AppendUint16(body, r.Type)
				body = binary.BigEndian.AppendUint16(body, 1)
				body = binary.BigEndian.AppendUint32(body, r.TTL)
				body = binary.BigEndian.AppendUint16(body, uint16(len(rdata)))
				body = append(body, rdata...)
				count++
			}
			for _, r := range zone[name] {
				add(name, r)
				if r.Type == TypeCNAME && query.QType != TypeCNAME {
					for _, target := range zone[r.Data] {
						add(r.Data, target)
					}
				}
			}
			// Copy exactly the question: a resolver may add records after it (Go's sends an EDNS0 OPT record), and the
			// reply says it has no additional records.
			_, nameEnd, _ := readName(buf[:n], 12)
			question := buf[12 : nameEnd+4]
			truncated := 12+len(question)+len(body) > 512
			flags := uint16(0x8400)
			if truncated {
				flags, body, count = flags|0x0200, nil, 0
			}
			if _, ok := zone[name]; !ok {
				flags |= 3 // NXDOMAIN
			}
			reply := binary.BigEndian.AppendUint16(nil, query.ID)
			reply = binary.BigEndian.AppendUint16(reply, flags)
			reply = binary.BigEndian.AppendUint16(reply, 1)
			reply = binary.BigEndian.AppendUint16(reply, count)
			reply = append(append(append(reply, 0, 0, 0, 0), question...), body...)
			conn.WriteToUDP(reply, peer)
		}
	}()
	return conn, nil
}

// Resolver returns Go's own DNS resolver, sending every query to addr instead of the system's server.
func Resolver(addr string) *net.Resolver {
	return &net.Resolver{
		PreferGo: true, // the pure-Go resolver, which uses Dial; the cgo one asks the C library instead
		Dial: func(ctx context.Context, network, _ string) (net.Conn, error) {
			var d net.Dialer
			return d.DialContext(ctx, network, addr)
		},
	}
}

func SearchCandidates(name string, ndots int, search []string) []string {
	if strings.HasSuffix(name, ".") {
		return []string{strings.TrimSuffix(name, ".")}
	}
	var expanded []string
	for _, domain := range search {
		expanded = append(expanded, name+"."+domain)
	}
	if strings.Count(name, ".") >= ndots {
		return append([]string{name}, expanded...)
	}
	return append(expanded, name)
}
```

```go
package dns

import (
	"context"
	"encoding/hex"
	"errors"
	"fmt"
	"net"
	"slices"
	"testing"
)

var zone = map[string][]Record{
	"example.com":     {{TypeA, 300, "93.184.216.34"}},
	"www.example.com": {{TypeCNAME, 3600, "example.com"}},
	"big.example.com": func() (rs []Record) {
		for i := 1; i <= 40; i++ {
			rs = append(rs, Record{TypeA, 60, fmt.Sprintf("10.0.0.%d", i)})
		}
		return rs
	}(),
}

func ask(t *testing.T, port int, id uint16, name string) Message {
	t.Helper()
	query, _ := BuildQuery(id, name, TypeA)
	conn, err := net.DialUDP("udp", nil, &net.UDPAddr{IP: net.IPv4(127, 0, 0, 1), Port: port})
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()
	conn.Write(query)
	buf := make([]byte, 4096)
	n, err := conn.Read(buf)
	if err != nil {
		t.Fatal(err)
	}
	m, err := ParseMessage(buf[:n])
	if err != nil {
		t.Fatal(err)
	}
	return m
}

func server(t *testing.T) int {
	conn, err := Serve(zone)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { conn.Close() })
	return conn.LocalAddr().(*net.UDPAddr).Port
}

func TestNamesAndQueriesOnTheWire(t *testing.T) {
	name, _ := EncodeName("www.example.com")
	query, _ := BuildQuery(0xbeef, "example.com", TypeA)
	if hex.EncodeToString(name) != "03777777076578616d706c6503636f6d00" || len(query) != 29 {
		t.Fatal(hex.EncodeToString(name), len(query))
	}
}

func TestTheServerFollowsTheCNAMEAndSaysNXDOMAIN(t *testing.T) {
	port := server(t)
	reply := ask(t, port, 42, "www.example.com")
	want := []Answer{{"www.example.com", TypeCNAME, 3600, "example.com"}, {"example.com", TypeA, 300, "93.184.216.34"}}
	if reply.ID != 42 || !reply.Authoritative || !slices.Equal(reply.Answers, want) {
		t.Fatal(reply)
	}
	if missing := ask(t, port, 43, "nope.example.com"); missing.Rcode != 3 {
		t.Fatal(missing.Rcode)
	}
	if big := ask(t, port, 7, "big.example.com"); !big.Truncated || len(big.Answers) != 0 {
		t.Fatal(big.Truncated, len(big.Answers))
	}
}

func TestGosOwnResolverAgrees(t *testing.T) {
	port := server(t)
	resolver := Resolver(fmt.Sprintf("127.0.0.1:%d", port))
	addrs, err := resolver.LookupHost(context.Background(), "example.com")
	if err != nil || !slices.Equal(addrs, []string{"93.184.216.34"}) {
		t.Fatal(addrs, err)
	}
	_, err = resolver.LookupHost(context.Background(), "nope.example.com")
	var dnsErr *net.DNSError
	if !errors.As(err, &dnsErr) || !dnsErr.IsNotFound {
		t.Fatal(err)
	}
}

func TestNdotsTurnsOneLookupIntoFourQueries(t *testing.T) {
	search := []string{"default.svc.cluster.local", "svc.cluster.local", "cluster.local"}
	got := SearchCandidates("api.example.com", 5, search)
	if len(got) != 4 || got[3] != "api.example.com" || !slices.Equal(SearchCandidates("api.example.com.", 5, search), []string{"api.example.com"}) {
		t.Fatal(got)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/10-dns-in-depth/labs/go). `python3 labs/run.py dns-in-depth/go`.

## 6. Java

`ByteBuffer` reads and writes big-endian fields; every byte read as a number is masked with `& 0xff`. The server runs on a virtual thread. The check also queries the lab's server through JNDI's DNS provider, the JDK's own DNS client.

```java
package dns;

import java.io.ByteArrayOutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** DNS on the wire with ByteBuffer, and a tiny authoritative UDP server. The same results as the TypeScript lab. */
public final class Dns {
    private Dns() {}

    public static final int A = 1;
    public static final int CNAME = 5;

    public static byte[] encodeName(String name) {
        var out = new ByteArrayOutputStream();
        for (String label : name.replaceAll("\\.$", "").split("\\.")) {
            if (label.isEmpty()) continue;
            if (label.length() > 63) throw new IllegalArgumentException("label too long: " + label);
            out.write(label.length());
            out.writeBytes(label.getBytes(StandardCharsets.US_ASCII));
        }
        out.write(0);
        return out.toByteArray();
    }

    public static byte[] buildQuery(int id, String name, int type) {
        byte[] encoded = encodeName(name);
        // ByteBuffer is big-endian by default: network byte order, as DNS wants.
        return ByteBuffer.allocate(12 + encoded.length + 4)
                .putShort((short) id).putShort((short) 0x0100).putShort((short) 1).putShort((short) 0).putShort((short) 0).putShort((short) 0)
                .put(encoded).putShort((short) type).putShort((short) 1).array();
    }

    record Name(String name, int end) {}

    static Name readName(byte[] buf, int offset) {
        var labels = new ArrayList<String>();
        int end = -1;
        for (int jumps = 0; ; ) {
            int length = buf[offset] & 0xff; // Java's byte is signed: mask to read it as 0–255
            if (length == 0) return new Name(String.join(".", labels), end == -1 ? offset + 1 : end);
            if ((length & 0xc0) == 0xc0) {
                if (end == -1) end = offset + 2;
                offset = ((length & 0x3f) << 8) | (buf[offset + 1] & 0xff);
                if (++jumps > 20) throw new IllegalStateException("compression loop");
                continue;
            }
            labels.add(new String(buf, offset + 1, length, StandardCharsets.US_ASCII));
            offset += 1 + length;
        }
    }

    public record Answer(String name, int type, long ttl, String data) {}

    public record Message(int id, boolean truncated, boolean authoritative, int rcode, String question, List<Answer> answers) {}

    public static Message parse(byte[] buf, int length) {
        var bb = ByteBuffer.wrap(buf, 0, length);
        int id = Short.toUnsignedInt(bb.getShort(0));
        int flags = Short.toUnsignedInt(bb.getShort(2));
        int count = Short.toUnsignedInt(bb.getShort(6));
        Name q = readName(buf, 12);
        int offset = q.end() + 4;
        List<Answer> answers = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            Name n = readName(buf, offset);
            int type = Short.toUnsignedInt(bb.getShort(n.end()));
            long ttl = Integer.toUnsignedLong(bb.getInt(n.end() + 4));
            int rdLength = Short.toUnsignedInt(bb.getShort(n.end() + 8));
            int rdata = n.end() + 10;
            String data = type == A
                    ? (buf[rdata] & 0xff) + "." + (buf[rdata + 1] & 0xff) + "." + (buf[rdata + 2] & 0xff) + "." + (buf[rdata + 3] & 0xff)
                    : readName(buf, rdata).name();
            answers.add(new Answer(n.name(), type, ttl, data));
            offset = rdata + rdLength;
        }
        return new Message(id, (flags & 0x0200) != 0, (flags & 0x0400) != 0, flags & 0xf, q.name(), answers);
    }

    public record Rec(int type, int ttl, String data) {}

    /** Serves `zone` on 127.0.0.1 from a virtual thread until the socket is closed. */
    public static DatagramSocket serve(Map<String, List<Rec>> zone) throws Exception {
        var socket = new DatagramSocket(0, InetAddress.getLoopbackAddress());
        Thread.ofVirtual().start(() -> {
            byte[] buf = new byte[512];
            while (!socket.isClosed()) {
                try {
                    var packet = new DatagramPacket(buf, buf.length);
                    socket.receive(packet);
                    Message query = parse(buf, packet.getLength());
                    int qtype = Short.toUnsignedInt(ByteBuffer.wrap(buf).getShort(readName(buf, 12).end()));
                    String name = query.question().toLowerCase();
                    var body = new ByteArrayOutputStream();
                    int count = 0;
                    for (Rec r : zone.getOrDefault(name, List.of())) {
                        count += write(body, name, r, qtype);
                        if (r.type() == CNAME && qtype != CNAME) {
                            for (Rec target : zone.getOrDefault(r.data(), List.of())) count += write(body, r.data(), target, qtype);
                        }
                    }
                    int questionEnd = readName(buf, 12).end() + 4; // exactly the question; anything after it (EDNS0) is dropped
                    boolean truncated = questionEnd + body.size() > 512;
                    int flags = 0x8400 | (truncated ? 0x0200 : 0) | (zone.containsKey(name) ? 0 : 3);
                    var reply = ByteBuffer.allocate(questionEnd + (truncated ? 0 : body.size()))
                            .putShort((short) query.id()).putShort((short) flags).putShort((short) 1).putShort((short) (truncated ? 0 : count))
                            .putShort((short) 0).putShort((short) 0).put(buf, 12, questionEnd - 12);
                    if (!truncated) reply.put(body.toByteArray());
                    socket.send(new DatagramPacket(reply.array(), reply.capacity(), packet.getSocketAddress()));
                } catch (Exception e) {
                    if (socket.isClosed()) return;
                }
            }
        });
        return socket;
    }

    private static int write(ByteArrayOutputStream body, String owner, Rec r, int qtype) {
        if (r.type() != qtype && r.type() != CNAME) return 0;
        byte[] rdata = r.type() == A ? ipv4(r.data()) : encodeName(r.data());
        body.writeBytes(encodeName(owner));
        body.writeBytes(ByteBuffer.allocate(10).putShort((short) r.type()).putShort((short) 1).putInt(r.ttl()).putShort((short) rdata.length).array());
        body.writeBytes(rdata);
        return 1;
    }

    private static byte[] ipv4(String address) {
        String[] parts = address.split("\\.");
        byte[] out = new byte[4];
        for (int i = 0; i < 4; i++) out[i] = (byte) Integer.parseInt(parts[i]);
        return out;
    }

    public static List<String> searchCandidates(String name, int ndots, List<String> search) {
        if (name.endsWith(".")) return List.of(name.substring(0, name.length() - 1));
        List<String> expanded = search.stream().map(d -> name + "." + d).toList();
        long dots = name.chars().filter(c -> c == '.').count();
        List<String> out = new ArrayList<>();
        if (dots >= ndots) out.add(name);
        out.addAll(expanded);
        if (dots < ndots) out.add(name);
        return out;
    }
}
```

```java
package dns;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.HexFormat;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;
import javax.naming.NameNotFoundException;
import javax.naming.directory.InitialDirContext;

/** The same checks as every other language. Run with -ea. */
public final class DnsCheck {
    private DnsCheck() {}

    static Dns.Message ask(int port, int id, String name) throws Exception {
        try (var client = new DatagramSocket()) {
            byte[] query = Dns.buildQuery(id, name, Dns.A);
            client.send(new DatagramPacket(query, query.length, InetAddress.getLoopbackAddress(), port));
            byte[] buf = new byte[4096];
            var packet = new DatagramPacket(buf, buf.length);
            client.setSoTimeout(2000);
            client.receive(packet);
            return Dns.parse(buf, packet.getLength());
        }
    }

    public static void main(String[] args) throws Exception {
        assert HexFormat.of().formatHex(Dns.encodeName("www.example.com")).equals("03777777076578616d706c6503636f6d00");
        assert Dns.buildQuery(0xbeef, "example.com", Dns.A).length == 29;

        var zone = Map.of(
                "example.com", List.of(new Dns.Rec(Dns.A, 300, "93.184.216.34")),
                "www.example.com", List.of(new Dns.Rec(Dns.CNAME, 3600, "example.com")),
                "big.example.com", IntStream.rangeClosed(1, 40).mapToObj(i -> new Dns.Rec(Dns.A, 60, "10.0.0." + i)).toList());
        try (var server = Dns.serve(zone)) {
            int port = server.getLocalPort();
            var reply = ask(port, 42, "www.example.com");
            assert reply.id() == 42 && reply.authoritative();
            assert reply.answers().equals(List.of(
                    new Dns.Answer("www.example.com", Dns.CNAME, 3600, "example.com"),
                    new Dns.Answer("example.com", Dns.A, 300, "93.184.216.34"))) : reply.answers();
            assert ask(port, 43, "nope.example.com").rcode() == 3;
            var big = ask(port, 7, "big.example.com");
            assert big.truncated() && big.answers().isEmpty();

            // Java's JNDI DNS provider can query any server: the JDK's own DNS client, pointed at ours.
            var env = new Hashtable<String, String>();
            env.put("java.naming.factory.initial", "com.sun.jndi.dns.DnsContextFactory");
            env.put("java.naming.provider.url", "dns://127.0.0.1:" + port);
            var ctx = new InitialDirContext(env);
            assert ctx.getAttributes("example.com", new String[] {"A"}).get("A").get().equals("93.184.216.34");
            try {
                ctx.getAttributes("nope.example.com", new String[] {"A"});
                throw new AssertionError("expected NXDOMAIN");
            } catch (NameNotFoundException expected) {
                // NXDOMAIN, as an exception
            }
            ctx.close();
        }

        var search = List.of("default.svc.cluster.local", "svc.cluster.local", "cluster.local");
        assert Dns.searchCandidates("api.example.com", 5, search).size() == 4;
        assert Dns.searchCandidates("api.example.com", 5, search).getLast().equals("api.example.com");
        assert Dns.searchCandidates("api.example.com.", 5, search).equals(List.of("api.example.com"));
        System.out.println("all dns checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/10-dns-in-depth/labs/java). `python3 labs/run.py dns-in-depth/java`.

## 7. Rust

`to_be_bytes` and `from_be_bytes` convert integers to and from big-endian byte arrays. `read_name` uses `get_or_insert` to remember where a name ended before its first pointer. The server thread owns its socket and the zone, moved into its closure.

```rust
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
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/10-dns-in-depth/labs/rust). `python3 labs/run.py dns-in-depth/rust`.

## 8. C#

`BinaryPrimitives` reads and writes big-endian fields on spans, and collection expressions (`[.. a, .. b]`) assemble each message. The server is a `Task` looping on `UdpClient.ReceiveAsync`. It runs in the .NET SDK container, where both server and client use the container's own 127.0.0.1.

```csharp
// DNS on the wire with BinaryPrimitives, and a tiny authoritative UDP server. The same results as the TypeScript
// lab. (.NET's Dns class always asks the operating system; DnsClient.NET can ask any server.)
using System.Buffers.Binary;
using System.Net;
using System.Net.Sockets;
using System.Text;

public record Answer(string Name, ushort Type, uint Ttl, string Data);

public record Message(ushort Id, bool Truncated, bool Authoritative, int Rcode, string Question, ushort QType, List<Answer> Answers);

public record Rec(ushort Type, uint Ttl, string Data);

public static class DnsWire
{
    public const ushort A = 1, CName = 5;

    public static byte[] EncodeName(string name)
    {
        var out_ = new List<byte>();
        foreach (var label in name.TrimEnd('.').Split('.', StringSplitOptions.RemoveEmptyEntries))
        {
            if (label.Length > 63) throw new ArgumentException($"label too long: {label}");
            out_.Add((byte)label.Length);
            out_.AddRange(Encoding.ASCII.GetBytes(label));
        }
        out_.Add(0);
        return [.. out_];
    }

    static byte[] U16(ushort v)
    {
        var b = new byte[2];
        BinaryPrimitives.WriteUInt16BigEndian(b, v); // network byte order, whatever the machine's
        return b;
    }

    public static byte[] BuildQuery(ushort id, string name, ushort type) =>
        [.. U16(id), .. U16(0x0100), .. U16(1), 0, 0, 0, 0, 0, 0, .. EncodeName(name), .. U16(type), .. U16(1)];

    public static (string Name, int End) ReadName(ReadOnlySpan<byte> buf, int offset)
    {
        var labels = new List<string>();
        var end = -1;
        for (var jumps = 0; ;)
        {
            int length = buf[offset];
            if (length == 0) return (string.Join('.', labels), end == -1 ? offset + 1 : end);
            if ((length & 0xc0) == 0xc0)
            {
                if (end == -1) end = offset + 2;
                offset = BinaryPrimitives.ReadUInt16BigEndian(buf[offset..]) & 0x3fff;
                if (++jumps > 20) throw new InvalidDataException("compression loop");
                continue;
            }
            labels.Add(Encoding.ASCII.GetString(buf.Slice(offset + 1, length)));
            offset += 1 + length;
        }
    }

    public static Message Parse(ReadOnlySpan<byte> buf)
    {
        var flags = BinaryPrimitives.ReadUInt16BigEndian(buf[2..]);
        var (qname, offset) = ReadName(buf, 12);
        var qtype = BinaryPrimitives.ReadUInt16BigEndian(buf[offset..]);
        offset += 4;
        var answers = new List<Answer>();
        for (var i = 0; i < BinaryPrimitives.ReadUInt16BigEndian(buf[6..]); i++)
        {
            var (name, next) = ReadName(buf, offset);
            var type = BinaryPrimitives.ReadUInt16BigEndian(buf[next..]);
            var ttl = BinaryPrimitives.ReadUInt32BigEndian(buf[(next + 4)..]);
            var length = BinaryPrimitives.ReadUInt16BigEndian(buf[(next + 8)..]);
            var rdata = next + 10;
            var data = type == A ? new IPAddress(buf.Slice(rdata, 4)).ToString() : ReadName(buf, rdata).Name;
            answers.Add(new Answer(name, type, ttl, data));
            offset = rdata + length;
        }
        return new Message(BinaryPrimitives.ReadUInt16BigEndian(buf), (flags & 0x0200) != 0, (flags & 0x0400) != 0, flags & 0xf, qname, qtype, answers);
    }

    /// <summary>Serves zone on 127.0.0.1 until the returned client is disposed.</summary>
    public static UdpClient Serve(IReadOnlyDictionary<string, List<Rec>> zone)
    {
        var server = new UdpClient(new IPEndPoint(IPAddress.Loopback, 0));
        _ = Task.Run(async () =>
        {
            while (true)
            {
                UdpReceiveResult received;
                try { received = await server.ReceiveAsync(); }
                catch (ObjectDisposedException) { return; }
                var buf = received.Buffer;
                var query = Parse(buf);
                var name = query.Question.ToLowerInvariant();
                var body = new List<byte>();
                var count = 0;
                void Add(string owner, Rec r)
                {
                    if (r.Type != query.QType && r.Type != CName) return;
                    byte[] rdata = r.Type == A ? IPAddress.Parse(r.Data).GetAddressBytes() : EncodeName(r.Data);
                    var ttl = new byte[4];
                    BinaryPrimitives.WriteUInt32BigEndian(ttl, r.Ttl);
                    body.AddRange([.. EncodeName(owner), .. U16(r.Type), .. U16(1), .. ttl, .. U16((ushort)rdata.Length), .. rdata]);
                    count++;
                }
                foreach (var r in zone.GetValueOrDefault(name) ?? [])
                {
                    Add(name, r);
                    if (r.Type == CName && query.QType != CName)
                        foreach (var target in zone.GetValueOrDefault(r.Data) ?? []) Add(r.Data, target);
                }
                var questionEnd = ReadName(buf, 12).End + 4; // exactly the question; anything after it (EDNS0) is dropped
                var truncated = questionEnd + body.Count > 512;
                var flags = (ushort)(0x8400 | (truncated ? 0x0200 : 0) | (zone.ContainsKey(name) ? 0 : 3));
                byte[] reply = [.. U16(query.Id), .. U16(flags), .. U16(1), .. U16((ushort)(truncated ? 0 : count)), 0, 0, 0, 0, .. buf[12..questionEnd], .. (truncated ? [] : body)];
                await server.SendAsync(reply, received.RemoteEndPoint);
            }
        });
        return server;
    }

    public static List<string> SearchCandidates(string name, int ndots, IEnumerable<string> search)
    {
        if (name.EndsWith('.')) return [name[..^1]];
        var expanded = search.Select(d => $"{name}.{d}").ToList();
        return name.Count(c => c == '.') >= ndots ? [name, .. expanded] : [.. expanded, name];
    }
}
```

```csharp
// Checks: the same results as every other language.
using System.Net;
using System.Net.Sockets;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

Check(Convert.ToHexStringLower(DnsWire.EncodeName("www.example.com")) == "03777777076578616d706c6503636f6d00", "name");
Check(DnsWire.BuildQuery(0xbeef, "example.com", DnsWire.A).Length == 29, "query length");

var zone = new Dictionary<string, List<Rec>>
{
    ["example.com"] = [new(DnsWire.A, 300, "93.184.216.34")],
    ["www.example.com"] = [new(DnsWire.CName, 3600, "example.com")],
    ["big.example.com"] = [.. Enumerable.Range(1, 40).Select(i => new Rec(DnsWire.A, 60, $"10.0.0.{i}"))],
};
using var server = DnsWire.Serve(zone);
var port = ((IPEndPoint)server.Client.LocalEndPoint!).Port;

async Task<Message> Ask(ushort id, string name)
{
    using var client = new UdpClient();
    await client.SendAsync(DnsWire.BuildQuery(id, name, DnsWire.A), new IPEndPoint(IPAddress.Loopback, port));
    using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(2));
    return DnsWire.Parse((await client.ReceiveAsync(timeout.Token)).Buffer);
}

var reply = await Ask(42, "www.example.com");
Check(reply.Id == 42 && reply.Authoritative, reply);
Check(reply.Answers.SequenceEqual([new Answer("www.example.com", DnsWire.CName, 3600, "example.com"), new Answer("example.com", DnsWire.A, 300, "93.184.216.34")]), string.Join(", ", reply.Answers));
Check((await Ask(43, "nope.example.com")).Rcode == 3, "NXDOMAIN");
var big = await Ask(7, "big.example.com");
Check(big.Truncated && big.Answers.Count == 0, "truncated");

string[] search = ["default.svc.cluster.local", "svc.cluster.local", "cluster.local"];
var candidates = DnsWire.SearchCandidates("api.example.com", 5, search);
Check(candidates.Count == 4 && candidates[^1] == "api.example.com", candidates.Count);
Check(DnsWire.SearchCandidates("api.example.com.", 5, search).SequenceEqual(["api.example.com"]), "trailing dot");
Console.WriteLine("all dns checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/10-dns-in-depth/labs/csharp). `python3 labs/run.py dns-in-depth/csharp`.

## Common pitfalls

1. **Native byte order on the wire.** Use the explicitly big-endian call.
2. **Reading Java bytes as numbers without `& 0xff`.** Anything above 127 comes out negative.
3. **Echoing more than the question.** Clients add EDNS0 records after it.
4. **Go's resolver without `PreferGo: true`.** The C library's resolver ignores your `Dial`.
5. **Expecting `getaddrinfo` (or .NET's `Dns`) to query a server you name.** They ask the operating system.

## Check your understanding

1. What does query ID 42 become if a little-endian machine writes its native bytes, and why does the client then never accept the reply?
2. Why did the lab's first server work with Node's resolver but not Go's?
3. In Java, `buf[offset]` is −56. What was the byte, and how do you read it correctly?
4. Which three of the six languages can point their standard resolver at a chosen server, and how?

<details>
<summary>Answers — after your attempt</summary>

1. 42 is `00 2a`; written little-endian it's `2a 00`, which a big-endian reader reads as 10,752. The server echoes 10,752, and the client, waiting for 42, discards the reply as someone else's.
2. Node's resolver sent only a question. Go's added an EDNS0 OPT record after it, and the server echoed that too while its header claimed no additional records, so the answers that followed started in the wrong place.
3. 200 (−56 + 256). Read it as `buf[offset] & 0xff`, which promotes it to an `int` and keeps only the low eight bits.
4. TypeScript (`Resolver.setServers`), Go (`net.Resolver` with `PreferGo` and a custom `Dial`), and Java (JNDI's `dns://host:port` provider URL).

</details>

## Practice — independent task

**Add `AAAA` support to your language's lab.**

1. Make the server answer type 28 (`AAAA`) with 16-byte IPv6 addresses, and the parser format them.
2. Add a test for `example.com` type `AAAA` returning `2606:2800:220:1:248:1893:25c8:1946`.
3. If your language's resolver can point at the server (Go, Java), also look the address up through it.

**Done when:** your test passes, and you can say how your language turns 16 bytes into the standard IPv6 text form.

## Before moving on

You can write network-byte-order fields in your language, run a UDP server and answer it, and say whether its standard resolver can query a server you choose.

**Recap.** DNS is the same bytes in every language: big-endian fields written with `struct`'s `!`, `binary.BigEndian`, `ByteBuffer`, `to_be_bytes` or `BinaryPrimitives`, and Java's signed bytes masked with `& 0xff`. A server must echo exactly the question, because real resolvers like Go's send EDNS0 records after it. Go's and Java's standard resolvers (and Node's) can query a server you name; Python's, Rust's and C#'s ask the operating system, so use a DNS library for that.

## Related

- [[networking/10-dns-in-depth/index|DNS in depth]]: the main lesson
- [[networking/11-http-evolution/in-other-languages|HTTP in other languages]]: the next layer up, in the same languages
- [[networking/09-sockets-and-the-network-api|Sockets and the network API]]: UDP and TCP sockets in depth
