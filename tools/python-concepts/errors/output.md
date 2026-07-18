# Python Exception Re-raising: What Survives, and How

Same failure (`ClientError: AccessDenied`) pushed through four re-raise strategies. The question in each case: **what type does the caller catch, and can the original AWS error code still be recovered?**

## TL;DR table

| strategy | caller catches | `__cause__` | `__context__` | `__suppress_context__` | code recoverable | traceback framing |
| -------------------------------- | -------------- | ------------- | ------------- | ---------------------- | ------------------------ | ----------------------- |
| `raise` (bare) | `ClientError` | `None` | `None` | `False` | ✅ (it *is* the original) | normal |
| `raise e` | `ClientError` | `None` | `None` | `False` | ✅ (it *is* the original) | normal + extra frame |
| `raise S3WriteError(...)` | `S3WriteError` | `None` | `ClientError` | `False` | ✅ via `__context__` | "During handling of..." |
| `raise S3WriteError(...) from e` | `S3WriteError` | `ClientError` | `ClientError` | `True` | ✅ via `__cause__` | "direct cause of" |

**The headline:** the original error survives in *all four* cases. What differs is (a) the type the caller catches and (b) which attribute holds the original — which in turn controls how the traceback reads.

______________________________________________________________________

## v1 — bare `raise`

```
caught type        : ClientError
__cause__          : None
__context__        : None
__suppress_context__: False
recovered code     : AccessDenied
```

No wrapping, no chaining. The `try/except ClientError: raise` is functionally identical to having no try/except at all. Caller still catches `ClientError`.

**Traceback:** single clean chain, `put_object → ClientError`.

______________________________________________________________________

## v2 — `raise e`

```
caught type        : ClientError
__cause__          : None
__context__        : None
__suppress_context__: False
recovered code     : AccessDenied
```

Semantically identical to v1 for the caller — still a `ClientError`, still no chaining. The only difference is cosmetic: `raise e` injects an **extra frame** pointing at the `raise e` line:

```
  line 33, in write_v2_raise_e
    raise e                    # re-raise the same object   ← extra frame
  line 31, in write_v2_raise_e
    put_object()
  line 19, in put_object
    raise ClientError(...)
```

Bare `raise` (v1) gives the tidier traceback. Prefer it.

______________________________________________________________________

## v3 — `raise S3WriteError(...)` *without* `from`

```
caught type        : S3WriteError
__cause__          : None
__context__        : ClientError('AccessDenied: ...')
__suppress_context__: False
recovered code     : AccessDenied
```

Now the caller catches `S3WriteError` (your package's contract), and the original is **still reachable** — Python sets `__context__` implicitly because you raised inside an `except` block. The code is recoverable, just via `__context__` rather than `__cause__`.

**Traceback framing** — the misleading part:

```
ClientError: AccessDenied: ...

During handling of the above exception, another exception occurred:

...
S3WriteError: s3://bucket/key
```

"During handling of the above exception" reads like a *second, separate* failure happened during cleanup — but here the `S3WriteError` **is** the boto failure re-expressed, not a surprise bug. That's why `from e` is preferred.

______________________________________________________________________

## v4 — `raise S3WriteError(...) from e` ✅ preferred for wrapping

```
caught type        : S3WriteError
__cause__          : ClientError('AccessDenied: ...')
__context__        : ClientError('AccessDenied: ...')
__suppress_context__: True
recovered code     : AccessDenied
```

Same catchable type as v3, but the relationship is now **explicit**: `from e` populates `__cause__` (the canonical attribute tooling and humans check first) and flips `__suppress_context__` to `True`.

**Traceback framing** — accurate:

```
ClientError: AccessDenied: ...

The above exception was the direct cause of the following exception:

...
S3WriteError: s3://bucket/key
```

______________________________________________________________________

## Decision guide

- **`raise` (bare)** — only when you did something first (log, Sentry tag, cleanup). Otherwise delete the try/except.
- **`raise e`** — basically never; strictly worse traceback than bare `raise`.
- **`raise XYZError(...)`** — almost never; you want `from e`.
- **`raise XYZError(...) from e`** — the default for wrapping a lower-level error in your package's own type.

**Footgun:** `raise XYZError(...) from None` *suppresses* the context entirely and hides the original — the boto code becomes unrecoverable. Occasionally useful to hide noisy internals, easy to trigger by accident.
