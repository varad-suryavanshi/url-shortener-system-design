from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic_settings import BaseSettings, SettingsConfigDict

class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_expires_min: int = 60

jwt_settings = JWTSettings()

def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=jwt_settings.jwt_expires_min)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": exp}
    return jwt.encode(payload, jwt_settings.jwt_secret, algorithm=jwt_settings.jwt_alg)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, jwt_settings.jwt_secret, algorithms=[jwt_settings.jwt_alg])
    except JWTError:
        raise ValueError("Invalid token")