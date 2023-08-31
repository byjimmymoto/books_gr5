from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Table, Text, ForeignKey

Base = declarative_base()


book_publisher = Table('book_publishers',
                    Base.metadata,
                    Column('book_id', ForeignKey('books.Id'), primary_key=True),
                    Column('publisher_id', ForeignKey('publishers.Id'), primary_key=True)
                    )


book_author = Table('book_authors',
                    Base.metadata,
                    Column('book_id', ForeignKey('books.Id'), primary_key=True),
                    Column('author_id', ForeignKey('authors.Id'), primary_key=True)
                    )


book_genre = Table('book_genres',
                   Base.metadata,
                   Column('book_id', ForeignKey('books.Id'), primary_key=True),
                   Column('genre_id', ForeignKey('genres.Id'), primary_key=True)
                   )


class Book(Base):
    __tablename__ = "books"
    id = Column('Id', Integer, primary_key=True, index=True)
    title = Column('Title', String, nullable=False)
    subtitle = Column('SubTitle', String, nullable=False)
    publish_date = Column('PublishDate', Integer, nullable=False)
    description = Column('Description', Text)
    thumbnail = Column('Thumbnail', String)
    publishers = relationship("Publisher", secondary=book_publisher, cascade="all,delete", back_populates="books")
    authors = relationship("Author", secondary=book_author, cascade="all,delete", back_populates="books")
    genres = relationship("Genre", secondary=book_genre, cascade="all,delete", back_populates="books")

    def __repr__(self):
        return f'<Book {self.id} ({self.title} {self.isbn}) {self.pages}>'


class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column('Id', Integer, primary_key=True, index=True)
    name = Column('Name', String, nullable=False)
    books = relationship("Book", secondary="book_publishers", back_populates="publishers")

    def __repr__(self):
        return f'<Publisher {self.id} ({self.name})>'


class Author(Base):
    __tablename__ = "authors"

    id = Column('Id', Integer, primary_key=True, index=True)
    name = Column('Name', String, nullable=False)
    books = relationship("Book", secondary="book_authors", back_populates="authors")

    def __repr__(self):
        return f'<Author {self.id} ({self.name})>'


class Genre(Base):
    __tablename__ = "genres"

    id = Column('Id', Integer, primary_key=True, index=True)
    name = Column('Name', String, nullable=False)
    books = relationship("Book", secondary="book_genres", back_populates="genres")

    def __repr__(self):
        return f'<Genre {self.id} ({self.name})>'



