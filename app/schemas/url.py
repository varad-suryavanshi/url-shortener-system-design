from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class ShortenRequest(BaseModel):
    original_url: HttpUrl

class ShortenResponse(BaseModel):
    original_url: HttpUrl
    short_code: str
    short_url: str
    created_at: datetime

class StatsResponse(BaseModel):
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    click_count: int = Field(ge=0)
    last_clicked_at: Optional[datetime] = None