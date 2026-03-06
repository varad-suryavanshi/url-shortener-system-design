from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from app.auth.deps import get_current_user
from app.database import urls_collection
from app.schemas.url import ShortenRequest, ShortenResponse
from app.routes.urls import generate_unique_code
from app.utils.validators import validate_custom_code
from app.utils.urls import build_short_url

router = APIRouter(prefix="/me", tags=["me"])

@router.get("")
async def me(user=Depends(get_current_user)):
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "created_at": user["created_at"],
    }

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_for_user(
    payload: ShortenRequest,
    request: Request,
    custom: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    now = datetime.now(timezone.utc)

    if custom:
        code = validate_custom_code(custom)
        exists = await urls_collection.find_one({"short_code": code}, {"_id": 1})
        if exists:
            raise HTTPException(status_code=409, detail="Custom code already taken")
    else:
        code = await generate_unique_code()

    doc = {
        "original_url": str(payload.original_url),
        "short_code": code,
        "created_at": now,
        "click_count": 0,
        "last_clicked_at": None,
        "user_id": str(user["_id"]),
    }

    try:
        await urls_collection.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Short code already taken")

    base = str(request.base_url).rstrip("/")
    return ShortenResponse(
        original_url=payload.original_url,
        short_code=code,
        short_url=f"{base}/r/{code}",
        created_at=now,
    )

# @router.get("/urls")
# async def list_my_urls(user=Depends(get_current_user)):
#     user_id = str(user["_id"])
#     cursor = urls_collection.find({"user_id": user_id}).sort("created_at", -1)

#     results = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])
#         results.append(doc)

#     return {"items": results}

@router.get("/urls")
async def list_my_urls(request: Request, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    cursor = urls_collection.find({"user_id": user_id}).sort("created_at", -1)

    base = str(request.base_url)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["short_url"] = build_short_url(base, doc["short_code"])
        results.append(doc)

    return {"items": results}



# @router.get("/top")
# async def top_urls(limit: int = 10, user=Depends(get_current_user)):
#     user_id = str(user["_id"])
#     limit = max(1, min(limit, 50))  # clamp 1..50

#     cursor = (
#         urls_collection.find({"user_id": user_id})
#         .sort("click_count", -1)
#         .limit(limit)
#     )

#     items = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])
#         items.append(doc)

#     return {"items": items, "limit": limit}


@router.get("/top")
async def top_urls(request: Request, limit: int = 10, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    limit = max(1, min(limit, 50))

    cursor = (
        urls_collection.find({"user_id": user_id})
        .sort("click_count", -1)
        .limit(limit)
    )

    base = str(request.base_url)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["short_url"] = build_short_url(base, doc["short_code"])
        items.append(doc)

    return {"items": items, "limit": limit}