# Base64 Encoding

Base64 is a binary-to-text encoding scheme that represents binary data using a set of 64 printable ASCII characters. It's essentially a way to take any arbitrary bytes and convert them into a "safe" string that can travel through systems designed only for text.

To encode 3 bytes of input (24 bits), you need 4 Base64 characters (4 × 6 = 24 bits). If the input length isn't a multiple of 3, it adds padding using the `=` character.

- Because of this, it increases the size of the data by about 33%.
- Put another way: you're using 8 bits (one ASCII character) to represent only 6 bits of actual data. Two bits per character are "wasted" because you're restricting yourself to the 64-character alphabet.

## Why It Exists

Many protocols and systems were designed in an era when only plain ASCII text was reliably transmitted. Email (SMTP), URLs, JSON, XML, and HTTP headers all have restrictions on what characters they can safely contain. Binary data - images, files, encrypted content - contains bytes that would break or be mangled by these text-only channels. Base64 solves this by encoding binary into a universally safe alphabet.

## The 64-Character Alphabet

Base64 uses these characters:

- `A-Z` (26 characters)
- `a-z` (26 characters)
- `0-9` (10 characters)
- `+` and `/` (2 characters)
- `=` for padding

Some variants exist: URL-safe Base64 swaps `+/` for `-_` since plus and slash have special meanings in URLs.

## How the Encoding Works

The algorithm groups input bytes into chunks of 3 bytes (24 bits), then splits those 24 bits into 4 groups of 6 bits each. Each 6-bit group maps to one of the 64 characters.

Step by step with "Hi":

1. Get the ASCII bytes: `H` = 72, `i` = 105
1. Convert to binary: `01001000 01101001`
1. Group into 6-bit chunks: `010010 000110 1001??`
1. Since we only have 16 bits, pad to make it divisible by 6: `010010 000110 100100`
1. Convert each 6-bit value to decimal: 18, 6, 36
1. Look up in the Base64 table: `S`, `G`, `k`
1. Add `=` padding since input wasn't divisible by 3: `SGk=`

The padding rules: if input length mod 3 is 1, add `==`; if mod 3 is 2, add `=`; if mod 3 is 0, no padding needed.

## The Size Tradeoff

Base64 increases data size by approximately 33%. Every 3 bytes of input become 4 bytes of output. This is the cost of representing 256 possible byte values using only 64 characters - you need more characters to encode the same information.

## Common Use Cases

Email attachments: MIME encoding uses Base64 to embed binary files in email messages, which are fundamentally text-based.

Data URIs: Embedding images directly in HTML or CSS without separate HTTP requests. You'll see things like `data:image/png;base64,iVBORw0KGgo...` in stylesheets.

API payloads: When you need to include binary data in JSON (which doesn't support raw bytes), Base64 encoding is the standard approach. JWTs encode their header and payload sections as Base64URL.

Basic HTTP authentication: The `Authorization: Basic` header contains `username:password` encoded in Base64. Note this is encoding, not encryption - it provides no security on its own.

Storing binary in text fields: Sometimes you need to shove binary data into a database column or config file that only accepts strings.

## What Base64 Is Not

It's not encryption or compression. The encoding is trivially reversible and actually makes data larger. It provides no confidentiality - anyone can decode it instantly. It's purely a transport encoding for compatibility purposes.

## Quick Reference in Code

```python
import base64

# Encoding
data = b"Hello, World!"
encoded = base64.b64encode(data)  # b'SGVsbG8sIFdvcmxkIQ=='

# Decoding
decoded = base64.b64decode(encoded)  # b'Hello, World!'

# URL-safe variant
url_safe = base64.urlsafe_b64encode(data)  # Uses - and _ instead of + and /
```

```bash
# Command line
echo -n "Hello" | base64        # SGVsbG8=
echo "SGVsbG8=" | base64 -d     # Hello
```

The key insight: Base64 exists because we sometimes need to move binary data through text-only pipes. It's a simple, standardized way to do that at the cost of a 33% size increase.
