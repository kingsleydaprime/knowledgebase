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
