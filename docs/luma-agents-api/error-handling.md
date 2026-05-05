---
title: Error handling | Luma Agents
description: Every HTTP status code, error response, rate limit scenario, and async failure mode in the Luma Agents API.
---

This page documents every error the Luma Agents API can return, both synchronous errors (returned immediately) and asynchronous failures (discovered when polling). Use it as a reference when building error handling into your integration.

## Quick reference

| Status | Meaning                          | Retryable?                     |
| ------ | -------------------------------- | ------------------------------ |
| 201    | Success — generation created     | —                              |
| 400    | Invalid request parameters       | No — fix parameters            |
| 401    | Invalid or missing API key       | No — fix authentication        |
| 402    | Insufficient credits             | No — add credits               |
| 403    | Access denied (plan or account)  | No — check your plan           |
| 413    | Image exceeds 50 MB              | No — resize image              |
| 422    | Bad image data (base64 or URL)   | No — fix image                 |
| 429    | Rate limited (RPM or concurrent) | Yes — use `Retry-After` header |
| 502    | Upstream service unavailable     | Yes — retry with backoff       |
| 503    | Image ingestion unavailable      | Yes — retry or use base64      |

## Machine-readable codes

**Synchronous errors** (returned immediately) use **HTTP status codes** as the primary machine-readable identifier — branch on the status code, then read `detail` for specifics.

**Asynchronous failures** (discovered when polling) include a **`failure_code`** field for programmatic handling:

| `failure_code`      | Description                                       | Retryable?                   |
| ------------------- | ------------------------------------------------- | ---------------------------- |
| `content_moderated` | Prompt or input image violated content guidelines | No — modify prompt           |
| `generation_failed` | Internal model error during generation            | Yes — retry same request     |
| `budget_exhausted`  | Credits ran out mid-generation                    | No — add credits, then retry |
| `output_not_found`  | Generated output could not be retrieved           | Yes — retry same request     |

```python
if generation.state == "failed":
    if generation.failure_code == "content_moderated":
        # Do not retry — modify the prompt
        raise ValueError(f"Content policy violation: {generation.failure_reason}")
    else:
        # Transient error — safe to retry
        retry_generation(generation)
```

