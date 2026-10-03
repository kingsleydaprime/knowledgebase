# TLS and Transport Security in Other Languages

**[Intermediate]** — A companion to [[networking/12-tls-and-transport-security/index|TLS and transport security]], which works the maths of TLS by hand (Diffie-Hellman, the discrete logarithm, an RSA signature), then uses the real primitives (X25519, HKDF, AES-GCM), then runs a real TLS 1.3 handshake and breaks each of the three certificate checks. This page does the same in Python, Go, Java, Rust and C#. The maths is identical everywhere, and so are the numbers. What differs is how much cryptography each standard library carries: Go's has all of it, Java's and C#'s have most of it, Python's has TLS but not the primitives underneath, and Rust's has none.

## Before you start

You can already:

- Work Diffie-Hellman with small numbers, and say what HKDF and AES-GCM are for → [[networking/12-tls-and-transport-security/index|the main lesson]], section 7.
- Explain the three checks a client makes on a certificate: the name, the chain to a trusted CA, and the dates.
- Open a TCP connection in at least one of the languages here.

After this lesson you will be able to:

1. Say where your language gets its big-number arithmetic, its key exchange, its HKDF and its AES-GCM, and which TLS library it uses.
2. Make a TLS client trust a private CA without turning verification off.
3. Recognise each language's error for a wrong name, an untrusted CA and an expired certificate.

## The kid version

Five children learn the same secret handshake. One was given the whole kit at birth: the lock, the key-cutter and the sealing wax. Two got most of it and had to make one small tool themselves. One got the door but none of the tools behind it, so it borrows them from a neighbour. And one got nothing and fetches every piece from a shop. When they meet, the handshake is the same, because the handshake is a set of rules, not a kit.

**Where the analogy stops working.** A home-made tool for a children's game is harmless. A home-made cipher isn't: the Java lab writes HKDF by hand because it's a dozen lines of HMAC and can be checked against the published test vector, but the arithmetic inside X25519 or AES must come from a vetted library, because a version that gives the right answers can still leak its key through timing.

## 1. The tools, by ecosystem

| Language | Big numbers | Key exchange | HKDF | AES-GCM | TLS |
|---|---|---|---|---|---|
| TypeScript | `bigint` | `crypto.diffieHellman` (X25519) | `crypto.hkdfSync` | `crypto.createCipheriv` | `node:tls` (OpenSSL) |
| Python | `int`, unlimited | `cryptography` package | `cryptography` package | `cryptography` package | `ssl` (OpenSSL) |
| Go | `math/big` | `crypto/ecdh` (X25519) | `crypto/hkdf` (Go 1.24+) | `crypto/cipher` | `crypto/tls`, written in Go |
| Java | `BigInteger` | `KeyAgreement "XDH"` (X25519) | none until Java 25; by hand here | `Cipher "AES/GCM/NoPadding"` | JSSE (`SSLSocket`), written in Java |
| Rust | `num-bigint` crate | `x25519-dalek` crate | `hkdf` crate | `aes-gcm` crate | `rustls` crate |
| C# | `System.Numerics.BigInteger` | `ECDiffieHellman` (P-256 on Linux) | `HKDF` | `AesGcm` | `SslStream` (OpenSSL on Linux) |

C would call OpenSSL directly (`EVP_PKEY_derive`, `EVP_KDF`, `SSL_connect`), which is what Python, Node and .NET on Linux do underneath; no lab here.

## 2. What changes between languages

### Who does the TLS: OpenSSL, or the language itself

Python's `ssl`, Node's `tls` and .NET's `SslStream` on Linux all hand the protocol to the system's OpenSSL. So their cipher choice, their error wording and whether they offer the post-quantum hybrid group depend on the OpenSSL version installed, not on the language. Go's `crypto/tls`, Java's JSSE and Rust's `rustls` implement TLS themselves, so they behave the same on every machine. You can see it in the results:

- **Cipher suite.** OpenSSL, Java and rustls pick `TLS_AES_256_GCM_SHA384`. Go picks `TLS_AES_128_GCM_SHA256`: in TLS 1.3 its order isn't configurable, and it puts AES-128 first when the processor has AES instructions. Both are safe.
- **Key exchange group.** Go (1.24+), rustls and OpenSSL 3.5+ send `X25519MLKEM768`, X25519 combined with the post-quantum ML-KEM. Java 21 offers plain X25519. The C# lab's container ships an older OpenSSL, so .NET there offers plain X25519 too, and .NET 10's `MLKem` class reports itself unsupported.

### Trusting a private CA, without switching checks off

Every lab trusts the lab's CA for the "good" handshake and leaves it out for the "untrusted" one. The right way is to give the client a trust store that contains the CA; the wrong way, which every language also allows, is to turn verification off.

- **Python:** `ssl.create_default_context(cafile="ca.crt")`.
- **Go:** an `x509.CertPool` with `AppendCertsFromPEM`, set as `tls.Config.RootCAs`.
- **Java:** a `KeyStore` with the CA as a certificate entry, into a `TrustManagerFactory`, into an `SSLContext`.
- **Rust:** a `RootCertStore` with the CA added.
- **C#:** `X509ChainPolicy` with `TrustMode = CustomRootTrust` and the CA in `CustomTrustStore`.

### The name check isn't always on

Go, Rust, Python's default context, Node and .NET check the hostname by default. **Java's raw `SSLSocket` doesn't**: it checks the chain and the dates, and accepts a certificate for any name unless you set `setEndpointIdentificationAlgorithm("HTTPS")`. (`HttpClient` turns it on for you.) Without that one line, the lab's `evil.test` connection succeeds.

### Revocation: .NET asks, the others don't

.NET checks whether a certificate has been revoked by default, and the lab's CA publishes no revocation list, so the first run failed with `RevocationStatusUnknown`. The C# lab turns revocation checking off for this private CA, with a comment. The other languages don't check revocation unless you ask. Browsers mostly don't ask either: they rely on revocation lists their vendor pushes to them.

### No X25519 in .NET

.NET's `ECDiffieHellman` supports the NIST curves everywhere but not Curve25519 on Linux, so the C# lab exchanges keys on P-256, the other group TLS 1.3 clients offer. The maths is the same idea on a different curve; the 32-byte shared secret feeds HKDF exactly as before.

### Why the maths is the same everywhere

Every lab counts square-and-multiply's multiplications and gets 23 for a 16-bit exponent and 508 for a 255-bit one; every lab inverts 17 modulo 3120 and gets 2753. These numbers don't depend on the language, which is the point: the maths is a fact about numbers, and the code only has to get it right. C# has no modular inverse in `BigInteger`, so its lab writes the extended Euclidean algorithm; the rest use the built-in (`pow(a, -1, m)`, `ModInverse`, `modInverse`, `modinv`).

## 3. The same results, in every language

