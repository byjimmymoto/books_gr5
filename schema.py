from pydantic import BaseModel
from typing import Optional, List, Union, Text


class PublisherBase(BaseModel):
    name: str


class PublisherCreate(PublisherBase):
    name: str


class Publisher(PublisherBase):
    id: Optional[int]
    name: str

    class Config:
        orm_mode = True


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
    title: str
    subtitle: str
    publish_date: int
    description: Text
    thumbnail: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: Optional[int]
    title: str
    subtitle: str
    publish_date: int
    publisher: Publisher
    description: Text
    thumbnail: str
    authors: List[Author] = []
    genre: List[Genre] = []

    class Config:
        orm_mode = True



