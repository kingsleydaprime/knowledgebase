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
