from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from app.database import urls_collection
from app.schemas.url import ShortenRequest, ShortenResponse, StatsResponse
from app.utils.shortcode import generate_code
from typing import Optional
from app.utils.validators import validate_custom_code
from pymongo.errors import DuplicateKeyError



router = APIRouter(tags=["urls"])

async def generate_unique_code(max_tries: int = 10) -> str:
    for _ in range(max_tries):
        code = generate_code(6)
        exists = await urls_collection.find_one({"short_code": code}, {"_id": 1})
        if not exists:
            return code
    raise HTTPException(status_code=500, detail="Could not generate unique short code")

# @router.post("/shorten", response_model=ShortenResponse)
# async def shorten_url(payload: ShortenRequest, request: Request):
#     code = await generate_unique_code()
#     now = datetime.now(timezone.utc)

#     doc = {
#         "original_url": str(payload.original_url),
#         "short_code": code,
#         "created_at": now,
#         "click_count": 0,
#     }
#     await urls_collection.insert_one(doc)

#     base = str(request.base_url).rstrip("/")  # e.g. http://127.0.0.1:8000
#     return ShortenResponse(
#         original_url=payload.original_url,
#         short_code=code,
#         short_url=f"{base}/r/{code}",
#         created_at=now,
#     )

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_for_user(
    payload: ShortenRequest,
    request: Request,
    custom: Optional[str] = Query(default=None),
):
    now = datetime.now(timezone.utc)

    if custom:
        code = validate_custom_code(custom)
        existing = await urls_collection.find_one({"short_code": code}, {"_id": 1})
        if existing:
            raise HTTPException(status_code=409, detail="Custom code already taken")
    else:
        code = await generate_unique_code()

    doc = {
        "original_url": str(payload.original_url),
        "short_code": code,
        "created_at": now,
        "click_count": 0,
        "last_clicked_at": None,
    }

    try:
        await urls_collection.insert_one(doc)
    except DuplicateKeyError:
        # in case a collision happens despite our checks
        raise HTTPException(status_code=409, detail="Short code already taken")

    base = str(request.base_url).rstrip("/")
    return ShortenResponse(
        original_url=payload.original_url,
        short_code=code,
        short_url=f"{base}/r/{code}",
        created_at=now,
    )

@router.get("/r/{short_code}")
async def redirect(short_code: str):
    doc = await urls_collection.find_one({"short_code": short_code})
    if not doc:
        raise HTTPException(status_code=404, detail="Short code not found")

    # increment click count
    # await urls_collection.update_one(
    #     {"short_code": short_code},
    #     {"$inc": {"click_count": 1}}
    # )
    now = datetime.now(timezone.utc)
    await urls_collection.update_one(
        {"short_code": short_code},
        {"$inc": {"click_count": 1}, "$set": {"last_clicked_at": now}}
    )

    return RedirectResponse(url=doc["original_url"], status_code=307)

@router.get("/stats/{short_code}", response_model=StatsResponse)
async def stats(short_code: str):
    doc = await urls_collection.find_one({"short_code": short_code})
    if not doc:
        raise HTTPException(status_code=404, detail="Short code not found")

    return StatsResponse(
        original_url=doc["original_url"],
        short_code=doc["short_code"],
        created_at=doc["created_at"],
        click_count=doc.get("click_count", 0),
        last_clicked_at=doc.get("last_clicked_at"),
    )