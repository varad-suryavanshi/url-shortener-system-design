from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.database import users_collection
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(payload: RegisterRequest):
    existing = await users_collection.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    doc = {
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }
    await users_collection.insert_one(doc)
    return {"message": "registered"}

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = await users_collection.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(sub=str(user["_id"]))
    return TokenResponse(access_token=token)