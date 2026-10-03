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
