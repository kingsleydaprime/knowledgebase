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
