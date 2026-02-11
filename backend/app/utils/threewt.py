import json
from urllib.parse import urlencode
from urllib.request import urlopen


def shorten_url(
    long_url: str,
    key: str,
    api_base: str,
    domain: str,
    expire_date: str | None = None,
) -> str:
    params = {
        "format": "json",
        "url": long_url,
        "key": key,
        "domain": domain,
        "protocol": "1",
    }
    if expire_date:
        params["expireDate"] = expire_date
    query = urlencode(params)
    url = f"{api_base.rstrip('/')}/api.htm?{query}"
    print("[3WT] request:", url)
    with urlopen(url, timeout=10) as resp:
        body = resp.read().decode("utf-8")
    print("[3WT] response:", body)
    data = json.loads(body)
    if str(data.get("code")) == "0" and data.get("url"):
        return data["url"]
    err = data.get("err") or "short url failed"
    raise ValueError(err)
