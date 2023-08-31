from pydantic import BaseModel
from typing import Optional, List, Union, Text


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





