import motor
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from app.tags import tags_metadata
from models import Note
from routes import notes_router

app = FastAPI(
    title="Challenge Grupo R5",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/documentation", redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseSettings):
    mongo_host: str = "books-gr5.slfcocq.mongodb.net"
    mongo_user: str = "gr5_books"
    mongo_pass: str = "Hb7j4-2h"
    mongo_db: str = "books_gr5"

    @property
    def mongo_dsn(self):
        return f"mongodb+srv://{self.mongo_user}:{self.mongo_pass}@{self.mongo_host}/{self.mongo_db}"


@app.on_event("startup")
async def app_init():
    # CREATE MOTOR CLIENT
    client = motor.motor_asyncio.AsyncIOMotorClient(
        Settings().mongo_dsn
    )

    # INIT BEANIE
    await init_beanie(client.books_gr5, document_models=[Note])

    # ADD ROUTES
    app.include_router(notes_router, prefix="/v1", tags=["notes"])
