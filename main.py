import uvicorn
from fastapi import FastAPI, status, HTTPException, Query
from typing import List
from enum import Enum
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


class Attribute(str, Enum):
    title = "title"
    subtitle = "subtitle"
    publish_date = "publish_date"
    description = "description"
    thumbnail = "thumbnail"


app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


def add_publishers(p):
    db_publisher = ModelPublisher(name=p.name)
    db.session.add(db_publisher)
    db.session.commit()
    return db_publisher


def add_authors(p):
    db_author = ModelAuthor(name=p.name)
    db.session.add(db_author)
    db.session.commit()
    return db_author


def add_genres(p):
    db_genre = ModelGenre(name=p.name)
    db.session.add(db_genre)
    db.session.commit()
    return db_genre


def get_books(skip: int = 0, limit: int = 100):
    return db.session.query(ModelBook).offset(skip).limit(limit).all()


def get_book(book_id: int):
    return db.session.query(ModelBook).filter(ModelBook.id == book_id).first()


def get_delete_book(book_id: int):
    book_delete = db.session.query(ModelBook).filter(ModelBook.id == book_id).first()
    db.session.delete(book_delete)
    db.session.commit()
    return book_delete


def get_update_book(book_id: int, sbooks):
    book = sbooks
    db_publisher = list(map(add_publishers, book.publishers)) if len(book.publishers) > 0 else []
    db_authors = list(map(add_authors, book.authors)) if len(book.authors) > 0 else []
    db_genres = list(map(add_genres, book.genres)) if len(book.genres) > 0 else []
    update_books = {
                      "id": book_id,
                      "title": book.title,
                      "subtitle": book.subtitle,
                      "publish_date": book.publish_date,
                      "description": book.description,
                      "thumbnail": book.thumbnail,
                      "publishers": db_publisher,
                      "authors": db_authors,
                      "genres": db_genres
                    }
    return (db.session.query(ModelBook).filter(ModelBook.id == book_id).
            update(update_books, synchronize_session='evaluate'))


def get_search_book(attribute: str, text_attr: str):
    return db.session.query(ModelBook).filter(eval("ModelBook."+attribute) == text_attr).first()


@app.get("/books/", response_model=List[SchemaBook])
async def read_books(skip: int = 0, limit: int = 100):
    books = get_books(skip=skip, limit=limit)
    return books


@app.get("/book/{book_id}", response_model=SchemaBook)
async def read_book(book_id: int):
    db_book = get_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/book/", response_model=SchemaBook)
async def create_book(book: SchemaBook):
    db_publisher = list(map(add_publishers, book.publishers)) if len(book.publishers) > 0 else []
    db_authors = list(map(add_authors, book.authors)) if len(book.authors) > 0 else []
    db_genres = list(map(add_genres, book.genres)) if len(book.genres) > 0 else []
    db_user = ModelBook(
        title=book.title, subtitle=book.subtitle, publish_date=book.publish_date,
        description=book.description, thumbnail=book.thumbnail,
        publishers=db_publisher, authors=db_authors, genres=db_genres
    )
    db.session.add(db_user)
    db.session.commit()
    return db_user


@app.put("/book/{book_id}", response_model=SchemaBook,status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book: SchemaBook):
    db_book = db.session.query(ModelBook).filter(ModelBook.id == book_id).first()
    db_book.title = book.title
    db_book.subtitle = book.subtitle
    db_book.publish_date = book.publish_date
    db_book.description = book.description
    db_book.thumbnail = book.thumbnail
    db.session.commit()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.delete("/book/{book_id}", response_model=SchemaBook)
async def delete_book(book_id: int):
    db_book = get_delete_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.get("/search_attibutes/", response_model=SchemaBook)
async def read_attribute(text_attr: str, attribute: Attribute = Attribute.title):
    search_book = get_search_book(attribute.value, text_attr)
    if attribute is None or text_attr is None:
        raise HTTPException(status_code=404, detail="Book not found, because no send parameters")
    elif search_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return search_book


@app.post("/author/", response_model=SchemaAuthor)
def create_author(author: SchemaAuthor):
    db_user = ModelAuthor(
        name=author.name
    )
    db.session.add(db_user)
    db.session.commit()
    return db_user


@app.post("/genre/", response_model=SchemaGenre)
def create_genre(genre: SchemaGenre):
    db_user = ModelGenre(
        name=genre.name
    )
    db.session.add(db_user)
    db.session.commit()
    return db_user


@app.post("/publisher/", response_model=SchemaPublisher)
def create_publisher(publisher: SchemaPublisher):
    db_user = ModelPublisher(
        name=publisher.name
    )
    db.session.add(db_user)
    db.session.commit()
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
