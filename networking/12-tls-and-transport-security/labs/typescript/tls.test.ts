import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { X509Certificate } from "node:crypto";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import tls from "node:tls";
import { deriveKey, discreteLog, keyPair, modInverse, modPow, open, seal, sharedSecret } from "./tlsmath.ts";

test("Diffie-Hellman by hand: p = 23, g = 5, secrets 6 and 15", () => {
  const [p, g, a, b] = [23n, 5n, 6n, 15n];
  const A = modPow(g, a, p).value; // Alice sends A
  const B = modPow(g, b, p).value; // Bob sends B
  assert.deepEqual([A, B], [8n, 19n]);
  assert.equal(modPow(B, a, p).value, 2n); // Alice: B^a = g^(ba)
  assert.equal(modPow(A, b, p).value, 2n); // Bob:   A^b = g^(ab): the same secret, never sent
});

test("easy forwards, hard backwards: the discrete logarithm", () => {
  const forwards = modPow(3n, 54_321n, 65_537n);
  assert.deepEqual(forwards, { value: 21_002n, multiplications: 23 }); // about two per bit of the exponent
  assert.deepEqual(discreteLog(3n, 21_002n, 65_537n), { x: 54_321n, steps: 54_321 }); // one per possible exponent
  // X25519's group has about 2^252 elements: forwards is still a few hundred multiplications...
  assert.equal(modPow(5n, 2n ** 255n - 21n, 2n ** 255n - 19n).multiplications, 508);
  // ...and backwards, by trying exponents, would take about 2^252 steps. Better algorithms exist, but not good enough.
});

test("an RSA signature by hand: n = 61 × 53, e = 17", () => {
  const [p, q, e] = [61n, 53n, 17n];
  const n = p * q;
  const d = modInverse(e, (p - 1n) * (q - 1n)); // the private exponent: e × d ≡ 1 (mod φ(n))
  assert.deepEqual([n, d], [3233n, 2753n]);
  const digest = 65n; // in reality, a hash of the certificate's contents
  const signature = modPow(digest, d, n).value; // only the private key can make this
  assert.equal(signature, 588n);
  assert.equal(modPow(signature, e, n).value, 65n); // anyone with the public key (n, e) can check it
  assert.notEqual(modPow(signature, e, n).value, 66n); // and it doesn't fit any other digest
});

test("the real thing: X25519, then HKDF, then AES-256-GCM", () => {
  const [client, server] = [keyPair(), keyPair()];
  const clientSecret = sharedSecret(client.privateKey, server.publicKey);
  assert.deepEqual(clientSecret, sharedSecret(server.privateKey, client.publicKey)); // the same 32 bytes on both sides
  assert.equal(clientSecret.length, 32);
  assert.equal(client.publicKey.export({ type: "spki", format: "der" }).length, 44); // 12 bytes of label + the 32-byte key

  const transcript = Buffer.from("hash of every handshake message so far");
  const clientToServer = deriveKey(clientSecret, "c ap traffic", transcript);
  const serverToClient = deriveKey(clientSecret, "s ap traffic", transcript);
  assert.notDeepEqual(clientToServer, serverToClient); // one secret, independent keys per direction

  const nonce = Buffer.alloc(12, 1);
  const header = Buffer.from([23, 3, 3, 0, 40]); // a TLS record header: sent in the clear, but covered by the tag
  const { ciphertext, tag } = seal(clientToServer, nonce, "GET / HTTP/1.1", header);
  assert.equal(open(clientToServer, nonce, ciphertext, tag, header), "GET / HTTP/1.1");
  const tampered = Buffer.from(ciphertext);
  tampered[0] ^= 1; // flip one bit on the way
  assert.throws(() => open(clientToServer, nonce, tampered, tag, header), /unable to authenticate/);
  assert.throws(() => open(serverToClient, nonce, ciphertext, tag, header), /unable to authenticate/); // the wrong key
});

// A small certificate authority, made with the openssl command-line tool in a temporary folder.
let dir = "";
const file = (name: string) => readFileSync(join(dir, name));

