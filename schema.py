from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List, Text
import strawberry


class PublisherBase(BaseModel):
    id: Optional[int]
    name: str

    class Config:
        orm_mode = True


class PublisherCreate(PublisherBase):
    pass


class Publisher(PublisherBase):
    name: str


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    name: str


class Author(AuthorBase):
    id: Optional[int]
    name: str

    class Config:
        orm_mode = True


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    name: str


class Genre(GenreBase):
    id: Optional[int]
    name: str

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: Optional[int]
    title: str
    subtitle: str
    publish_date: int
    description: Text
    thumbnail: str

    class Config:
        orm_mode = True


class BookCreate(BookBase):
    pass


class Book(BookBase):
    publishers: List[Publisher]
    authors: List[Author]
    genres: List[Genre]


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserOut(BaseModel):
    id: UUID
    email: str


class SystemUser(UserOut):
    password: str


@strawberry.type
class PublisherType:
    id: int
    name: str


@strawberry.type
class PublisherInput:
    name: str


@strawberry.type
class AuthorType:
    id: int
    name: str


@strawberry.type
class AuthorInput:
    name: str


@strawberry.type
class GenreType:
    id: int
    name: str


@strawberry.type
class GenreInput:
    name: str


@strawberry.type
class BookType:
    id: int
    title: str
    subtitle: str
    publish_date: int
    description: Text
    thumbnail: str
    publishers: Optional[List[PublisherType]]
    authors: Optional[List[AuthorType]]
    genres: Optional[List[GenreType]]


@strawberry.type
class BookInput:
    title: str
    subtitle: str
    publish_date: int
    description: Text
    thumbnail: str
