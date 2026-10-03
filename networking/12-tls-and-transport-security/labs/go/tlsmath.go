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
