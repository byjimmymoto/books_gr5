from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey

Base = declarative_base()


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
    authors = relationship("Author", secondary='BookAuthor', back_populates="book")

    def __repr__(self):
        return f'<Book {self.id} ({self.title} {self.isbn}) {self.pages}>'


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    books = relationship("Book", secondary='BookAuthor', back_populates="author")

    def __repr__(self):
        return f'<Author {self.id} ({self.name})>'


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    books = relationship("Book", secondary='BookGenre', back_populates="genre")

    def __repr__(self):
        return f'<Genre {self.id} ({self.name})>'



