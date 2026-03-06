from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.urls import router as urls_router
from app.database import urls_collection, client
from app.routes.auth import router as auth_router
from app.routes.me import router as me_router


app = FastAPI(title="TinyURL Clone")
app.include_router(auth_router)
app.include_router(me_router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # includes OPTIONS
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await client.admin.command("ping")
    await urls_collection.create_index("short_code", unique=True)
    await urls_collection.create_index([("user_id", 1), ("click_count", -1)])
    await urls_collection.create_index("created_at")

@app.get("/")
async def root():
    return {"message": "TinyURL API running", "docs": "/docs"}

app.include_router(health_router)
app.include_router(urls_router)