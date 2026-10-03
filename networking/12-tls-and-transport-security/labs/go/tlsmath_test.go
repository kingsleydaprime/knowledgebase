package tlsmath

import (
	"bytes"
	"crypto/tls"
	"crypto/x509"
	"errors"
	"math/big"
	"os"
	"os/exec"
	"path/filepath"
	"testing"
)

func n(x int64) *big.Int { return big.NewInt(x) }

func TestDiffieHellmanByHand(t *testing.T) {
	p, g := n(23), n(5)
	A, _ := ModPow(g, n(6), p)
	B, _ := ModPow(g, n(15), p)
	if A.Int64() != 8 || B.Int64() != 19 {
		t.Fatalf("public values %v %v, want 8 19", A, B)
	}
	alice, bob := new(big.Int).Exp(B, n(6), p), new(big.Int).Exp(A, n(15), p) // big.Int's Exp agrees
	if alice.Int64() != 2 || bob.Int64() != 2 {
		t.Fatalf("shared %v %v, want 2 2", alice, bob)
	}
}

func TestEasyForwardsHardBackwards(t *testing.T) {
	value, multiplications := ModPow(n(3), n(54_321), n(65_537))
	if value.Int64() != 21_002 || multiplications != 23 {
		t.Fatalf("got %v in %d multiplications, want 21002 in 23", value, multiplications)
	}
	x, steps, err := DiscreteLog(3, 21_002, 65_537)
	if err != nil || x != 54_321 || steps != 54_321 {
		t.Fatalf("discrete log %d in %d steps (%v), want 54321 in 54321", x, steps, err)
	}
	p := new(big.Int).Sub(new(big.Int).Lsh(n(1), 255), n(19)) // 2^255 - 19, Curve25519's prime
	if _, m := ModPow(n(5), new(big.Int).Sub(p, n(2)), p); m != 508 {
		t.Fatalf("%d multiplications for a 255-bit exponent, want 508", m)
	}
}

func TestRSASignatureByHand(t *testing.T) {
	d := ModInverse(17, 60*52)
	if d != 2753 {
		t.Fatalf("d = %d, want 2753", d)
	}
	signature := new(big.Int).Exp(n(65), n(d), n(61*53))
	back := new(big.Int).Exp(signature, n(17), n(3233))
	if signature.Int64() != 588 || back.Int64() != 65 {
		t.Fatalf("signature %v verifies to %v, want 588 and 65", signature, back)
	}
}

func TestX25519HKDFAESGCM(t *testing.T) {
	client, _ := KeyPair()
	server, _ := KeyPair()
	secret, _ := client.ECDH(server.PublicKey())
	other, _ := server.ECDH(client.PublicKey())
	if !bytes.Equal(secret, other) || len(client.PublicKey().Bytes()) != 32 {
		t.Fatal("both sides must compute the same secret from 32-byte public keys")
	}
	transcript := []byte("hash of every handshake message so far")
	c2s, _ := DeriveKey(secret, "c ap traffic", transcript)
	s2c, _ := DeriveKey(secret, "s ap traffic", transcript)
	if bytes.Equal(c2s, s2c) {
		t.Fatal("each direction needs its own key")
	}
	nonce, header := bytes.Repeat([]byte{1}, 12), []byte{23, 3, 3, 0, 40}
	sealed, _ := Seal(c2s, nonce, []byte("GET / HTTP/1.1"), header)
	if opened, err := Open(c2s, nonce, sealed, header); err != nil || string(opened) != "GET / HTTP/1.1" {
		t.Fatalf("opened %q, %v", opened, err)
	}
	tampered := bytes.Clone(sealed)
	tampered[0] ^= 1
	if _, err := Open(c2s, nonce, tampered, header); err == nil {
		t.Fatal("a flipped bit must fail the tag check")
	}
}

// certs makes the lab CA and certificates with the shared script, in a folder the test cleans up.
func certs(t *testing.T) string {
	dir := t.TempDir()
	if out, err := exec.Command("sh", "../shared/make-certs.sh", dir).CombinedOutput(); err != nil {
		t.Fatalf("make-certs: %v\n%s", err, out)
	}
	return dir
}

// handshake serves one TLS connection with certFile and connects to it as a client that trusts the lab CA if
// trustCA is set. It returns what the client saw, or the verification error.
func handshake(t *testing.T, dir, certFile, serverName string, trustCA bool) (tls.ConnectionState, error) {
	cert, err := tls.LoadX509KeyPair(filepath.Join(dir, certFile), filepath.Join(dir, "shop.key"))
	if err != nil {
		t.Fatal(err)
	}
	listener, err := tls.Listen("tcp", "127.0.0.1:0", &tls.Config{Certificates: []tls.Certificate{cert}, NextProtos: []string{"h2", "http/1.1"}})
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()
	done := make(chan struct{})
	go func() {
		defer close(done)
		if conn, err := listener.Accept(); err == nil {
			_ = conn.(*tls.Conn).Handshake() // fails when the client rejects the certificate, which is the point
			conn.Close()
		}
	}()
	defer func() { <-done }()

	config := &tls.Config{ServerName: serverName, NextProtos: []string{"h2", "http/1.1"}}
	if trustCA {
		pem, _ := os.ReadFile(filepath.Join(dir, "ca.crt"))
		config.RootCAs = x509.NewCertPool()
		config.RootCAs.AppendCertsFromPEM(pem)
	} else {
		config.RootCAs = x509.NewCertPool() // trusts nothing, so the test doesn't depend on the machine's store
	}
	conn, err := tls.Dial("tcp", listener.Addr().String(), config)
	if err != nil {
		return tls.ConnectionState{}, err
	}
	defer conn.Close()
	return conn.ConnectionState(), nil
}

func TestARealTLS13Handshake(t *testing.T) {
	state, err := handshake(t, certs(t), "shop.crt", "shop.test", true)
	if err != nil {
		t.Fatal(err)
	}
	got := []string{tls.VersionName(state.Version), tls.CipherSuiteName(state.CipherSuite), state.CurveID.String(), state.NegotiatedProtocol}
	want := []string{"TLS 1.3", "TLS_AES_128_GCM_SHA256", "X25519MLKEM768", "h2"}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("got %v, want %v", got, want)
		}
	}
}

func TestTheThreeChecksEachFailingOnItsOwn(t *testing.T) {
	dir := certs(t)
	var hostname x509.HostnameError
	if _, err := handshake(t, dir, "shop.crt", "evil.test", true); !errors.As(err, &hostname) {
		t.Errorf("wrong name: got %v, want a HostnameError", err)
	}
	var unknown x509.UnknownAuthorityError
	if _, err := handshake(t, dir, "shop.crt", "shop.test", false); !errors.As(err, &unknown) {
		t.Errorf("untrusted CA: got %v, want an UnknownAuthorityError", err)
	}
	var invalid x509.CertificateInvalidError
	if _, err := handshake(t, dir, "expired.crt", "shop.test", true); !errors.As(err, &invalid) || invalid.Reason != x509.Expired {
		t.Errorf("expired: got %v, want CertificateInvalidError with Reason Expired", err)
	}
}
