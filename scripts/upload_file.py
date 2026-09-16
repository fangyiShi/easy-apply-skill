"""Upload one file to a short-lived HTTP upload URL returned by Notion.

This script deliberately does not create Notion upload slots or update pages. Those
connector/API operations remain in the runtime integration layer. It only performs
the multipart file POST once a trusted upload URL and headers have been returned.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import secrets
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def parse_headers(values: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for value in values:
        if ":" not in value:
            raise ValueError(f"Header must use 'Name: value' format: {value!r}")
        name, header_value = value.split(":", 1)
        name = name.strip()
        header_value = header_value.strip()
        if not name:
            raise ValueError("Header name cannot be empty")
        headers[name] = header_value
    return headers


def _multipart_body(file_path: Path, field_name: str) -> tuple[bytes, str]:
    boundary = f"----easyapply-{secrets.token_hex(16)}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    prefix = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8")
    suffix = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return prefix + file_path.read_bytes() + suffix, boundary


def upload_file(
    upload_url: str,
    file_path: str | Path,
    *,
    headers: dict[str, str] | None = None,
    field_name: str = "file",
    timeout: float = 60.0,
    allow_http: bool = False,
) -> dict[str, object]:
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Missing upload file: {path}")

    parsed = urllib.parse.urlparse(upload_url)
    if parsed.scheme not in ({"https", "http"} if allow_http else {"https"}):
        raise ValueError("Upload URL must use HTTPS")

    body, boundary = _multipart_body(path, field_name)
    request_headers = dict(headers or {})
    request_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    request_headers["Content-Length"] = str(len(body))

    request = urllib.request.Request(
        upload_url,
        data=body,
        headers=request_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read(4096).decode("utf-8", errors="replace")
            return {
                "status": response.status,
                "reason": response.reason,
                "response": response_body,
            }
    except urllib.error.HTTPError as exc:
        response_body = exc.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"Upload failed with HTTP {exc.code}: {response_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Upload request failed: {exc.reason}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="POST one file to a Notion-provided upload URL")
    parser.add_argument("--url", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--header", action="append", default=[], help="Required upload header: 'Name: value'")
    parser.add_argument("--field-name", default="file")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--allow-http", action="store_true", help="Testing only; production upload URLs should use HTTPS")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = upload_file(
            args.url,
            args.file,
            headers=parse_headers(args.header),
            field_name=args.field_name,
            timeout=args.timeout,
            allow_http=args.allow_http,
        )
    except Exception as exc:
        # Never print the upload URL or headers; they may contain short-lived secrets.
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
