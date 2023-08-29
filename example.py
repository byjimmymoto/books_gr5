import asyncio
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, conlist

from beanie import Document, Indexed, init_beanie


class Author(BaseModel):
    name: str


class Genre(BaseModel):
    name: str


class Book(Document):
    title: str                          # You can use normal types just like in pydantic
    subtitle: str
    authors_ids: conlist(str, min_length=None)
    genres_ids: conlist(str, min_length=None)
    published_date: str
    publisher: str
    description: Optional[str] = None
    thumbnail: str


# This is an asynchronous example, so we will access it from an async function
async def example():
    # Beanie uses Motor async client under the hood
    client = AsyncIOMotorClient("mongodb+srv://gr5_books:Hb7j4-2h@books-gr5.slfcocq.mongodb.net/")

    # Initialize beanie with the Product document class
    await init_beanie(database=client.books_gr5, document_models=[Book])

    # categoria1 = Genre(name="Fantasy")
    # categoria2 = Genre(name="Fantasy2")
    categoria = ["categoria1", "categoria2"]
    # autor2 = Author(name="José de Alencar2")
    autor = ["José de Alencar2"]
    product = await Book.find_one(Book.title == "Iracema2")
    if product:
        print("No lo guarda")
    else:
        # Beanie documents work just like pydantic models
        libro = Book(title="Iracema2",subtitle="Iracema",authors_ids=autor,genres_ids=categoria,
                       published_date="2000-03-16",publisher="Oxford University Press",
                       description="Jose de Alencar's prose-poem Iracema, first published in 1865, is a classic of Brazilian"
                                   " literature--perhaps the most widely-known piece of fiction within Brazil, and the most "
                                   "widely-read of Alencar;s many works. Set in the sixteenth century, it is an extremely "
                                   "romantic portrayal of a doomed live between a Portuguese soldier and an Indian maiden. "
                                   "Iracema reflects the gingerly way that mid-nineteenth century Brazil dealt with race "
                                   "mixture and multicultural experience. Precisely because of its nineteenth-century "
                                   "romanticism, Iracema strongly contributed to a Brazilian sense of nationhood--contemporary "
                                   "Brazilian writers and literary critics still cite it as a foundation for their own work.",
                       thumbnail="http://books.google.com/books/content?id=cIumSmjEKkAC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api")
        # And can be inserted into the database
        await libro.insert()

        # You can find documents with pythonic syntax


        # And update them
        await product.set({Book.title:"Iracema4"})


if __name__ == "__main__":
    asyncio.run(example())