| Check | Expected in every language |
|---|---|
| Diffie-Hellman, p = 23, g = 5, secrets 6 and 15 | public values 8 and 19; both sides reach 2 |
| 3^54321 mod 65537 | 21002, in 23 multiplications |
| the discrete log of 21002 | 54321, in 54,321 tries |
| a 255-bit exponent | 508 multiplications |
| RSA with n = 61 × 53, e = 17 | d = 2753; the signature of 65 is 588, and 588^17 mod 3233 is 65 |
| key exchange, HKDF, AES-GCM | the same 32-byte secret on both sides; different keys per direction; one flipped bit fails the tag |
| a real handshake | TLS 1.3, ALPN `h2` |
| wrong name / CA not trusted / expired | three different errors, one per check |

## Terms used in this lesson

1. **Trust store**: This is the set of CA certificates a client accepts as the end of a certificate chain.
2. **Keystore**: In Java, this is a file or object holding keys and certificates; the server's own certificate and private key go in one, often a PKCS#12 file.
3. **PKCS#12**: This is a file format that bundles a private key with its certificate chain, protected by a password, usually with the extension `.p12` or `.pfx`.
4. **Endpoint identification**: In Java, this is the hostname check, which compares the name you connected to with the names in the certificate.
5. **Revocation**: This is a CA withdrawing a certificate before it expires, published in a revocation list or answered by an online responder.
6. **Test vector**: This is a published input and its correct output, used to check that an implementation of an algorithm is right.

## 4. The certificates, made once for every language

Every lab except TypeScript makes its certificates with one script, so they all test exactly the same files. It writes a CA, a certificate for `shop.test`, the same certificate dated January 2020, and PKCS#12 copies for Java. The CA certificate carries `basicConstraints` and `keyUsage`, and the server certificate carries `keyUsage`, `extendedKeyUsage` and key identifiers. Strict verifiers reject certificates without them: Python 3.13's default context refused the first version of this script with "CA cert does not include key usage extension".

```sh
#!/bin/sh
# Makes a small certificate authority and certificates for shop.test in the folder given (created if missing):
#   ca.crt ca.key        the lab's root CA
#   shop.crt shop.key    a current certificate for shop.test, signed by the CA
#   expired.crt          the same key and name, valid only in January 2020
#   shop.p12 expired.p12 each certificate with its key as a PKCS#12 keystore (password "lab"), for Java
# Needs OpenSSL 3.4 or later (for -not_before and -not_after). Usage: sh make-certs.sh <folder>
set -eu
dir=$1
mkdir -p "$dir"
cd "$dir"
ec="-newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes"
# A CA certificate must say what it may do: strict verifiers (Python 3.13+'s default) reject one without keyUsage.
openssl req -x509 $ec -keyout ca.key -out ca.crt -subj "/CN=Lab Root CA" -days 1 \
    -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign" 2>/dev/null
openssl req $ec -keyout shop.key -out shop.csr -subj "/CN=shop.test" 2>/dev/null
cat > san.cnf <<'EXT'
subjectAltName=DNS:shop.test
keyUsage=critical,digitalSignature
extendedKeyUsage=serverAuth
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid
EXT
openssl x509 -req -in shop.csr -CA ca.crt -CAkey ca.key -extfile san.cnf -out shop.crt -days 1 2>/dev/null
openssl x509 -req -in shop.csr -CA ca.crt -CAkey ca.key -extfile san.cnf -out expired.crt \
    -not_before 20200101000000Z -not_after 20200102000000Z 2>/dev/null
openssl pkcs12 -export -in shop.crt -inkey shop.key -out shop.p12 -passout pass:lab -name shop
openssl pkcs12 -export -in expired.crt -inkey shop.key -out expired.p12 -passout pass:lab -name shop
```

## 5. Python

Python's integers have no size limit, so the maths needs nothing. The standard library has `ssl` but none of the primitives underneath, so X25519, HKDF and AES-GCM come from the `cryptography` package, which wraps OpenSSL. The handshake errors come from `err.verify_message`, OpenSSL's own wording.

```python
"""The maths under TLS by hand with Python's unlimited integers, then the real primitives from the `cryptography`
package (the standard library has no X25519, HKDF or AES-GCM), and a real TLS 1.3 handshake with the ssl module."""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def mod_pow(base: int, exp: int, m: int) -> tuple[int, int]:
    """Square-and-multiply, counting multiplications. Python's built-in pow(base, exp, m) does the same, faster."""
    result, b, multiplications = 1, base % m, 0
    while exp > 0:
        if exp & 1:
            result = result * b % m
            multiplications += 1
        b = b * b % m
        multiplications += 1
        exp >>= 1
    return result, multiplications


def discrete_log(g: int, target: int, p: int) -> tuple[int, int]:
    value = 1
    for x in range(1, p):
        value = value * g % p
        if value == target:
            return x, x  # the exponent, and the steps it took: one per exponent tried
    raise ValueError("no solution")


def mod_inverse(a: int, m: int) -> int:
    return pow(a, -1, m)  # Python 3.8+: pow with exponent -1 is the modular inverse (extended Euclid inside)


def derive_key(secret: bytes, label: str, transcript_hash: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=transcript_hash, info=label.encode()).derive(secret)


def seal(key: bytes, nonce: bytes, plaintext: bytes, associated: bytes) -> bytes:
    return AESGCM(key).encrypt(nonce, plaintext, associated)  # the 16-byte tag is appended to the ciphertext


def open_sealed(key: bytes, nonce: bytes, sealed: bytes, associated: bytes) -> bytes:
    return AESGCM(key).decrypt(nonce, sealed, associated)  # raises InvalidTag if anything was changed


def key_pair() -> X25519PrivateKey:
    return X25519PrivateKey.generate()
```

