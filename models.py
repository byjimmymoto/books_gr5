from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Table, Text, ForeignKey

Base = declarative_base()


book_author_association = Table(
    'book_author',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('book.Id')),
    Column('author_id', Integer, ForeignKey('author.Id'))
)

book_genre_association = Table(
    'book_genre',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('book.Id')),
    Column('genre_id', Integer, ForeignKey('genres.Id'))
)


class Publisher(Base):
    __tablename__ = 'Publisher'

    id = Column('Id', Integer, primary_key=True, autoincrement=True)
    name = Column('Name', String, nullable=False)
    books = relationship("Book", back_populates="publisher")

    def __repr__(self):
        return f'<Publisher {self.id} ({self.name})>'


class Book(Base):
    __tablename__ = "book"
    id = Column('Id', Integer, primary_key=True, index=True)
    title = Column('Title', String,)
    subtitle = Column('SubTitle', String)
    publish_date = Column('PublishDate', Integer)
    publisher = relationship("Publisher", back_populates="book")
    description = Column('Description', Text)
    thumbnail = Column('Thumbnail', String)
    authors = relationship("Author", secondary=book_author_association, back_populates="books")
    genre = relationship("Genre", secondary=book_genre_association, back_populates="book")

    def __repr__(self):
        return f'<Book {self.id} ({self.title} {self.isbn}) {self.pages}>'


class Author(Base):
    __tablename__ = "author"

    id = Column('Id', Integer, primary_key=True, index=True)
    name = Column('Name', String(255), index=True)
    books = relationship("Book", secondary=book_author_association, back_populates="authors")

    def __repr__(self):
        return f'<Author {self.id} ({self.name})>'


class Genre(Base):
    __tablename__ = "genres"

    id = Column('Id', Integer, primary_key=True, index=True)
    name = Column('Name', String(255), index=True)
    books = relationship("Book", secondary=book_genre_association, back_populates="genres")

    def __repr__(self):
        return f'<Genre {self.id} ({self.name})>'



