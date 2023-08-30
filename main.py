import uvicorn
from fastapi import FastAPI

import os
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db
from models import Publisher as ModelPublisher
from schema import Publisher as SchemaPublisher
from models import Author as ModelAuthor
from schema import Author as SchemaAuthor
from models import Genre as ModelGenre
from schema import Genre as SchemaGenre
from models import Book as ModelBook
from schema import Book as SchemaBook
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


@app.post("/book/", response_model=SchemaBook)
def create_book(book: SchemaBook):
    db_user = ModelBook(
        title=book.title, subtitle=book.subtitle, publish_date=book.publish_date, publisher=book.publisher,
        description=book.description, thumbnail=book.thumbnail, authors=book.authors, genre=book.genre
    )
    db.session.add(db_user)
    db.session.commit()
    return db_user


@app.post("/author/", response_model=SchemaAuthor)
def create_author(author: SchemaAuthor):
    db_user = ModelAuthor(
        name=author.name
    )
    db.session.add(db_user)
    db.session.commit()
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
