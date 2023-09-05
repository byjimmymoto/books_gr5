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
from fastapi.middleware.cors import CORSMiddleware
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
from jwt.utils import get_hashed_password, create_access_token, create_refresh_token, verify_password
from schema import UserOut, UserAuth, TokenSchema, SystemUser
from uuid import uuid4
from jwt.deps import get_current_user
from strawberry.fastapi import GraphQLRouter
from sgraphql.core import Mutation, Query
from celery import Celery
import requests
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Attribute(str, Enum):
    """
    Clase para mostrar atributos en el endpoint search_attributes
    """
    title = "title"
    subtitle = "subtitle"
    publish_date = "publish_date"
    description = "description"
    thumbnail = "thumbnail"


def add_publishers(p):
    """
    Funcion adicionar editores
    :param p: Objeto con el editor
    :return: editor creado en la base de datos
    """
    db_publisher = ModelPublisher(name=p.name)
    db.session.add(db_publisher)
    db.session.commit()
    return db_publisher


def add_authors(p):
    """
    Funcion adicionar autores
    :param p: Objeto con el autor
    :return: autor creado en la base de datos
    """
    db_author = ModelAuthor(name=p.name)
    db.session.add(db_author)
    db.session.commit()
    return db_author


def add_genres(p):
    """
    Funcion adicionar generos
    :param p: Objeto con el genero
    :return: genero creado en la base de datos
    """
    db_genre = ModelGenre(name=p.name)
    db.session.add(db_genre)
    db.session.commit()
    return db_genre


def get_books(skip: int = 0, limit: int = 100):
    """
    Trae los libros de la base de datos local
    :param skip: registro inicio
    :param limit: limite de registros
    :return: objeto con registros de libros base local
    """
    return db.session.query(ModelBook).offset(skip).limit(limit).all()


def get_book(book_id: int):
    """
    Retorna el libro por el id
    :param book_id: id del libro en la base de datos local
    :return: objeto con el libro
    """
    return db.session.query(ModelBook).filter(ModelBook.id == book_id).first()


def get_delete_book(book_id: int):
    """
    Eliminacion de libro por id
    :param book_id: id del libro a borrar
    :return: objeto borrado
    """
    book_delete = db.session.query(ModelBook).filter(ModelBook.id == book_id).first()
    db.session.delete(book_delete)
    db.session.commit()
    return book_delete


def get_update_book(book_id: int, sbooks):
    """
    Libro a actualizar en la base de datos local
    :param book_id: id del libro para actualizar
    :param sbooks: objeto con el contenido de la actualizacion
    :return: objeto actualizado
    """
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
    """
    Busqueda de libro por atributo
    :param attribute: atributo a buscar (title, subtitle, etc)
    :param text_attr: texto del atributo a buscar
    :return: objeto encontrado
    """
    return db.session.query(ModelBook).filter(eval("ModelBook."+attribute) == text_attr).first()


def json_add_email(db_book, email):
    """
    Funcion para adicionar email del usuario que hace la consulta y motor local
    :param db_book: objeto a retornar con los datos del libro
    :param email: email del usuario que genera la consulta
    :return: objeto de respuesta consolidado
    """
    json_compatible_item_data = jsonable_encoder(db_book)
    json_compatible_item_data["usuario"] = email
    json_compatible_item_data["engine"] = "Local"
    return JSONResponse(content=json_compatible_item_data)


def json_add_data(data, email, engine):
    """
    Funcion para adicionar email del usuario que hace la consulta y motor usado
    :param data: objeto a retornar con los datos del libro
    :param email: email del usuario que genera la consulta
    :param engine: motor usado
    :return: objeto de respuesta consolidado
    """
    json_compatible_item_data = jsonable_encoder(data)
    json_compatible_item_data["usuario"] = email
    json_compatible_item_data["engine"] = engine
    return JSONResponse(content=json_compatible_item_data)


def review_response(response):
    try:
        return response
    except KeyError:
        return ""


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.include_router(graphql_app, prefix="/sgraphql", tags=["sgraphql"])

