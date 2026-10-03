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
