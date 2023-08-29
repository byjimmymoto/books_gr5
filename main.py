import uvicorn
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, Indexed, init_beanie
import strawberry
from typing import Optional, Any, Dict, AnyStr, List, Union
from fastapi import Body, FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fastapi.openapi.utils as fu
from app.tags import tags_metadata
from strawberry.fastapi import GraphQLRouter
from models.mongodb import Book, Author, Genre
from models.graphql import BookType, AuthorType, GenreType
from models.mutations import CreateMutation, Queries


fu.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "error": {"title": "Message", "type": "string"},
    },
}


JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


def get_errors():
    '''
    Respuesta de error unificada
    :return: respuesta 404 con mensaje indicado
    '''
    raise HTTPException(status_code=404, detail="No hay suficiente informacion")


@strawberry.type
class Mutation:
    add_book: BookType = strawberry.mutation(resolver=CreateMutation.add_book)
    add_author: AuthorType = strawberry.mutation(resolver=CreateMutation.add_author)
    add_genre: GenreType = strawberry.mutation(resolver=CreateMutation.add_genre)


@strawberry.type
class Query:
    books: List[BookType] = strawberry.field(resolver=Queries.get_all_books)


# schema = strawberry.Schema(query=Query, mutation=Mutation)
# graphql_app = GraphQLRouter(schema)
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
# app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def app_init():
    app.db = AsyncIOMotorClient("mongodb+srv://gr5_books:Hb7j4-2h@books-gr5.slfcocq.mongodb.net/").books_gr5
    await init_beanie(database=app.db, document_models=[Book])


@app.get("/")
def ping():
    return {"ping": "pong"}


@app.get("/{book_name}")
async def search_book(book_name):
    book = Book.find_one(Book.title == book_name)
    return {book} if book else {}


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
