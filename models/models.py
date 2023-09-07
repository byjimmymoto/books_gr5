from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Table, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

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


class TokenSchema(Base):
    __tablename__ = "tokenschema"

    id = Column('Id', Integer, primary_key=True, index=True)
    access_token = Column('access_token', String, nullable=False)
    refresh_token = Column('refresh_token', String, nullable=False)

    def __repr__(self):
        return f'<TokenSchema {self.id} ({self.access_token})>'


class TokenPayload(Base):
    __tablename__ = "tokenpayload"

    id = Column('Id', Integer, primary_key=True, index=True)
    sub = Column('sub', String, nullable=False)
    exp = Column('exp', Integer, nullable=False)

    def __repr__(self):
        return f'<TokenPayload {self.id} ({self.sub})>'


class UserAuth(Base):
    __tablename__ = "userauth"

    id = Column('Id', Integer, primary_key=True, index=True)
    email = Column('email', String, nullable=False)
    password = Column('password', String, nullable=False)

    def __repr__(self):
        return f'<UserAuth {self.id} ({self.email})>'


class UserOut(Base):
    __tablename__ = "userout"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column('email', String, nullable=False)
    password = Column('password', String, nullable=False)

    def __repr__(self):
        return f'<UserOut {self.id} ({self.email})>'