```python
import pathlib
import socket
import ssl
import subprocess
import tempfile
import threading
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tlsmath import derive_key, discrete_log, key_pair, mod_inverse, mod_pow, open_sealed, seal

LABS = pathlib.Path(__file__).resolve().parent.parent


class Maths(unittest.TestCase):
    def test_diffie_hellman_by_hand(self):
        p, g, a, b = 23, 5, 6, 15
        A, B = mod_pow(g, a, p)[0], mod_pow(g, b, p)[0]
        self.assertEqual((A, B), (8, 19))
        self.assertEqual((pow(B, a, p), pow(A, b, p)), (2, 2))  # the built-in three-argument pow agrees

    def test_easy_forwards_hard_backwards(self):
        self.assertEqual(mod_pow(3, 54_321, 65_537), (21_002, 23))
        self.assertEqual(discrete_log(3, 21_002, 65_537), (54_321, 54_321))
        self.assertEqual(mod_pow(5, 2**255 - 21, 2**255 - 19)[1], 508)  # Python's ints have no size limit

    def test_rsa_signature_by_hand(self):
        n, e = 61 * 53, 17
        d = mod_inverse(e, 60 * 52)
        self.assertEqual((n, d), (3233, 2753))
        signature = pow(65, d, n)
        self.assertEqual((signature, pow(signature, e, n)), (588, 65))

    def test_x25519_hkdf_aes_gcm(self):
        client, server = key_pair(), key_pair()
        secret = client.exchange(server.public_key())
        self.assertEqual(secret, server.exchange(client.public_key()))
        self.assertEqual(len(client.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)), 32)
        transcript = b"hash of every handshake message so far"
        c2s, s2c = derive_key(secret, "c ap traffic", transcript), derive_key(secret, "s ap traffic", transcript)
        self.assertNotEqual(c2s, s2c)
        nonce, header = bytes([1] * 12), bytes([23, 3, 3, 0, 40])
        sealed = seal(c2s, nonce, b"GET / HTTP/1.1", header)
        self.assertEqual(open_sealed(c2s, nonce, sealed, header), b"GET / HTTP/1.1")
        tampered = bytes([sealed[0] ^ 1]) + sealed[1:]
        with self.assertRaises(InvalidTag):
            open_sealed(c2s, nonce, tampered, header)


class Handshake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.certs = pathlib.Path(cls.tmp.name)
        subprocess.run(["sh", str(LABS / "shared" / "make-certs.sh"), str(cls.certs)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def handshake(self, cert: str, server_name: str, trust_ca: bool):
        """Serves one TLS connection with `cert` and connects to it; returns what the client saw, or the error."""
        server_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        server_ctx.load_cert_chain(self.certs / cert, self.certs / "shop.key")
        server_ctx.set_alpn_protocols(["h2", "http/1.1"])
        listener = socket.create_server(("127.0.0.1", 0))
        port = listener.getsockname()[1]

        def serve():
            conn, _ = listener.accept()
            try:
                with server_ctx.wrap_socket(conn, server_side=True):
                    pass
            except (ssl.SSLError, OSError):
                pass  # the client may hang up after rejecting the certificate

        thread = threading.Thread(target=serve)
        thread.start()
        client_ctx = ssl.create_default_context(cafile=self.certs / "ca.crt" if trust_ca else None)
        client_ctx.set_alpn_protocols(["h2", "http/1.1"])
        try:
            with socket.create_connection(("127.0.0.1", port)) as raw, client_ctx.wrap_socket(raw, server_hostname=server_name) as tls:
                return {"version": tls.version(), "cipher": tls.cipher()[0], "alpn": tls.selected_alpn_protocol()}
        except ssl.SSLCertVerificationError as err:
            return {"error": err.verify_message}
        finally:
            thread.join()
            listener.close()

    def test_a_real_tls_13_handshake(self):
        result = self.handshake("shop.crt", "shop.test", True)
        self.assertEqual(result, {"version": "TLSv1.3", "cipher": "TLS_AES_256_GCM_SHA384", "alpn": "h2"})

    def test_the_three_checks_each_failing_on_its_own(self):
        self.assertIn("Hostname mismatch", self.handshake("shop.crt", "evil.test", True)["error"])
        self.assertEqual(self.handshake("shop.crt", "shop.test", False)["error"], "unable to get local issuer certificate")
        self.assertEqual(self.handshake("expired.crt", "shop.test", True)["error"], "certificate has expired")


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/12-tls-and-transport-security/labs/python). `python3 labs/run.py tls-and-transport-security/python`.

## 6. Go

Everything is in the standard library: `math/big`, `crypto/ecdh`, `crypto/hkdf`, `crypto/cipher` and `crypto/tls`. The handshake test reads `ConnectionState`, including `CurveID`, so it can assert the post-quantum hybrid group. Each failure is a typed error, unwrapped with `errors.As`: `x509.HostnameError`, `x509.UnknownAuthorityError`, and `x509.CertificateInvalidError` with `Reason` set to `x509.Expired`.

```go
// Package tlsmath does the maths under TLS by hand with math/big, then uses the real primitives Go ships in its
// standard library: X25519 (crypto/ecdh), HKDF (crypto/hkdf) and AES-GCM (crypto/cipher). The handshake itself is
// crypto/tls, exercised in the tests.
package tlsmath

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdh"
	"crypto/hkdf"
	"crypto/rand"
	"crypto/sha256"
	"errors"
	"math/big"
)

// ModPow is square-and-multiply, counting multiplications. big.Int's Exp does the same, faster.
func ModPow(base, exp, m *big.Int) (*big.Int, int) {
	result, b, e := big.NewInt(1), new(big.Int).Mod(base, m), new(big.Int).Set(exp)
	multiplications := 0
	for e.Sign() > 0 {
		if e.Bit(0) == 1 {
			result.Mod(result.Mul(result, b), m)
			multiplications++
		}
		b.Mod(b.Mul(b, b), m)
		multiplications++
		e.Rsh(e, 1)
	}
	return result, multiplications
}

// DiscreteLog finds x with g^x = target (mod p) the only general way: trying every exponent. It returns x and the
// steps taken, one per exponent tried.
func DiscreteLog(g, target, p int64) (int64, int64, error) {
	value := int64(1)
	for x := int64(1); x < p; x++ {
		value = value * g % p
		if value == target {
			return x, x, nil
		}
	}
	return 0, 0, errors.New("no solution")
}

// ModInverse is the d with a·d = 1 (mod m), found by the extended Euclidean algorithm inside big.Int.
func ModInverse(a, m int64) int64 {
	return new(big.Int).ModInverse(big.NewInt(a), big.NewInt(m)).Int64()
}

// KeyPair makes an X25519 key pair: a random 32-byte private key and the point it gives on Curve25519.
func KeyPair() (*ecdh.PrivateKey, error) {
	return ecdh.X25519().GenerateKey(rand.Reader)
}

// DeriveKey stretches the shared secret into a 32-byte key for one purpose, bound to the handshake so far.
func DeriveKey(secret []byte, label string, transcriptHash []byte) ([]byte, error) {
	return hkdf.Key(sha256.New, secret, transcriptHash, label, 32)
}

func gcm(key []byte) (cipher.AEAD, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}
	return cipher.NewGCM(block)
}

// Seal encrypts and authenticates plaintext; the 16-byte tag is appended to the ciphertext.
func Seal(key, nonce, plaintext, associated []byte) ([]byte, error) {
	aead, err := gcm(key)
	if err != nil {
		return nil, err
	}
	return aead.Seal(nil, nonce, plaintext, associated), nil
}

// Open checks the tag and decrypts; it fails if a single bit of the ciphertext or associated data changed.
func Open(key, nonce, sealed, associated []byte) ([]byte, error) {
	aead, err := gcm(key)
	if err != nil {
		return nil, err
	}
	return aead.Open(nil, nonce, sealed, associated)
}
```

```go
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
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/12-tls-and-transport-security/labs/go). `python3 labs/run.py tls-and-transport-security/go`.

## 7. Java

`BigInteger` has `modPow` and `modInverse`; the JDK has X25519 and AES-GCM. Java 21 has no HKDF class, so the lab writes it from HMAC-SHA256 and checks it against the first test vector in RFC 5869. The handshake uses `SSLServerSocket` and `SSLSocket`, with the server's key and certificate from a PKCS#12 keystore. Note `setEndpointIdentificationAlgorithm("HTTPS")`: without it, the wrong-name check never runs.

