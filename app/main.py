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
from models.models import Publisher as ModelPublisher
from models.schema import Publisher as SchemaPublisher
from models.models import Author as ModelAuthor
from models.schema import Author as SchemaAuthor
from models.models import Genre as ModelGenre
from models.schema import Genre as SchemaGenre
from models.models import Book as ModelBook
from models.schema import Book as SchemaBook
from dotenv import load_dotenv
from jwt.utils import get_hashed_password, create_access_token, create_refresh_token, verify_password
from models.schema import UserOut, UserAuth, TokenSchema, SystemUser
from uuid import uuid4
from jwt.deps import get_current_user
from strawberry.fastapi import GraphQLRouter
from sgraphql.core import Mutation, Query
from location.tags import description, tags_metadata
from celery_tasks.tasks import search_googlebook, search_openlibrary
import time
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env"))


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


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
    :return: objeto de respuesta
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


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(
    title="Book GR5",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/documentation",
    redoc_url=None,
    contact={
        "name": "Jaime Alberto Martínez",
        "url": "https://www.linkedin.com/in/jaime-alberto-martinez-martinez/",
        "email": "jimmymoto26@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.include_router(graphql_app, prefix="/sgraphql", tags=["sgraphql"])


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    """
    Redirección a url de openapi con nombre personalizado
    :return: url redirigida
    """
    logger.info("redireccion a url documentacion")
    return RedirectResponse(url='/documentation')


@app.post('/signup', summary="Crear usuario nuevo", response_model=UserOut, tags=['JWT'])
async def create_user(data: UserAuth):
    """
    Creación de usuario nuevo
    :param data: datos de autenticación
    :return: usuario creado
    """
    logger.info("creacion de usuario")
    from models.models import UserOut
    user = db.session.query(UserOut).filter(UserOut.email == data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario existente"
        )
    user = UserOut(
        id=str(uuid4()), email=data.email, password=get_hashed_password(data.password)
    )
    db.session.add(user)
    db.session.commit()
    return user


@app.post('/login', summary="Crear acceso y refrescar token por usuario", response_model=TokenSchema, tags=['JWT'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de logueo de usuario y refresco de token
    :param form_data: datos de usuario
    :return: access token y refresh token
    """
    logger.info("inicio sesion usuario")
    from models.models import UserOut
    user = db.session.query(UserOut).filter(UserOut.email == form_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email o password incorrecto"
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email o password incorrecto"
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@app.get('/me', summary='Detalles de usuario logueado', response_model=UserOut, tags=['JWT'])
async def get_me(user: SystemUser = Depends(get_current_user)):
    """
    Endpoint de prueba de funcionamiento de acceso JWT
    :param user: Consulta los datos almacenados del usuario
    :return: email del usuario
    """
    logger.info("Consulta funcionamiento usuario")
    return user


@app.get("/books/", response_model=List[SchemaBook], response_model_exclude_unset=True, tags=['Book_local'])
async def read_books(skip: int = 0, limit: int = 100, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint de busqueda de libros creados en la base de datos local
    :param skip: registro de inicio
    :param limit: limite de registros
    :param user: usuario que usa el endpoint
    :return: listado de libros en base de datos local
    """
    books = get_books(skip=skip, limit=limit)
    json_compatible_item_data = jsonable_encoder(books + [user.email])
    return JSONResponse(content=json_compatible_item_data)


@app.get("/book/{book_id}", response_model=SchemaBook, tags=['Book_local'])
async def read_book(book_id: int, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint para consulta de libro por id
    :param book_id: id del libro
    :param user: usuario que realiza la consulta
    :return: objeto con el libro
    """
    db_book = get_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add_email(db_book, user.email)


@app.post("/book/", response_model=SchemaBook, tags=['Book_local'])
async def create_book(book: SchemaBook, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint de creacion de libro
    :param book: Diccionario con los datos del libro a crear
    :param user: usuario que realiza la consulta
    :return: objeto con el libro
    """
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


@app.put("/book/{book_id}", response_model=SchemaBook, status_code=status.HTTP_200_OK, tags=['Book_local'])
async def update_book(book_id: int, book: SchemaBook, user: SystemUser = Depends(get_current_user)):
    """
    Enpoint con la actualizacion de libro existente
    :param book_id: id libro a actualizar
    :param book: diccionario con los datos para actualizar
    :param user: usuario que genera la actualización
    :return: objeto con el libro
    """
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


@app.delete("/book/{book_id}", response_model=SchemaBook, tags=['Book_local'])
async def delete_book(book_id: int, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint para eliminación de libro por id
    :param book_id: id del libro
    :param user: usuario que genera la eliminación
    :return: objeto eliminado
    """
    db_book = get_delete_book(book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return json_add_email(db_book, user.email)


@app.get("/search_attibutes/", response_model=SchemaBook, tags=['API_Books'])
async def read_attribute(text_attr: str, attribute: Attribute = Attribute.title,
                         user: SystemUser = Depends(get_current_user)):
    """
    Endpoint para consulta de libro por medio de parametros y que usa dos API si no esta local
    :param text_attr: Atributo de texto a buscar
    :param attribute: tipo de atributo a buscar
    :param user: usuario que genera la busqueda
    :return: objeto con el registro encontrado
    """
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


@app.post("/author/", response_model=SchemaAuthor, tags=['Book_local'])
def create_author(author: SchemaAuthor, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint para crear autor
    :param author: diccionario con los datos del autor
    :param user: usuario que realiza el uso del endpoint
    :return: objeto creado
    """
    db_user = ModelAuthor(
        name=author.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add_email(db_user, user.email)


@app.post("/genre/", response_model=SchemaGenre, tags=['Book_local'])
def create_genre(genre: SchemaGenre, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint para crear genero
    :param genre: diccionario con los datos del genero
    :param user: usuario que realiza el uso del endpoint
    :return: objeto creado
    """
    db_user = ModelGenre(
        name=genre.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add_email(db_user, user.email)


@app.post("/publisher/", response_model=SchemaPublisher, tags=['Book_local'])
def create_publisher(publisher: SchemaPublisher, user: SystemUser = Depends(get_current_user)):
    """
    Endpoint para crear editor
    :param publisher: diccionario con los datos del editor
    :param user: usuario que realiza el uso del endpoint
    :return: objeto creado
    """
    db_user = ModelPublisher(
        name=publisher.name
    )
    db.session.add(db_user)
    db.session.commit()
    return json_add_email(db_user, user.email)



