import re
from fastapi import HTTPException

CUSTOM_RE = re.compile(r"^[A-Za-z0-9_-]+$")

def validate_custom_code(code: str) -> str:
    code = code.strip()

    if len(code) < 4 or len(code) > 32:
        raise HTTPException(status_code=422, detail="custom code length must be 4–32")

    if not CUSTOM_RE.match(code):
        raise HTTPException(status_code=422, detail="custom code must match [A-Za-z0-9_-]")

    # Reserve words so you don't collide with your routes
    reserved = {"auth", "me", "docs", "openapi.json", "health", "stats", "r"}
    if code.lower() in reserved:
        raise HTTPException(status_code=422, detail="custom code is reserved")

    return code