from typing import List
from fastapi_sqlalchemy import db

from models import Publisher, Author, Genre, Book
from schema import PublisherInput, AuthorInput, GenreInput, BookInput, BookType, GenreType
import strawberry

from strawberry.types import Info


@strawberry.type
class Mutation:
    # @strawberry.mutation
    # async def add_book(self, book_data: BookInput, info: Info) -> str:
    #     book = db.session.query(Book).filter(Book.title == book_data.title).first()
    #     if book:
    #         raise Exception("User already exists")
    #     db_book = Book(
    #         title=book_data.title, subtitle=book_data.subtitle, publish_date=book_data.publish_date,
    #         description=book_data.description, thumbnail=book_data.thumbnail
    #     )
    #     db.session.add(db_book)
    #     db.session.commit()
    #
    #     return db_book
    #
    # @strawberry.mutation
    # async def add_publisher(self, publisher_data: PublisherInput, info: Info) -> str:
    #     publisher = db.session.query(Publisher).filter(Publisher.name == publisher_data.name).first()
    #     if publisher:
    #         raise Exception("Publisher duplicate")
    #     db_publisher = Publisher(
    #         name=publisher_data.name
    #     )
    #     db.session.add(db_publisher)
    #     db.session.commit()
    #     return db_publisher
    #
    #     return post
    #
    # @strawberry.mutation
    # async def add_author(self, author_data: AuthorInput, info: Info) -> str:
    #     author = db.session.query(Author).filter(Author.name == author_data.name).first()
    #     if author:
    #         raise Exception("Author duplicate")
    #     db_author = Author(
    #         name=author_data.name
    #     )
    #     db.session.add(db_author)
    #     db.session.commit()
    #     return db_author

    @strawberry.mutation
    async def add_genre(self, name: str, info: Info) -> str:
        genre = db.session.query(Genre).filter(Genre.name == name).first()
        if genre:
            raise Exception("Genre duplicate")
        db_genre = Genre(
            name=name
        )
        db.session.add(db_genre)
        db.session.commit()
        return db_genre


@strawberry.type
class Query:
    @strawberry.field
    def get_all_books(self, skip: int = 0, limit: int = 100) -> List[BookType]:
        return db.session.query(Book).offset(skip).limit(limit).all()

    @strawberry.field
    def get_single_book(self, title: str) -> BookType:
        book = db.session.query(Book).filter(Book.title == title).first()
        if not book:
            raise Exception("Book not found")
        return book

    @strawberry.field
    def get_single_genre(name: str) -> GenreType:
        genre = db.session.query(Genre).filter(Genre.name == name).first()
        if not genre:
            raise Exception("Genre not found")
        return genre