```java
package tls;

import java.math.BigInteger;
import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PrivateKey;
import java.security.PublicKey;
import javax.crypto.Cipher;
import javax.crypto.KeyAgreement;
import javax.crypto.Mac;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * The maths under TLS by hand with BigInteger, then the real primitives from the JDK: X25519 (KeyPairGenerator "X25519"
 * and KeyAgreement "XDH") and AES-GCM. Java 21 has no HKDF class (it arrives in Java 25 as javax.crypto.KDF), so HKDF
 * is written here from HMAC-SHA256 in a dozen lines, which is all it is.
 */
public final class TlsMath {
    private TlsMath() {}

    /** Square-and-multiply, counting multiplications. BigInteger's modPow does the same, faster. */
    public record Power(BigInteger value, int multiplications) {}

    public static Power modPow(BigInteger base, BigInteger exp, BigInteger m) {
        BigInteger result = BigInteger.ONE, b = base.mod(m);
        int multiplications = 0;
        for (int i = 0; i < exp.bitLength(); i++) {
            if (exp.testBit(i)) {
                result = result.multiply(b).mod(m);
                multiplications++;
            }
            b = b.multiply(b).mod(m);
            multiplications++;
        }
        return new Power(result, multiplications);
    }

    /** Finds x with g^x = target (mod p) the only general way, trying every exponent; the steps taken equal x. */
    public static long discreteLog(long g, long target, long p) {
        long value = 1;
        for (long x = 1; x < p; x++) {
            value = value * g % p;
            if (value == target) return x;
        }
        throw new ArithmeticException("no solution");
    }

    public static KeyPair keyPair() throws GeneralSecurityException {
        return KeyPairGenerator.getInstance("X25519").generateKeyPair();
    }

    public static byte[] sharedSecret(PrivateKey mine, PublicKey theirs) throws GeneralSecurityException {
        var agreement = KeyAgreement.getInstance("XDH");
        agreement.init(mine);
        agreement.doPhase(theirs, true);
        return agreement.generateSecret();
    }

    /** HKDF (RFC 5869): extract a fixed-size key from the secret, then expand it into as many bytes as asked for. */
    public static byte[] hkdf(byte[] secret, byte[] salt, byte[] info, int length) throws GeneralSecurityException {
        var mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(salt.length == 0 ? new byte[32] : salt, "HmacSHA256"));
        byte[] prk = mac.doFinal(secret); // extract: PRK = HMAC(salt, secret)
        mac.init(new SecretKeySpec(prk, "HmacSHA256"));
        byte[] out = new byte[length], block = new byte[0];
        for (int i = 0, done = 0; done < length; i++) { // expand: T(i) = HMAC(PRK, T(i-1) | info | i)
            mac.update(block);
            mac.update(info);
            mac.update((byte) (i + 1));
            block = mac.doFinal();
            int n = Math.min(block.length, length - done);
            System.arraycopy(block, 0, out, done, n);
            done += n;
        }
        return out;
    }

    public static byte[] deriveKey(byte[] secret, String label, byte[] transcriptHash) throws GeneralSecurityException {
        return hkdf(secret, transcriptHash, label.getBytes(java.nio.charset.StandardCharsets.US_ASCII), 32);
    }

    private static byte[] gcm(int mode, byte[] key, byte[] nonce, byte[] input, byte[] associated) throws GeneralSecurityException {
        var cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(mode, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
        cipher.updateAAD(associated);
        return cipher.doFinal(input);
    }

    /** Encrypts and authenticates; the 16-byte tag is appended to the ciphertext. */
    public static byte[] seal(byte[] key, byte[] nonce, byte[] plaintext, byte[] associated) throws GeneralSecurityException {
        return gcm(Cipher.ENCRYPT_MODE, key, nonce, plaintext, associated);
    }

    /** Checks the tag and decrypts; throws AEADBadTagException if anything changed. */
    public static byte[] open(byte[] key, byte[] nonce, byte[] sealed, byte[] associated) throws GeneralSecurityException {
        return gcm(Cipher.DECRYPT_MODE, key, nonce, sealed, associated);
    }
}
```

