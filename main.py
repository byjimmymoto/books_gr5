import uvicorn
import os
import strawberry
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List
from enum import Enum
from models import Publisher as ModelPublisher
from schema import Publisher as SchemaPublisher
from models import Author as ModelAuthor
from schema import Author as SchemaAuthor
from models import Genre as ModelGenre
from schema import Genre as SchemaGenre
from models import Book as ModelBook
from schema import Book as SchemaBook
from dotenv import load_dotenv
from utils import get_hashed_password, create_access_token, create_refresh_token, verify_password
from schema import UserOut, UserAuth, TokenSchema, SystemUser
from uuid import uuid4
from deps import get_current_user
from strawberry.fastapi import GraphQLRouter
from core import Mutation, Query
from celery import Celery

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Attribute(str, Enum):
    title = "title"
    subtitle = "subtitle"
    publish_date = "publish_date"
    description = "description"
    thumbnail = "thumbnail"


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


def json_add(db_book, email):
    json_compatible_item_data = jsonable_encoder(db_book)
    json_compatible_item_data["usuario"] = email
    return JSONResponse(content=json_compatible_item_data)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.include_router(graphql_app, prefix="/graphql")

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)


@celery.task
def divide(x, y):
    import time
    time.sleep(50)
    return x / y


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    # querying database to check if user already exist
    from models import UserOut
    user = db.session.query(UserOut).filter(UserOut.email == data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = UserOut(
        id=str(uuid4()), email=data.email, password=get_hashed_password(data.password)
    )
    db.session.add(user)
    db.session.commit() # saving user to database
    return user


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    from models import UserOut
    user = db.session.query(UserOut).filter(UserOut.email == form_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user


@app.get("/books/", response_model=List[SchemaBook], response_model_exclude_unset=True)
async def read_books(skip: int = 0, limit: int = 100, user: SystemUser = Depends(get_current_user)):
    books = get_books(skip=skip, limit=limit)
    json_compatible_item_data = jsonable_encoder(books + [user.email])
    return JSONResponse(content=json_compatible_item_data)


@app.get("/book/{book_id}", response_model=SchemaBook)
async def read_book(book_id: int, user: SystemUser = Depends(get_current_user)):
    db_book = get_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add(db_book, user.email)


@app.post("/book/", response_model=SchemaBook)
async def create_book(book: SchemaBook, user: SystemUser = Depends(get_current_user)):
    db_publisher = list(map(add_publishers, book.publishers)) if len(book.publishers) > 0 else []
    db_authors = list(map(add_authors, book.authors)) if len(book.authors) > 0 else []
    db_genres = list(map(add_genres, book.genres)) if len(book.genres) > 0 else []
    db_book = ModelBook(
        title=book.title, subtitle=book.subtitle, publish_date=book.publish_date,
        description=book.description, thumbnail=book.thumbnail,
        publishers=db_publisher, authors=db_authors, genres=db_genres
    )
    db.session.add(db_book)
    db.session.commit()
    return json_add(db_book, user.email)


@app.put("/book/{book_id}", response_model=SchemaBook,status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book: SchemaBook, user: SystemUser = Depends(get_current_user)):
    db_book = db.session.query(ModelBook).filter(ModelBook.id == book_id).first()
    db_book.title = book.title
    db_book.subtitle = book.subtitle
    db_book.publish_date = book.publish_date
    db_book.description = book.description
    db_book.thumbnail = book.thumbnail
    db.session.commit()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add(db_book, user.email)


@app.delete("/book/{book_id}", response_model=SchemaBook)
async def delete_book(book_id: int, user: SystemUser = Depends(get_current_user)):
    db_book = get_delete_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add(db_book, user.email)


@app.get("/search_attibutes/", response_model=SchemaBook)
async def read_attribute(text_attr: str, attribute: Attribute = Attribute.title,
                         user: SystemUser = Depends(get_current_user)):
    search_book = get_search_book(attribute.value, text_attr)
    if attribute is None or text_attr is None:
        raise HTTPException(status_code=404, detail="Book not found, because no send parameters")
    elif search_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add(search_book, user.email)


@app.post("/author/", response_model=SchemaAuthor)
def create_author(author: SchemaAuthor, user: SystemUser = Depends(get_current_user)):
    db_user = ModelAuthor(
        name=author.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add(db_user, user.email)


@app.post("/genre/", response_model=SchemaGenre)
def create_genre(genre: SchemaGenre, user: SystemUser = Depends(get_current_user)):
    db_user = ModelGenre(
        name=genre.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add(db_user, user.email)


@app.post("/publisher/", response_model=SchemaPublisher)
def create_publisher(publisher: SchemaPublisher, user: SystemUser = Depends(get_current_user)):
    db_user = ModelPublisher(
        name=publisher.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add(db_user, user.email)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
