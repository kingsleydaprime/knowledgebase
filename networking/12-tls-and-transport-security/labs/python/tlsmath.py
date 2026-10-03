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
