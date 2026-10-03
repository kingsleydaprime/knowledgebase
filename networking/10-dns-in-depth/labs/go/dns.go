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
