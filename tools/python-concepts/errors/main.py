import traceback


# --- Fake boto-style error so this is self-contained ---
class ClientError(Exception):
    """Stand-in for botocore.exceptions.ClientError."""

    def __init__(self, code, message):
        self.response = {"Error": {"Code": code, "Message": message}}
        super().__init__(f"{code}: {message}")


# --- Our package's custom exception ---
class S3WriteError(Exception):
    """Raised when a write to S3 fails."""


def put_object():
    """Pretend this is client.put_object — it fails deep in boto."""
    raise ClientError("AccessDenied", "not authorized to perform s3:PutObject")


# --- Four strategies ---
def write_v1_bare():
    try:
        put_object()
    except ClientError:
        raise  # bare re-raise


def write_v2_raise_e():
    try:
        put_object()
    except ClientError as e:
        raise e  # re-raise the same object


def write_v3_wrap_no_from():
    try:
        put_object()
    except ClientError:
        raise S3WriteError("s3://bucket/key")  # new exc, implicit context


def write_v4_wrap_from():
    try:
        put_object()
    except ClientError as e:
        raise S3WriteError("s3://bucket/key") from e  # new exc, explicit cause


def demo(fn):
    print("=" * 72)
    print(fn.__name__)
    print("=" * 72)
    try:
        fn()
    except Exception as e:
        traceback.print_exc()
        print("-" * 40)
        print("caught type        :", type(e).__name__)
        print("__cause__          :", repr(e.__cause__))
        print("__context__        :", repr(e.__context__))
        print("__suppress_context__:", e.__suppress_context__)

        # Can we still recover the underlying AWS error code?
        original = (
            e.__cause__ or e.__context__ or (e if isinstance(e, ClientError) else None)
        )
        if isinstance(original, ClientError):
            print("recovered code     :", original.response["Error"]["Code"])
        else:
            print("recovered code     : <lost>")
    print()


for fn in (write_v1_bare, write_v2_raise_e, write_v3_wrap_no_from, write_v4_wrap_from):
    demo(fn)
