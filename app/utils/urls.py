def build_short_url(base_url: str, short_code: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/r/{short_code}"