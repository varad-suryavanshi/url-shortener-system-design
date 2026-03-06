from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    mongodb_uri: str
    mongodb_db: str

settings = Settings()

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.mongodb_db]

urls_collection = db["urls"]
users_collection = db["users"]