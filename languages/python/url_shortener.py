import base64
import hashlib

# sqids.org
# Sqids (pronounced "squids") is an open-source library that lets you
# generate short unique identifiers from numbers. These IDs are URL-safe,
# can encode several numbers, and do not contain common profanity words. Read more.

BASE_SERVICE = "https://jyab.ly/"


def shorten_url(url: str) -> str:
    """Shorten a URL using base64 encoding and hashing."""
    # Hash the URL
    hash_object = hashlib.md5(url.encode())
    hash_value = hash_object.hexdigest()

    # Encode the hash value
    encoded_value = base64.b64encode(hash_value.encode())

    # Return the shortened URL
    return encoded_value.decode()[:6]


url = "https://api.jyablonski.dev/hello-world"

shortened_url = shorten_url(url=url)