before(() => {
  dir = mkdtempSync(join(tmpdir(), "tls-lab-"));
  const openssl = (...args: string[]) => execFileSync("openssl", args, { cwd: dir, stdio: "pipe" });
  const ec = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-nodes"];
  openssl("req", "-x509", ...ec, "-keyout", "ca.key", "-out", "ca.crt", "-subj", "/CN=Lab Root CA", "-days", "1");
  openssl("req", ...ec, "-keyout", "shop.key", "-out", "shop.csr", "-subj", "/CN=shop.test");
  writeFileSync(join(dir, "san.cnf"), "subjectAltName=DNS:shop.test\n"); // the names the certificate is valid for
  const sign = ["x509", "-req", "-in", "shop.csr", "-CA", "ca.crt", "-CAkey", "ca.key", "-extfile", "san.cnf"];
  openssl(...sign, "-out", "shop.crt", "-days", "1");
  openssl(...sign, "-out", "expired.crt", "-not_before", "20200101000000Z", "-not_after", "20200102000000Z");
});

after(() => rmSync(dir, { recursive: true, force: true }));

/** Starts a TLS server with this certificate, connects once, and reports what the client saw. */
async function handshake(cert: string, client: tls.ConnectionOptions) {
  const server = tls.createServer({ key: file("shop.key"), cert: file(cert), ALPNProtocols: ["h2", "http/1.1"] }, (s) => s.end());
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    return await new Promise<Record<string, unknown>>((resolve) => {
      const socket = tls.connect({ port: (server.address() as { port: number }).port, host: "127.0.0.1", ...client }, () => {
        resolve({
          version: socket.getProtocol(),
          cipher: socket.getCipher().name,
          alpn: socket.alpnProtocol,
          group: socket.getEphemeralKeyInfo() && (socket.getEphemeralKeyInfo() as { name: string }).name,
          sessionKeys: socket.exportKeyingMaterial(16, "lab").toString("hex"),
        });
        socket.end();
      });
      socket.on("error", (err: NodeJS.ErrnoException) => resolve({ error: err.code }));
    });
  } finally {
    server.close();
  }
}

test("the certificate's signature checks out against the CA's public key, and names shop.test", () => {
  const shop = new X509Certificate(file("shop.crt"));
  const ca = new X509Certificate(file("ca.crt"));
  assert.equal(shop.verify(ca.publicKey), true);
  assert.equal(shop.checkHost("shop.test"), "shop.test");
  assert.equal(shop.checkHost("evil.test"), undefined);
});

test("a real TLS 1.3 handshake: one cipher suite, ALPN, a hybrid post-quantum key exchange", async () => {
  const result = await handshake("shop.crt", { servername: "shop.test", ca: file("ca.crt"), ALPNProtocols: ["h2", "http/1.1"] });
  assert.equal(result.version, "TLSv1.3");
  assert.equal(result.cipher, "TLS_AES_256_GCM_SHA384");
  assert.equal(result.alpn, "h2"); // HTTP/2 chosen inside the handshake, no extra round trip
  assert.equal(result.group, "X25519MLKEM768"); // X25519 combined with ML-KEM: the default in OpenSSL 3.5
});

test("every connection gets fresh keys, even with the same certificate", async () => {
  const options = { servername: "shop.test", ca: file("ca.crt") };
  const [first, second] = [await handshake("shop.crt", options), await handshake("shop.crt", options)];
  assert.notEqual(first.sessionKeys, second.sessionKeys); // ephemeral key exchange: forward secrecy
});

test("the three checks a client makes, each failing on its own", async () => {
  const trusted = { ca: file("ca.crt") };
  assert.equal((await handshake("shop.crt", { ...trusted, servername: "evil.test" })).error, "ERR_TLS_CERT_ALTNAME_INVALID"); // wrong name
  assert.equal((await handshake("shop.crt", { servername: "shop.test" })).error, "UNABLE_TO_VERIFY_LEAF_SIGNATURE"); // CA not trusted
  assert.equal((await handshake("expired.crt", { ...trusted, servername: "shop.test" })).error, "CERT_HAS_EXPIRED"); // out of date
});
