// tlsmath.ts — the maths under TLS, small enough to follow by hand, then the real thing with node:crypto.
// The toy numbers are for understanding only: never use hand-written crypto, or numbers this small, for real.
import { createCipheriv, createDecipheriv, diffieHellman, generateKeyPairSync, hkdfSync, type KeyObject } from "node:crypto";

/**
 * base^exp mod m by square-and-multiply: walk the exponent's bits, squaring each time and multiplying when the bit
 * is 1. Reducing mod m after every step keeps the numbers small. Returns the result and the multiplications used,
 * which grow with the number of bits in exp, not with exp itself.
 */
export function modPow(base: bigint, exp: bigint, m: bigint): { value: bigint; multiplications: number } {
  let result = 1n;
  let b = base % m;
  let e = exp;
  let multiplications = 0;
  while (e > 0n) {
    if (e & 1n) {
      result = (result * b) % m;
      multiplications++;
    }
    b = (b * b) % m;
    multiplications++;
    e >>= 1n;
  }
  return { value: result, multiplications };
}

/** The other direction: find x with g^x ≡ target (mod p) by trying x = 1, 2, 3, … The only general way for a small group. */
export function discreteLog(g: bigint, target: bigint, p: bigint): { x: bigint; steps: number } {
  let value = 1n;
  for (let x = 1n, steps = 1; x < p; x++, steps++) {
    value = (value * g) % p;
    if (value === target) return { x, steps };
  }
  throw new RangeError("no solution");
}

/** The inverse of a mod m, by the extended Euclidean algorithm: the d with a·d ≡ 1 (mod m). */
export function modInverse(a: bigint, m: bigint): bigint {
  let [oldR, r] = [a, m];
  let [oldS, s] = [1n, 0n];
  while (r !== 0n) {
    const q = oldR / r;
    [oldR, r] = [r, oldR - q * r];
    [oldS, s] = [s, oldS - q * s];
  }
  if (oldR !== 1n) throw new RangeError("no inverse: a and m share a factor");
  return ((oldS % m) + m) % m;
}

/** A real X25519 key pair: the private key stays here; only the 32-byte public key is ever sent. */
export function keyPair(): { privateKey: KeyObject; publicKey: KeyObject } {
  return generateKeyPairSync("x25519");
}

/** Both sides compute this from their own private key and the other's public key, and get the same 32 bytes. */
export function sharedSecret(mine: KeyObject, theirs: KeyObject): Buffer {
  return diffieHellman({ privateKey: mine, publicKey: theirs });
}

/**
 * HKDF turns one shared secret into as many independent keys as needed, each tied to a label: "client to server"
 * and "server to client" get different keys from the same secret, as TLS 1.3's key schedule does.
 */
export function deriveKey(secret: Buffer, label: string, transcriptHash: Buffer): Buffer {
  return Buffer.from(hkdfSync("sha256", secret, transcriptHash, label, 32));
}

/**
 * AES-256-GCM: encrypts and also computes a 16-byte tag over the ciphertext and the "additional data" (sent in the
 * clear but protected, like a record's header). A nonce must never repeat under the same key.
 */
export function seal(key: Buffer, nonce: Buffer, plaintext: string, additionalData: Buffer) {
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  cipher.setAAD(additionalData);
  const ciphertext = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  return { ciphertext, tag: cipher.getAuthTag() };
}

/** Decrypts, and throws unless the tag proves nothing was changed: ciphertext, additional data or tag. */
export function open(key: Buffer, nonce: Buffer, ciphertext: Buffer, tag: Buffer, additionalData: Buffer): string {
  const decipher = createDecipheriv("aes-256-gcm", key, nonce);
  decipher.setAAD(additionalData);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");
}
