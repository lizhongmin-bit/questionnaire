import json
import ssl
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def shorten_url(
    long_url: str,
    token: str,
    term: str,
    api_base: str,
    ssl_verify: bool = True,
    ca_file: str | None = None,
) -> str:
    api_base = api_base.rstrip("/")
    payload = json.dumps(
        [
            {
                "LongUrl": long_url,
                "TermOfValidity": term,
            }
        ],
        ensure_ascii=False,
    ).encode("utf-8")
    try:
        print("[DWZ] request:", payload.decode("utf-8"))
    except Exception:
        print("[DWZ] request: <decode failed>")
    req = Request(
        f"{api_base}/api/v3/short-urls",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=UTF-8",
            "Dwz-Token": token,
        },
    )
    try:
        context = None
        if ssl_verify:
            context = ssl.create_default_context(cafile=ca_file) if ca_file else ssl.create_default_context()
        else:
            context = ssl._create_unverified_context()
        with urlopen(req, timeout=10, context=context) as resp:
            body = resp.read().decode("utf-8")
    except HTTPError as exc:
        try:
            err_body = exc.read().decode("utf-8")
        except Exception:
            err_body = ""
        if err_body:
            print("[DWZ] response (error):", err_body)
        else:
            print("[DWZ] response (error): <empty>")
        raise ValueError(f"HTTP {exc.code} {err_body}".strip()) from exc
    print("[DWZ] response:", body)
    data = json.loads(body)
    if data.get("Code") == 0:
        short_urls = data.get("ShortUrls") or []
        if short_urls and short_urls[0].get("ShortUrl"):
            return short_urls[0]["ShortUrl"]
    if data.get("Code") == -99:
        short_urls = data.get("ShortUrls") or []
        if short_urls:
            err = short_urls[0].get("ErrMsg") or "short url failed"
            raise ValueError(err)
    raise ValueError(data.get("ErrMsg") or "short url failed")