celery = Celery(
    "main",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)


@celery.task
def search_openlibrary(title: str):
    url = "https://openlibrary.org/search.json"
    response = requests.get(f"{url}?title={title}&fields=*,availability&limit=1").json()
    book_response = {
        "title": review_response(response['docs'][0]['title']),
        "subtitle": review_response(response['docs'][0]['title_sort']),
        "publish_date": review_response(response['docs'][0]['publish_year'][0]),
        "description": ' '.join(review_response(response['docs'][0]['subject'])),
        "thumbnail": f"https://covers.openlibrary.org/b/isbn/{review_response(response['docs'][0]['isbn'][1])}-S.jpg",
        "publisher": review_response(response['docs'][0]['publisher_facet'][0]),
        "authors": [
            {
                "name": review_response(response['docs'][0]['author_name'][0])
            }
        ],
        "genres": [
            {
                "name": review_response(response['docs'][0]['subject_key'][0])
            }
        ]
    }
    return book_response


@celery.task
def search_googlebook(title: str):
    url = "https://www.googleapis.com/books/v1/volumes"
    response = requests.get(f"{url}?q={title}&maxResults=1&key=AIzaSyCuJz7LrtNMeH3y4P5Q0BERH4DbPlqbJ5Y").json()
    book_response = {
        "title": review_response(response['items'][0]['volumeInfo']['title']),
        "subtitle": review_response(response['items'][0]['volumeInfo']['title']),
        "publish_date": review_response(response['items'][0]['volumeInfo']['publishedDate']),
        "description": review_response(response['items'][0]['volumeInfo']['description']),
        "thumbnail": review_response(response['items'][0]['volumeInfo']['imageLinks']['smallThumbnail']),
        "publisher": review_response(response['items'][0]['volumeInfo']['publisher']),
        "authors": [
            {
                "name": review_response(response['items'][0]['volumeInfo']['authors'][0])
            }
        ],
        "genres": [
            {
                "name": review_response(response['items'][0]['volumeInfo']['categories'][0])
            }
        ]
    }
    return book_response


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
    return json_add_email(db_book, user.email)


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
    return json_add_email(db_book, user.email)


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
    return json_add_email(db_book, user.email)


@app.delete("/book/{book_id}", response_model=SchemaBook)
async def delete_book(book_id: int, user: SystemUser = Depends(get_current_user)):
    db_book = get_delete_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add_email(db_book, user.email)


@app.get("/search_attibutes/", response_model=SchemaBook)
async def read_attribute(text_attr: str, attribute: Attribute = Attribute.title,
                         user: SystemUser = Depends(get_current_user)):
    search_book = get_search_book(attribute.value, text_attr)
    openlibrary = search_openlibrary.delay(text_attr)
    bookgoogle = search_googlebook.delay(text_attr)
    if attribute is None or text_attr is None:
        raise HTTPException(status_code=404, detail="Book not found, because no send parameters")
    elif search_book is None:
        time.sleep(3)
        if openlibrary.status == "SUCCESS":
            return json_add_data(openlibrary.result, user.email, 'OpenLibrary')
        elif bookgoogle.status == "SUCCESS":
            return json_add_data(bookgoogle.result, user.email, 'GoogleBooks')
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    return json_add_email(search_book, user.email)


@app.post("/author/", response_model=SchemaAuthor)
def create_author(author: SchemaAuthor, user: SystemUser = Depends(get_current_user)):
    db_user = ModelAuthor(
        name=author.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add_email(db_user, user.email)


@app.post("/genre/", response_model=SchemaGenre)
def create_genre(genre: SchemaGenre, user: SystemUser = Depends(get_current_user)):
    db_user = ModelGenre(
        name=genre.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add_email(db_user, user.email)


@app.post("/publisher/", response_model=SchemaPublisher)
def create_publisher(publisher: SchemaPublisher, user: SystemUser = Depends(get_current_user)):
    db_user = ModelPublisher(
        name=publisher.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add_email(db_user, user.email)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
