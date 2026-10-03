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
