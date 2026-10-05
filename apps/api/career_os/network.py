"""Small allowlisted HTTPS transport, no redirects or implicit retries."""

import json
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit

ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.openai.com"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:
        return None


def bounded_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    max_bytes: int = 5_000_000,
    timeout: int = 20,
) -> dict[str, Any]:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_HOSTS
        or parsed.username
        or parsed.password
        or parsed.port not in {None, 443}
    ):
        raise ValueError("network_destination_denied")
    request = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AI-Career-OS/0.1",
            **(headers or {}),
        },
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError("network_response_too_large")
        result = json.loads(body)
        if not isinstance(result, dict):
            raise ValueError("network_expected_object")
        return result
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        # Never propagate provider bodies, keys or arbitrary source text into logs.
        raise ValueError("network_request_failed") from None
