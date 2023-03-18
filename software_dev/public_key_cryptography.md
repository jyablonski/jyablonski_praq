# Private Keys
[Article](https://auth0.com/blog/how-to-explain-public-key-cryptography-digital-signatures-to-anyone/)

Crypographic system comprised of 2 mathematically linked cryptographic keys generated from one-way functions.  The public key can be public, but the private key must be kept secret.  You encrypt messages with the public key, and only the private key can be utilized to decrypt them.  This works in reverse as well.

Asymmetric cryptography - using 2 keys instead of 1.  Back in the day they only used 1 and it was called Symmetric Cryptography. This was very insecure because anytime you encrypted something and sent it someplace you basically had to send the key alongside with it.

The public key is derived from a one-way function from an existing Private Key.  This means later on if you have the private key but not the public key, you can easily acquire the public key.  However, if you only have the public key then you have no way of figuring out what the private key is.

This enables 2 things:
- The ability to securely send sensitive information.
- The ability to guarantee that the message wasn't altered en-route.  This is based on the idea that once you encrypt a message it cannot be decrypted, altered, and then encrypted again without the Private Key.

This allows us to put digital signatures on our data, files, and other information sent to & from computers.  Digital signatures can only be created with a private key.

Adding a passphrase to your keypair encrypts it locally in storage.  If a hacker ever got a hold of it they wouldn't be able to read it without the passphrase, and it might buy you time to rotate the key before they brute force the passphrase.

RSA, DSA, ECC are algorithms used to create public & private key pairs.

RSA Keys are built based on 2 large prime numbers, along with an auxiliary value.  These 2 prime numbers multipled together has a product value, but it is very difficult to take the product and find the original factors.  If they're very small prime factors then this is easy, but with larger numbers it's almost impossible.  That's why you can't really reverse engineer the Key Pair and why it's known as a one-way function.

PKCS8, OpenSSH, and PEM are 3 different formats used to store Private + Public Keys.  Under the hood they're basically the same data.

`PKCS8`
```
-----BEGIN PRIVATE KEY-----
MIIBVgIBADANBgkqhkiG9w0BAQEFAASCAUAwggE8AgEAAkEAq7BFUpkGp3+LQmlQ
-----END PRIVATE KEY-----
```

`OPENSSH`
```
-----BEGIN OPENSSH PRIVATE KEY-----
```

`PEM`
```
-----BEGIN RSA PRIVATE KEY----
```