```java
package tls;

import java.io.FileInputStream;
import java.math.BigInteger;
import java.net.InetAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.KeyStore;
import java.security.cert.CertificateExpiredException;
import java.security.cert.CertificateFactory;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import javax.crypto.AEADBadTagException;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLHandshakeException;
import javax.net.ssl.SSLServerSocket;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.TrustManagerFactory;

/** The same checks as every other language. Run with -ea and the certificate folder as the argument. */
public final class TlsCheck {
    private TlsCheck() {}

    static BigInteger n(long x) {
        return BigInteger.valueOf(x);
    }

    public static void main(String[] args) throws Exception {
        // Diffie-Hellman by hand: both sides reach 2 without ever sending it.
        var p = n(23);
        var a = TlsMath.modPow(n(5), n(6), p).value();
        var b = TlsMath.modPow(n(5), n(15), p).value();
        assert a.equals(n(8)) && b.equals(n(19)) : a + " " + b;
        assert b.modPow(n(6), p).equals(n(2)) && a.modPow(n(15), p).equals(n(2)); // BigInteger's modPow agrees

        // Easy forwards (23 multiplications), hard backwards (54,321 tries).
        assert TlsMath.modPow(n(3), n(54_321), n(65_537)).equals(new TlsMath.Power(n(21_002), 23));
        assert TlsMath.discreteLog(3, 21_002, 65_537) == 54_321;
        var curvePrime = BigInteger.TWO.pow(255).subtract(n(19));
        assert TlsMath.modPow(n(5), curvePrime.subtract(n(2)), curvePrime).multiplications() == 508;

        // An RSA signature by hand: d is the inverse of e, and only its owner can make 588 from 65.
        var d = n(17).modInverse(n(60 * 52));
        assert d.equals(n(2753));
        var signature = n(65).modPow(d, n(3233));
        assert signature.equals(n(588)) && signature.modPow(n(17), n(3233)).equals(n(65));

        // The hand-written HKDF matches the first test vector in RFC 5869.
        var hex = HexFormat.of();
        byte[] okm = TlsMath.hkdf(hex.parseHex("0b".repeat(22)), hex.parseHex("000102030405060708090a0b0c"), hex.parseHex("f0f1f2f3f4f5f6f7f8f9"), 42);
        assert hex.formatHex(okm).equals("3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865");

        // X25519, then HKDF, then AES-GCM: the real pieces of a TLS 1.3 connection.
        var client = TlsMath.keyPair();
        var server = TlsMath.keyPair();
        byte[] secret = TlsMath.sharedSecret(client.getPrivate(), server.getPublic());
        assert Arrays.equals(secret, TlsMath.sharedSecret(server.getPrivate(), client.getPublic())) && secret.length == 32;
        byte[] transcript = "hash of every handshake message so far".getBytes(StandardCharsets.US_ASCII);
        byte[] c2s = TlsMath.deriveKey(secret, "c ap traffic", transcript);
        assert !Arrays.equals(c2s, TlsMath.deriveKey(secret, "s ap traffic", transcript));
        byte[] nonce = new byte[12];
        Arrays.fill(nonce, (byte) 1);
        byte[] header = {23, 3, 3, 0, 40};
        byte[] sealed = TlsMath.seal(c2s, nonce, "GET / HTTP/1.1".getBytes(StandardCharsets.US_ASCII), header);
        assert new String(TlsMath.open(c2s, nonce, sealed, header), StandardCharsets.US_ASCII).equals("GET / HTTP/1.1");
        sealed[0] ^= 1;
        try {
            TlsMath.open(c2s, nonce, sealed, header);
            throw new AssertionError("a flipped bit must fail the tag check");
        } catch (AEADBadTagException expected) {
            // the tag no longer matches
        }

        // A real TLS 1.3 handshake, then the three checks failing one at a time.
        Path certs = Path.of(args[0]);
        assert handshake(certs, "shop.p12", "shop.test", true).equals("TLSv1.3 TLS_AES_256_GCM_SHA384 h2");
        assert handshake(certs, "shop.p12", "evil.test", true).contains("No subject alternative DNS name matching evil.test");
        assert handshake(certs, "shop.p12", "shop.test", false).contains("unable to find valid certification path");
        assert handshake(certs, "expired.p12", "shop.test", true).equals(CertificateExpiredException.class.getName());
        System.out.println("all checks passed");
    }

    /**
     * Serves one TLS connection from the keystore `serverStore` and connects to it as shop.test's client would. Returns
     * "version cipher alpn", or what the handshake failure says.
     */
    static String handshake(Path certs, String serverStore, String serverName, boolean trustLabCa) throws Exception {
        var keys = KeyStore.getInstance("PKCS12");
        try (var in = new FileInputStream(certs.resolve(serverStore).toFile())) {
            keys.load(in, "lab".toCharArray());
        }
        var keyManagers = KeyManagerFactory.getInstance("PKIX");
        keyManagers.init(keys, "lab".toCharArray());
        var serverContext = SSLContext.getInstance("TLS");
        serverContext.init(keyManagers.getKeyManagers(), null, null);

        var clientContext = SSLContext.getInstance("TLS");
        if (trustLabCa) {
            var trusted = KeyStore.getInstance("PKCS12");
            trusted.load(null, null);
            try (var in = new FileInputStream(certs.resolve("ca.crt").toFile())) {
                trusted.setCertificateEntry("lab", CertificateFactory.getInstance("X.509").generateCertificate(in));
            }
            var trustManagers = TrustManagerFactory.getInstance("PKIX");
            trustManagers.init(trusted);
            clientContext.init(null, trustManagers.getTrustManagers(), null);
        } else {
            clientContext.init(null, null, null); // the JDK's own trust store, which has never heard of the lab CA
        }

        try (var listener = (SSLServerSocket) serverContext.getServerSocketFactory().createServerSocket(0, 1, InetAddress.getLoopbackAddress())) {
            var params = listener.getSSLParameters();
            params.setApplicationProtocols(new String[] {"h2", "http/1.1"});
            listener.setSSLParameters(params);
            var serving = Thread.ofVirtual().start(() -> {
                try (var conn = (SSLSocket) listener.accept()) {
                    conn.startHandshake();
                } catch (Exception rejected) {
                    // the client hangs up when it rejects the certificate
                }
            });
            try (var raw = new Socket(InetAddress.getLoopbackAddress(), listener.getLocalPort());
                    var tls = (SSLSocket) clientContext.getSocketFactory().createSocket(raw, serverName, raw.getPort(), true)) {
                var clientParams = tls.getSSLParameters();
                clientParams.setEndpointIdentificationAlgorithm("HTTPS"); // check the name; off by default on a raw SSLSocket
                clientParams.setApplicationProtocols(new String[] {"h2", "http/1.1"});
                tls.setSSLParameters(clientParams);
                tls.startHandshake();
                var session = tls.getSession();
                return String.join(" ", List.of(session.getProtocol(), session.getCipherSuite(), tls.getApplicationProtocol()));
            } catch (SSLHandshakeException failed) {
                for (Throwable cause = failed; cause != null; cause = cause.getCause()) {
                    if (cause instanceof CertificateExpiredException) return cause.getClass().getName();
                }
                return failed.getMessage();
            } finally {
                serving.join();
            }
        }
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/12-tls-and-transport-security/labs/java). `python3 labs/run.py tls-and-transport-security/java`.

## 8. Rust

The standard library has no cryptography, so every piece is a crate: `num-bigint` for numbers past 128 bits, `x25519-dalek`, `hkdf` with `sha2`, `aes-gcm`, and `rustls` for TLS. An `EphemeralSecret` can be used for one key exchange only, because `diffie_hellman` takes it by value: the type system enforces the "fresh key per connection" that forward secrecy needs. Each failure is a `rustls::Error::InvalidCertificate` variant.

```rust
//! The maths under TLS by hand (num-bigint for numbers past 128 bits), then the real primitives from RustCrypto
//! crates: X25519 (x25519-dalek), HKDF (hkdf) and AES-GCM (aes-gcm). The standard library has no cryptography at
//! all. The handshake is rustls, exercised in the tests.
use aes_gcm::aead::{Aead, KeyInit, Payload};
use aes_gcm::{Aes256Gcm, Nonce};
use hkdf::Hkdf;
use num_bigint::BigUint;
use sha2::Sha256;

/// Square-and-multiply, counting multiplications. BigUint's modpow does the same, faster.
pub fn mod_pow(base: &BigUint, exp: &BigUint, m: &BigUint) -> (BigUint, u32) {
    let (mut result, mut b, mut multiplications) = (BigUint::from(1u32), base % m, 0);
    for i in 0..exp.bits() {
        if exp.bit(i) {
            result = result * &b % m;
            multiplications += 1;
        }
        b = &b * &b % m;
        multiplications += 1;
    }
    (result, multiplications)
}

/// Finds x with g^x = target (mod p) the only general way, trying every exponent; the steps taken equal x.
pub fn discrete_log(g: u64, target: u64, p: u64) -> Option<u64> {
    let mut value = 1;
    (1..p).find(|_| {
        value = value * g % p;
        value == target
    })
}

/// Stretches the shared secret into a 32-byte key for one purpose, bound to the handshake so far.
pub fn derive_key(secret: &[u8], label: &str, transcript_hash: &[u8]) -> [u8; 32] {
    let mut key = [0; 32];
    Hkdf::<Sha256>::new(Some(transcript_hash), secret)
        .expand(label.as_bytes(), &mut key)
        .expect("32 bytes is well within HKDF's limit");
    key
}

/// Encrypts and authenticates; the 16-byte tag is appended to the ciphertext.
pub fn seal(key: &[u8; 32], nonce: &[u8; 12], plaintext: &[u8], associated: &[u8]) -> Vec<u8> {
    let cipher = Aes256Gcm::new(key.into());
    cipher
        .encrypt(
            &Nonce::from(*nonce),
            Payload {
                msg: plaintext,
                aad: associated,
            },
        )
        .expect("encryption only fails for absurdly long messages")
}

