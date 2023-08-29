from typing import Optional, List
from pydantic import BaseModel, conlist
from beanie import Document


class Author(BaseModel):
    name: str


class Genre(BaseModel):
    name: str


class Book(Document):
    title: str                          # You can use normal types just like in pydantic
    subtitle: str
    authors_ids: Optional[List[Author]]
    genres_ids: Optional[List[Genre]]
    published_date: Optional[int]
    publisher: str
    description: Optional[str] = None
    thumbnail: str
