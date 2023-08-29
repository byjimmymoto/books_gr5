import strawberry
from typing import Optional, List


@strawberry.type
class AuthorType:
    name: str


@strawberry.type
class GenreType:
    name: str


@strawberry.type
class BookType:
    title: str  # You can use normal types just like in pydantic
    subtitle: str
    authors_ids: Optional[List[AuthorType]]
    genres_ids: Optional[List[GenreType]]
    published_date: Optional[int]
    publisher: str
    description: Optional[str] = None
    thumbnail: str


@strawberry.type
class BookInput:
    title: str  # You can use normal types just like in pydantic
    subtitle: str
    published_date: int
    publisher: str
    description: str
    thumbnail: str


@strawberry.type
class AuthorInput:
    name: str


@strawberry.type
class GenreInput:
    name: str