/// Checks the tag and decrypts; an error if a single bit of the ciphertext or associated data changed.
pub fn open(
    key: &[u8; 32],
    nonce: &[u8; 12],
    sealed: &[u8],
    associated: &[u8],
) -> Result<Vec<u8>, aes_gcm::Error> {
    Aes256Gcm::new(key.into()).decrypt(
        &Nonce::from(*nonce),
        Payload {
            msg: sealed,
            aad: associated,
        },
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use rustls::pki_types::pem::PemObject;
    use rustls::pki_types::{CertificateDer, PrivateKeyDer, ServerName};
    use rustls::{
        ClientConfig, ClientConnection, RootCertStore, ServerConfig, ServerConnection, StreamOwned,
    };
    use std::io::Write;
    use std::net::{TcpListener, TcpStream};
    use std::path::{Path, PathBuf};
    use std::process::Command;
    use std::sync::Arc;
    use x25519_dalek::{EphemeralSecret, PublicKey};

    fn n(x: u64) -> BigUint {
        BigUint::from(x)
    }

    #[test]
    fn diffie_hellman_by_hand() {
        let p = n(23);
        let (a, b) = (mod_pow(&n(5), &n(6), &p).0, mod_pow(&n(5), &n(15), &p).0);
        assert_eq!((a.clone(), b.clone()), (n(8), n(19)));
        assert_eq!((b.modpow(&n(6), &p), a.modpow(&n(15), &p)), (n(2), n(2))); // BigUint's modpow agrees
    }

    #[test]
    fn easy_forwards_hard_backwards() {
        assert_eq!(mod_pow(&n(3), &n(54_321), &n(65_537)), (n(21_002), 23));
        assert_eq!(discrete_log(3, 21_002, 65_537), Some(54_321));
        let p = (n(1) << 255u32) - n(19); // 2^255 - 19, Curve25519's prime
        assert_eq!(mod_pow(&n(5), &(&p - n(2)), &p).1, 508);
    }

    #[test]
    fn rsa_signature_by_hand() {
        let d = n(17).modinv(&n(60 * 52)).unwrap();
        assert_eq!(d, n(2753));
        let signature = n(65).modpow(&d, &n(3233));
        assert_eq!(
            (signature.clone(), signature.modpow(&n(17), &n(3233))),
            (n(588), n(65))
        );
    }

    #[test]
    fn x25519_hkdf_aes_gcm() {
        let (client, server) = (EphemeralSecret::random(), EphemeralSecret::random());
        let (client_public, server_public) = (PublicKey::from(&client), PublicKey::from(&server));
        let (secret, other) = (
            client.diffie_hellman(&server_public),
            server.diffie_hellman(&client_public),
        );
        assert_eq!(secret.as_bytes(), other.as_bytes()); // an EphemeralSecret can be used once: it's consumed here
        let transcript = b"hash of every handshake message so far";
        let c2s = derive_key(secret.as_bytes(), "c ap traffic", transcript);
        assert_ne!(
            c2s,
            derive_key(secret.as_bytes(), "s ap traffic", transcript)
        );
        let (nonce, header) = ([1; 12], [23, 3, 3, 0, 40]);
        let mut sealed = seal(&c2s, &nonce, b"GET / HTTP/1.1", &header);
        assert_eq!(
            open(&c2s, &nonce, &sealed, &header).unwrap(),
            b"GET / HTTP/1.1"
        );
        sealed[0] ^= 1;
        assert!(open(&c2s, &nonce, &sealed, &header).is_err());
    }

    /// Makes the lab CA and certificates with the shared script, in a fresh folder under target/.
    fn certs(name: &str) -> PathBuf {
        let dir = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("target")
            .join(name);
        let status = Command::new("sh")
            .arg("../shared/make-certs.sh")
            .arg(&dir)
            .status()
            .unwrap();
        assert!(status.success());
        dir
    }

    /// Serves one TLS connection with `cert` and connects to it. Returns "version cipher group alpn", or the error.
    fn handshake(
        dir: &Path,
        cert: &str,
        server_name: &str,
        trust_lab_ca: bool,
    ) -> Result<String, String> {
        let chain = vec![CertificateDer::from_pem_file(dir.join(cert)).unwrap()];
        let key = PrivateKeyDer::from_pem_file(dir.join("shop.key")).unwrap();
        let mut server_config = ServerConfig::builder()
            .with_no_client_auth()
            .with_single_cert(chain, key)
            .unwrap();
        server_config.alpn_protocols = vec![b"h2".to_vec(), b"http/1.1".to_vec()];
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let serving = std::thread::spawn(move || {
            let (sock, _) = listener.accept().unwrap();
            let mut tls = StreamOwned::new(
                ServerConnection::new(Arc::new(server_config)).unwrap(),
                sock,
            );
            let _ = tls.flush(); // drives the handshake; fails when the client rejects the certificate, which is the point
            let _ = tls.conn.complete_io(&mut tls.sock);
        });

        let mut roots = RootCertStore::empty(); // trusts nothing unless we add the lab CA
        if trust_lab_ca {
            roots
                .add(CertificateDer::from_pem_file(dir.join("ca.crt")).unwrap())
                .unwrap();
        }
        let mut client_config = ClientConfig::builder()
            .with_root_certificates(roots)
            .with_no_client_auth();
        client_config.alpn_protocols = vec![b"h2".to_vec(), b"http/1.1".to_vec()];
        let name = ServerName::try_from(server_name.to_string()).unwrap();
        let mut conn = ClientConnection::new(Arc::new(client_config), name).unwrap();
        let mut sock = TcpStream::connect(("127.0.0.1", port)).unwrap();
        let result = loop {
            if !conn.is_handshaking() {
                break Ok(format!(
                    "{:?} {:?} {:?} {}",
                    conn.protocol_version().unwrap(),
                    conn.negotiated_cipher_suite().unwrap().suite(),
                    conn.negotiated_key_exchange_group().unwrap().name(),
                    String::from_utf8_lossy(conn.alpn_protocol().unwrap())
                ));
            }
            if let Err(err) = conn.complete_io(&mut sock) {
                break Err(format!(
                    "{:?}",
                    err.get_ref()
                        .and_then(|e| e.downcast_ref::<rustls::Error>())
                        .unwrap()
                ));
            }
        };
        drop(sock);
        serving.join().unwrap();
        result
    }

    #[test]
    fn a_real_tls_13_handshake() {
        let dir = certs("handshake");
        assert_eq!(
            handshake(&dir, "shop.crt", "shop.test", true).unwrap(),
            "TLSv1_3 TLS13_AES_256_GCM_SHA384 X25519MLKEM768 h2"
        );
    }

    #[test]
    fn the_three_checks_each_failing_on_its_own() {
        let dir = certs("failures");
        assert!(
            handshake(&dir, "shop.crt", "evil.test", true)
                .unwrap_err()
                .starts_with("InvalidCertificate(NotValidForName")
        );
        assert_eq!(
            handshake(&dir, "shop.crt", "shop.test", false).unwrap_err(),
            "InvalidCertificate(UnknownIssuer)"
        );
        assert!(
            handshake(&dir, "expired.crt", "shop.test", true)
                .unwrap_err()
                .starts_with("InvalidCertificate(Expired")
        );
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/12-tls-and-transport-security/labs/rust). `python3 labs/run.py tls-and-transport-security/rust`.

## 9. C#

`BigInteger` has `ModPow` but no modular inverse, so the lab writes the extended Euclidean algorithm. The key exchange is ECDH on P-256 (no X25519 on Linux), then `HKDF` and `AesGcm`. The handshake uses `SslStream`; a validation callback records the `SslPolicyErrors` and the chain's status flags, which say exactly which check failed. The certificates are made on the host before the container starts, so the container needs no OpenSSL tools.

```csharp
// The maths under TLS by hand with BigInteger, then the real primitives from .NET: ECDH, HKDF and AesGcm. .NET has
// no X25519 on Linux, so the key exchange here is ECDH on P-256, the other curve TLS 1.3 offers; the maths and the
// shape of the code are the same.
using System.Numerics;
using System.Security.Cryptography;
using System.Text;

public static class TlsMath
{
    /// <summary>Square-and-multiply, counting multiplications. BigInteger.ModPow does the same, faster.</summary>
    public static (BigInteger Value, int Multiplications) ModPow(BigInteger b, BigInteger exp, BigInteger m)
    {
        BigInteger result = 1;
        b %= m;
        var multiplications = 0;
        for (; exp > 0; exp >>= 1)
        {
            if (!exp.IsEven)
            {
                result = result * b % m;
                multiplications++;
            }
            b = b * b % m;
            multiplications++;
        }
        return (result, multiplications);
    }

    /// <summary>Finds x with g^x = target (mod p) the only general way, trying every exponent; the steps equal x.</summary>
    public static long DiscreteLog(long g, long target, long p)
    {
        long value = 1;
        for (long x = 1; x < p; x++)
        {
            value = value * g % p;
            if (value == target) return x;
        }
        throw new ArithmeticException("no solution");
    }

    /// <summary>The d with a·d = 1 (mod m), by the extended Euclidean algorithm (BigInteger has no ModInverse).</summary>
    public static BigInteger ModInverse(BigInteger a, BigInteger m)
    {
        (BigInteger oldR, BigInteger r, BigInteger oldS, BigInteger s) = (a, m, 1, 0);
        while (r != 0)
        {
            var q = oldR / r;
            (oldR, r) = (r, oldR - q * r);
            (oldS, s) = (s, oldS - q * s);
        }
        return (oldS % m + m) % m;
    }

    /// <summary>Stretches the shared secret into a 32-byte key for one purpose, bound to the handshake so far.</summary>
    public static byte[] DeriveKey(byte[] secret, string label, byte[] transcriptHash) =>
        HKDF.DeriveKey(HashAlgorithmName.SHA256, secret, 32, transcriptHash, Encoding.ASCII.GetBytes(label));

    /// <summary>Encrypts and authenticates; the 16-byte tag is appended to the ciphertext.</summary>
    public static byte[] Seal(byte[] key, byte[] nonce, byte[] plaintext, byte[] associated)
    {
        using var gcm = new AesGcm(key, 16);
        var sealedBytes = new byte[plaintext.Length + 16];
        gcm.Encrypt(nonce, plaintext, sealedBytes.AsSpan(0, plaintext.Length), sealedBytes.AsSpan(plaintext.Length), associated);
        return sealedBytes;
    }

    /// <summary>Checks the tag and decrypts; throws AuthenticationTagMismatchException if anything changed.</summary>
    public static byte[] Open(byte[] key, byte[] nonce, byte[] sealedBytes, byte[] associated)
    {
        using var gcm = new AesGcm(key, 16);
        var plaintext = new byte[sealedBytes.Length - 16];
        gcm.Decrypt(nonce, sealedBytes.AsSpan(0, plaintext.Length), sealedBytes.AsSpan(plaintext.Length), plaintext, associated);
        return plaintext;
    }
}
```

```csharp
// Checks: the same results as every other language. The argument is the folder make-certs.sh filled.
using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Numerics;
using System.Security.Authentication;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Diffie-Hellman by hand: both sides reach 2 without ever sending it.
var (a, b) = (TlsMath.ModPow(5, 6, 23).Value, TlsMath.ModPow(5, 15, 23).Value);
Check((a, b) == (8, 19), (a, b));
Check(BigInteger.ModPow(b, 6, 23) == 2 && BigInteger.ModPow(a, 15, 23) == 2, "shared"); // the built-in agrees

// Easy forwards (23 multiplications), hard backwards (54,321 tries).
Check(TlsMath.ModPow(3, 54_321, 65_537) == (21_002, 23), "mod pow");
Check(TlsMath.DiscreteLog(3, 21_002, 65_537) == 54_321, "discrete log");
var curvePrime = BigInteger.Pow(2, 255) - 19;
Check(TlsMath.ModPow(5, curvePrime - 2, curvePrime).Multiplications == 508, "255-bit exponent");

// An RSA signature by hand: d is the inverse of e, and only its owner can make 588 from 65.
var d = TlsMath.ModInverse(17, 60 * 52);
var signature = BigInteger.ModPow(65, d, 3233);
Check((d, signature, BigInteger.ModPow(signature, 17, 3233)) == (2753, 588, 65), (d, signature));

// ECDH, then HKDF, then AES-GCM: the real pieces of a TLS 1.3 connection.
using var client = ECDiffieHellman.Create(ECCurve.NamedCurves.nistP256);
using var server = ECDiffieHellman.Create(ECCurve.NamedCurves.nistP256);
var secret = client.DeriveRawSecretAgreement(server.PublicKey);
Check(secret.SequenceEqual(server.DeriveRawSecretAgreement(client.PublicKey)) && secret.Length == 32, "ECDH");
var transcript = Encoding.ASCII.GetBytes("hash of every handshake message so far");
var c2s = TlsMath.DeriveKey(secret, "c ap traffic", transcript);
Check(!c2s.SequenceEqual(TlsMath.DeriveKey(secret, "s ap traffic", transcript)), "one key per direction");
var nonce = Enumerable.Repeat((byte)1, 12).ToArray();
byte[] header = [23, 3, 3, 0, 40];
var sealedBytes = TlsMath.Seal(c2s, nonce, Encoding.ASCII.GetBytes("GET / HTTP/1.1"), header);
Check(Encoding.ASCII.GetString(TlsMath.Open(c2s, nonce, sealedBytes, header)) == "GET / HTTP/1.1", "open");
sealedBytes[0] ^= 1;
try
{
    TlsMath.Open(c2s, nonce, sealedBytes, header);
    Check(false, "a flipped bit must fail the tag check");
}
catch (AuthenticationTagMismatchException)
{
    // the tag no longer matches
}

// A real TLS 1.3 handshake, then the three checks failing one at a time.
var certs = args[0];
Expect(await Handshake("shop.crt", "shop.test", true), "Tls13 TLS_AES_256_GCM_SHA384 h2");
Expect(await Handshake("shop.crt", "evil.test", true), "RemoteCertificateNameMismatch");
Expect(await Handshake("shop.crt", "shop.test", false), "RemoteCertificateChainErrors PartialChain");
Expect(await Handshake("expired.crt", "shop.test", true), "RemoteCertificateChainErrors NotTimeValid");
Console.WriteLine("all checks passed");

static void Expect(string got, string want) => Check(got == want, $"got \"{got}\", want \"{want}\"");

// Serves one TLS connection with `certFile` and connects to it. Returns "version cipher alpn", or what the client's
// certificate check found wrong.
async Task<string> Handshake(string certFile, string serverName, bool trustLabCa)
{
    using var cert = X509Certificate2.CreateFromPemFile(Path.Combine(certs, certFile), Path.Combine(certs, "shop.key"));
    using var listener = new TcpListener(IPAddress.Loopback, 0);
    listener.Start();
    var serving = Task.Run(async () =>
    {
        using var conn = await listener.AcceptTcpClientAsync();
        await using var tls = new SslStream(conn.GetStream());
        try
        {
            await tls.AuthenticateAsServerAsync(new SslServerAuthenticationOptions
            {
                ServerCertificate = cert,
                ApplicationProtocols = [SslApplicationProtocol.Http2, SslApplicationProtocol.Http11],
            });
        }
        catch (Exception e) when (e is AuthenticationException or IOException)
        {
            // the client hangs up when it rejects the certificate
        }
    });

    var problem = "";
    var options = new SslClientAuthenticationOptions
    {
        TargetHost = serverName,
        // .NET asks for revocation status by default, and the lab CA publishes no revocation list to ask.
        CertificateRevocationCheckMode = X509RevocationMode.NoCheck,
        ApplicationProtocols = [SslApplicationProtocol.Http2, SslApplicationProtocol.Http11],
        RemoteCertificateValidationCallback = (_, _, chain, errors) =>
        {
            var statuses = chain?.ChainStatus.Select(s => s.Status.ToString()) ?? [];
            problem = string.Join(" ", new[] { errors.ToString() }.Concat(statuses));
            return errors == SslPolicyErrors.None;
        },
    };
    if (trustLabCa)
    {
        options.CertificateChainPolicy = new X509ChainPolicy { TrustMode = X509ChainTrustMode.CustomRootTrust, RevocationMode = X509RevocationMode.NoCheck };
        options.CertificateChainPolicy.CustomTrustStore.Add(X509CertificateLoader.LoadCertificateFromFile(Path.Combine(certs, "ca.crt")));
    } // otherwise the system's trust store, which has never heard of the lab CA
    using var tcp = new TcpClient();
    await tcp.ConnectAsync(IPAddress.Loopback, ((IPEndPoint)listener.LocalEndpoint).Port);
    await using var tls = new SslStream(tcp.GetStream());
    try
    {
        await tls.AuthenticateAsClientAsync(options);
        return $"{tls.SslProtocol} {tls.NegotiatedCipherSuite} {tls.NegotiatedApplicationProtocol}";
    }
    catch (AuthenticationException)
    {
        return problem;
    }
    finally
    {
        tcp.Close();
        await serving;
    }
}
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/12-tls-and-transport-security/labs/csharp). `python3 labs/run.py tls-and-transport-security/csharp`.

## Common pitfalls

1. **Turning verification off to make a private CA work** (`verify=False`, `InsecureSkipVerify`, a trust-everything `TrustManager`, a callback that returns `true`). Add the CA to a trust store instead; every language here can.
2. **A raw Java `SSLSocket` without endpoint identification.** It checks the chain but not the name, so any certificate from a trusted CA is accepted for any site.
3. **Reusing a nonce with AES-GCM.** Every lab uses a fixed nonce once, for a demonstration. Two messages under the same key and nonce leak their XOR and let an attacker forge tags.
4. **Writing your own cipher or curve arithmetic.** HKDF by hand is fine for learning and checkable against test vectors; constant-time X25519 or AES is not something to write yourself.
5. **Assuming the same TLS everywhere.** Libraries on OpenSSL change behaviour with the system's OpenSSL version; Go, Java and rustls bring their own.

## Check your understanding

1. Why do Python, Node and .NET on Linux pick the same cipher suite and give similar error wording, while Go differs?
2. The Java lab's wrong-name handshake succeeds. What's missing?
3. How does Rust's `x25519-dalek` stop you from reusing a key-exchange secret?
4. The C# lab's good handshake failed with `RevocationStatusUnknown`. Why, and why don't the other labs hit it?
5. How can you trust that the Java lab's hand-written HKDF is correct?

<details>
<summary>Answers — after your attempt</summary>

1. Python, Node and .NET on Linux all hand TLS to OpenSSL, so OpenSSL's preferences and messages show through. Go's `crypto/tls` is its own implementation, with its own fixed TLS 1.3 order that puts AES-128-GCM first on processors with AES instructions.
2. `setEndpointIdentificationAlgorithm("HTTPS")` on the client's `SSLParameters`. A raw `SSLSocket` doesn't compare the hostname with the certificate unless told to.
3. `diffie_hellman` takes the `EphemeralSecret` by value, so after one call it's moved and can't be used again; the compiler rejects a second use.
4. .NET checks revocation by default and the lab's CA publishes no revocation list, so .NET can't tell whether the certificate was revoked and treats that as an error. The other languages don't check revocation unless asked.
5. It reproduces the first test vector in RFC 5869 exactly, all 42 bytes. A wrong extract or expand step would give different output.

</details>

## Practice — independent task

**Add mutual TLS to the lab in your language.**

1. Extend `make-certs.sh` (in a copy) to make a client certificate, `client.crt`, signed by the same CA, with `extendedKeyUsage=clientAuth`.
2. Make the server require a client certificate signed by the lab CA.
3. Show three cases: a client with the certificate connects; a client without one is refused; a client with a certificate from a different CA is refused.

**Done when:** all three cases behave as described, the server can read the client's name from its certificate, and you can say which side of the connection performs each check.

## Before moving on

You can name where your language gets each piece of TLS, trust a private CA without disabling checks, and say which error means which failed check.

**Recap.** The maths under TLS gives the same numbers in every language, and the handshake follows the same rules. The difference is where the code lives: Go has all of it in its standard library; Java and C# have most (Java lacks HKDF before Java 25, .NET lacks X25519 on Linux); Python has TLS through OpenSSL but needs `cryptography` for the primitives; and Rust takes every piece from crates, with `rustls` for TLS. Libraries on OpenSSL follow its version, while Go, Java and rustls bring their own. Trust a private CA by adding it to a trust store, keep the name check on (Java's raw sockets need it turned on), and never reuse a GCM nonce.

## Related

- [[networking/12-tls-and-transport-security/index|TLS and transport security]]: the main lesson, with the maths
- [[networking/11-http-evolution/in-other-languages|HTTP in other languages]]: the protocol ALPN chooses, in the same languages
- [[cybersecurity/05-cryptography/index|Cryptography]]: the primitives in more depth
- [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|Number theory and modular arithmetic]]: the maths behind the numbers