See [Asynchronous failures](#asynchronous-failures) below for the full response structure and handling examples.

---

## Error response format

All error responses share the same shape:

```json
{
  "detail": "Human-readable error message describing what went wrong"
}
```

Every response — success or error — includes these headers:

| Header          | Description                                                                          |
| --------------- | ------------------------------------------------------------------------------------ |
| `X-Request-Id`  | Echoes your `X-Request-Id` header, or a server-generated UUID if you didn't send one |
| `X-API-Version` | API version for this response (currently `2026-04-01`)                               |

Always log the `X-Request-Id` from error responses. Include it in support requests to help trace the issue.

---

## Synchronous errors on `POST /v1/generations`

These errors are returned immediately when submitting a generation request.

### 201 — Created (success)

The happy path. The generation was accepted and queued for processing.

**Response (HTTP 201):**

```
HTTP/1.1 201 Created
Content-Type: application/json
X-Request-Id: 550e8400-e29b-41d4-a716-446655440000
X-API-Version: 2026-04-01
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1712592060
```

```json
{
  "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "type": "image",
  "state": "queued",
  "model": "uni-1",
  "created_at": "2026-04-08T12:00:00Z",
  "output": [],
  "failure_reason": null,
  "failure_code": null
}
```

Note the rate limit headers — use them to track your remaining quota proactively.

---

### 400 — Bad Request

The request body contains invalid or conflicting parameters. The `detail` field tells you exactly what's wrong.

**Unknown model**

Request:
```json
{
  "prompt": "A sunset over the ocean",
  "model": "super-model-v9"
}
```
Response:
```json
{
  "detail": "Unknown model: super-model-v9"
}
```
Fix: Use a supported model. Currently the only supported value is `uni-1`. Note: ungranted alias names also surface as `"Unknown model"` (HTTP 400), not as a distinct "not on your plan" error — this is intentional, to prevent enumeration of unreleased aliases.

**Unsupported generation type**

Request:
```json
{
  "prompt": "A sunset over the ocean",
  "type": "video"
}
```
Response:
```json
{
  "detail": "Type 'video' is not supported for model 'uni-1'"
}
```
Fix: Set `type` to `"image"` or `"image_edit"` — the only types supported by `uni-1`.

**Invalid aspect ratio**

Request:
```json
{
  "prompt": "A sunset over the ocean",
  "aspect_ratio": "4:3"
}
```
Response:
```json
{
  "detail": "Invalid aspect_ratio '4:3'. Valid: 1:1, 1:2, 1:3, 16:9, 2:1, 2:3, 3:1, 3:2, 9:16"
}
```
Fix: Use one of the 9 supported aspect ratios.

**Prompt too short / too long**

```json
{ "detail": "Prompt must be between 1 and 6000 characters" }
```
Fix: Provide a prompt between 1 and 6,000 characters.

**Malformed image reference — both `url` and `data` provided**

Each `ImageRef` must use **either** `url` or `data`, not both.

```json
{ "detail": "image_ref[0]: provide either 'url' or 'data', not both" }
```

The `detail` is prefixed with the field path — `source` for the edit source image, or `image_ref[i]` for the reference at index `i`.

**Too many image references on an edit (more than 8)**

For `type: "image_edit"`, the source image occupies one reference slot, so you may only pass up to 8 additional references via `image_ref`.

```json
{ "detail": "image_edit supports up to 8 reference images (source occupies one slot)" }
```

**Source provided for type "image"**

```json
{ "detail": "source is only valid for type 'image_edit'" }
```

**Source missing for type "image_edit"**

```json
{ "detail": "source is required for type 'image_edit'" }
```

**Base64 data without `media_type`**

```json
{ "detail": "image_ref[0]: 'media_type' is required with 'data'" }
```

---

### 401 — Unauthorized

Authentication failed. The `Authorization` header is missing, malformed, or contains an invalid key.

The four 401 `detail` strings are distinct — branch on them if you want to surface a tailored message to your users:

| `detail`                       | Cause                                                              |
| ------------------------------ | ------------------------------------------------------------------ |
| `"Missing or invalid API key"` | No `Authorization` header, wrong scheme, or non-`luma-api-*` token |
| `"Invalid API key"`            | Bearer-form key whose value does not match any key on the server   |
| `"API key has been revoked"`   | Key was explicitly revoked                                         |
| `"API key has expired"`        | Key passed its `expires_at`                                        |

All four return HTTP 401, so a generic `if status == 401` branch is also fine.

---

### 402 — Payment Required

Your account does not have enough credits to process this generation.

```json
{ "detail": "Insufficient credits. Please add credits to continue." }
```

Fix: Add credits to your account, then retry. The request was not queued.

---

### 403 — Forbidden

Access is denied. There are several reasons this can happen:

**API client is suspended**

```json
{ "detail": "API client is suspended" }
```
Fix: Contact support to resolve the suspension.

**API client is deactivated**

```json
{ "detail": "API client is deactivated" }
```
Fix: Contact support to reactivate the client.

**There is no separate 403 for "model not available on plan."** When you request a model your client doesn't have access to (including unreleased aliases), the API returns **HTTP 400 with `"Unknown model: <name>"`** — see the [400 — Bad Request](#400--bad-request) section above. The 400-vs-403 collapse is deliberate: it prevents enumeration of unreleased model aliases.

---

### 413 — Payload Too Large

An image in your request (`source` or `image_ref`) exceeds the 50 MB size limit.

```json
{ "detail": "Image exceeds 50 MB size limit" }
```

This applies to:

- The `source` image in `image_edit` requests
- Any entry in the `image_ref` array
- Both URL-referenced and base64-encoded images

Fix: Resize or compress the image to under 50 MB before sending.

---

### 422 — Unprocessable Entity

An image reference was syntactically valid but could not be processed.

**Invalid base64 data**

```json
{ "detail": "image_ref[0]: invalid base64 data" }
```
Fix: Ensure the data is properly base64-encoded. In Python: `base64.b64encode(image_bytes).decode("utf-8")`.

**URL fetch failure — unreachable host**

```json
{ "detail": "image_ref[0]: failed to fetch URL" }
```
Fix: Verify the URL is publicly accessible and responds with image content.

**URL fetch failure — 404 or other HTTP error**

```json
{ "detail": "source: failed to fetch URL (HTTP 404)" }
```

**URL fetch failure — not an image**

```json
{ "detail": "image_ref[0]: content-type is not an image" }
```
Fix: Ensure the URL points to a valid image file (JPEG, PNG, etc.). The `detail` is surfaced by the upstream fetch proxy, so exact wording may vary.

---

### 429 — Too Many Requests

You've hit a rate limit. There are two distinct scenarios — see [Rate limits and headers](./rate-limits.md) for the full discussion.

**Requests-per-minute (RPM) limit exceeded**

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1712592012
```

```json
{ "detail": "Rate limit exceeded" }
```

Fix: Wait for the duration specified in `Retry-After`, or until the `X-RateLimit-Reset` timestamp.

**Concurrent job limit exceeded**

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

```json
{ "detail": "Too many concurrent jobs" }
```

Note: Concurrent job 429s include a fixed `Retry-After: 60` but do **not** include `X-RateLimit-*` headers (those only apply to RPM limiting).

Fix: Wait for one or more of your active generations to reach `completed` or `failed` before submitting new ones.

---

### 502 — Bad Gateway

An upstream service required to process your request is temporarily unavailable.

```json
{ "detail": "Upstream service unavailable" }
```

This can happen when the fetch proxy (used to download URL-referenced images) is down, or when internal scope provisioning fails.

Fix: Retry after a brief delay (5–10 seconds). If the error persists, contact support.

---

### 503 — Service Unavailable

The image URL ingestion subsystem is not available.

```json
{ "detail": "Image URL ingestion unavailable" }
```

This specifically affects requests that reference images via `url` (in `source` or `image_ref`).

Fix: As a workaround, download the image yourself and send it as base64 `data` instead:

```python
import base64
import httpx


# Download the image yourself
response = httpx.get("https://example.com/reference.jpg")
image_b64 = base64.b64encode(response.content).decode("utf-8")


# Send as base64 instead of URL
generation = client.generations.create(
    prompt="A similar scene but at sunset",
    image_ref=[
        {
            "data": image_b64,
            "media_type": "image/jpeg",
        }
    ],
)
```

If you don't need image references, retry without them.

---

## Synchronous errors on `GET /v1/generations/{generation_id}`

### 200 — OK (success)

The generation was found and its current status is returned.

### 401 — Unauthorized

Same as the POST endpoint — the `Authorization` header is missing, malformed, or invalid.

### 404 — Not Found

The generation ID does not exist, or it belongs to a different API key.

```json
{ "detail": "Generation not found" }
```

The error message is intentionally identical for "does not exist" and "belongs to another API key" to prevent enumeration.

Fix: Verify the generation ID and that you're using the same API key that submitted the original generation.

---

## Asynchronous failures

These failures happen **after** the `POST` succeeds with HTTP 201. You discover them by polling `GET /v1/generations/{id}` and finding `state: "failed"`.

Asynchronous failures are not HTTP errors. The POST returned 201 and the GET returns 200. The failure is indicated by the `state` field being `"failed"`, the `failure_reason` field containing a human-readable description, and the `failure_code` field containing a machine-readable code.

### Failed response structure

```json
{
  "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
  "type": "image",
  "state": "failed",
  "model": "uni-1",
  "created_at": "2026-04-08T12:00:00Z",
  "output": [],
  "failure_reason": "Description of what went wrong",
  "failure_code": "generation_failed"
}
```

Key differences from a completed response:

- `state` is `"failed"` instead of `"completed"`
- `output` is an empty array `[]`
- `failure_reason` contains a non-null human-readable string
- `failure_code` contains a machine-readable code for programmatic handling

### Failure codes

| `failure_code`      | Description                                                   | Action                                               |
| ------------------- | ------------------------------------------------------------- | ---------------------------------------------------- |
| `content_moderated` | The prompt or input image violated content guidelines         | Modify the prompt and resubmit — do not retry as-is  |
| `generation_failed` | The model encountered an internal error during generation     | Retry the same request — this is typically transient |
| `budget_exhausted`  | The account ran out of credits partway through the generation | Add credits, then resubmit                           |
| `output_not_found`  | The generated output could not be retrieved                   | Retry the same request                               |

### Possible failure reasons

| Failure reason                                                  | Description                                               | Action                                               |
| --------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------- |
| Generation output was flagged by our content moderation system. | The output image was flagged by content moderation        | Modify the prompt and resubmit                       |
| Insufficient credits to complete this generation.               | The account ran out of credits mid-generation             | Add credits, then resubmit                           |
| Generation failed                                               | The model encountered an internal error during generation | Retry the same request — this is typically transient |
| Output artifacts not found                                      | The generated output could not be retrieved               | Retry the same request                               |

### Handling async failures in code

Always check for the `failed` state when polling. Never assume a generation will complete.

```python
import time
from luma_agents import Luma


client = Luma()


generation = client.generations.create(
    prompt="A sunset over the ocean",
)


while generation.state not in ("completed", "failed"):
    time.sleep(2)
    generation = client.generations.get(generation.id)


if generation.state == "failed":
    print(f"Generation {generation.id} failed: {generation.failure_reason}")
    # Use failure_code for programmatic branching
    if generation.failure_code == "content_moderated":
        print("Content policy violation — do not retry with the same prompt")
    else:
        print("Transient error — safe to retry")
elif generation.state == "completed":
    print(f"Success: {generation.output[0].url}")
```

---

## Presigned URL expiry

Output URLs in the `output` array are **presigned S3 URLs that expire after 1 hour**. This is not an HTTP error from the API, but a common failure mode in downstream code.

### What happens when a URL expires

```bash
curl -I "https://storage.example.com/generations/d290f1ee/output.png?X-Amz-Expires=3600&..."
```

```
HTTP/1.1 403 Forbidden
```

The S3 presigned URL returns a 403 — the image data is still there, but the signature has expired.

### How to get a fresh URL

Poll the generation endpoint again. Each call to `GET /v1/generations/{id}` returns a fresh presigned URL with a new 1-hour expiry:

```python
# Original URL expired
generation = client.generations.get("d290f1ee-6c54-4b01-90e6-d701748f0851")
fresh_url = generation.output[0].url  # New presigned URL, valid for 1 hour
```

### Best practices for URL handling

1. **Download immediately** — Save images to your own storage as soon as the generation completes
2. **Don't cache URLs** — Presigned URLs are ephemeral; cache the downloaded image data instead
3. **Don't expose URLs to end users** — They'll break after 1 hour; serve images from your own CDN
4. **Re-poll if needed** — If you need the image again after expiry, call GET to get a new URL

---

## Rate limiting

For the complete guide on rate limiting — including the sliding window algorithm, all response headers, retry strategies, and proactive throttling — see [Rate limits and headers](./rate-limits.md).

**Quick reference:**

| Limit                     | Default | 429 `detail`                 |
| ------------------------- | ------- | ---------------------------- |
| Requests per minute (RPM) | 30      | `"Rate limit exceeded"`      |
| Concurrent jobs           | 10      | `"Too many concurrent jobs"` |

---

## Error handling checklist

Use this checklist to verify your integration handles all failure modes:

| Scenario                 | Type       | How to detect                                  | Action                                                                          |
| ------------------------ | ---------- | ---------------------------------------------- | ------------------------------------------------------------------------------- |
| Successful generation    | Happy path | HTTP 201, then poll until `state: "completed"` | Download from `output[].url`                                                    |
| Validation error         | Sync       | HTTP 400                                       | Fix request parameters, do not retry as-is                                      |
| Auth failure             | Sync       | HTTP 401                                       | Check API key — missing, malformed, revoked, or expired                         |
| No credits               | Sync       | HTTP 402                                       | Add credits                                                                     |
| Plan restriction         | Sync       | HTTP 403                                       | Upgrade plan, change model, or contact support (suspended/deactivated)          |
| Image too large          | Sync       | HTTP 413                                       | Compress image to under 50 MB                                                   |
| Bad image data           | Sync       | HTTP 422                                       | Fix base64 encoding or image URL                                                |
| Rate limited             | Sync       | HTTP 429                                       | Wait for `Retry-After` seconds, then retry                                      |
| Upstream down            | Sync       | HTTP 502                                       | Retry after 5–10 seconds                                                        |
| Ingestion down           | Sync       | HTTP 503                                       | Use base64 instead of URL, or retry later                                       |
| Poll — not found         | Sync       | HTTP 404 on GET                                | Check generation ID and API key                                                 |
| Async failure            | Async      | `state: "failed"` on poll                      | Branch on `failure_code`, read `failure_reason` for details, retry if transient |
| Expired output URL       | Downstream | HTTP 403 from S3                               | Re-poll GET to get fresh presigned URL                                          |
| Generation still running | Expected   | `state: "queued"` or `"processing"` on poll    | Continue polling every 2–5 seconds                                              |
