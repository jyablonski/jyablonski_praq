import pandas as pd
import hashlib

# encode turns text into bytes (string into binary)
# hexdigest turns bytes into hex (binary into hex)
# decode turns bytes into text (binary into string)

# md5 is 32 characters because it's 128 bits
# sha256 is 64 characters because it's 256 bits
# sha512 is 128 characters because it's 512 bits

df = "teststring123"
df = df.encode("utf-8")  # have to encode before hashing
df_md5_hash = hashlib.md5(df).hexdigest()  # 32 chars
df_sha256_hash = hashlib.sha256(df).hexdigest()  # 64 chars
df_sha512_hash = hashlib.sha512(df).hexdigest()  # 128 chars
print(df_sha256_hash)
print(df_sha512_hash)
print(df_md5_hash)

# sha256 is 32 characters
# jacob yabo concatanetes together into the same hash every time.
# otis and otisb properly comes out to different hashes.
# axis = 1 needed bc we didn't specify any columns with df.
df = pd.DataFrame(
    data={
        "first_name": ["jacob", "otis", "otisb", "jacob"],
        "last_name": ["yabo", "smith", "smith", "yabo"],
        "salary": [100000, 250000, 250000, 275000],
    }
)

df["hash_md5_onecol"] = df.apply(
    lambda x: hashlib.md5((str(x["first_name"])).encode("utf8")).hexdigest(), axis=1
)
df["hash_md5"] = df.apply(
    lambda x: hashlib.md5(
        (str(x["first_name"]) + str(x["last_name"])).encode("utf8")
    ).hexdigest(),
    axis=1,
)
df["hash_sha256"] = df.apply(
    lambda x: hashlib.sha256(
        (str(x["first_name"]) + str(x["last_name"])).encode("utf8")
    ).hexdigest(),
    axis=1,
)
df["hash_sha512"] = df.apply(
    lambda x: hashlib.sha512(
        (str(x["first_name"]) + str(x["last_name"])).encode("utf8")
    ).hexdigest(),
    axis=1,
)
print(df)

# df['hash'] = hashlib.sha256(str(df['first_name'] + df['last_name']).encode('utf-8')).hexdigest()
# df['md5'] = [hashlib.md5(val.encode('utf-8')).hexdigest() for val in df[['first_name', 'last_name']]]
# df['hash'] = (df['first_name'] + df['last_name']).apply(lambda x: x.encode('utf-8').hexdigest())
