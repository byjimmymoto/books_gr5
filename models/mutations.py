from models.mongodb import Book, Author, Genre
from models.graphql import BookInput, AuthorInput, GenreInput, BookType, AuthorType, GenreType
from typing import List


class CreateMutation:

    def add_book(self, book_data: BookInput):
        book = Book.where("title", book_data.title).get()
        if book:
            raise Exception("The book already exists.")

        book = Book()

        book.title = book_data.title
        book.subtitle = book_data.subtitle
        book.published_date = book_data.published_date
        book.publisher = book_data.publisher
        book.description = book_data.description
        book.thumbnail = book_data.thumbnail

        book.save()
        return book

    def add_author(self, author_data: AuthorInput):
        book = Book.find(author_data.name)
        if not book:
            raise Exception("Author not found")
        author = Author()
        author.name = author_data.name
        author.save()
        book.attach("authors_ids", author)
        return author

    def add_genre(self, genre_data: GenreInput):
        book = Book.find(genre_data.name)
        if not book:
            raise Exception("Genre not found")
        genre = Genre()
        genre.name = genre_data.name
        genre.save()
        book.attach("genre_ids", genre)
        return genre


class Queries:
    def get_all_books(self) -> List[BookType]:
        return Book.all()
