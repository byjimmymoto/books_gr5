"""New First migration

Revision ID: 6ab265e9c502
Revises: 
Create Date: 2023-08-30 17:42:21.901598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ab265e9c502'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authors',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_authors_Id'), 'authors', ['Id'], unique=False)
    op.create_table('books',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Title', sa.String(), nullable=False),
    sa.Column('SubTitle', sa.String(), nullable=False),
    sa.Column('PublishDate', sa.Integer(), nullable=False),
    sa.Column('Description', sa.Text(), nullable=True),
    sa.Column('Thumbnail', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_books_Id'), 'books', ['Id'], unique=False)
    op.create_table('genres',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_genres_Id'), 'genres', ['Id'], unique=False)
    op.create_table('publishers',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_publishers_Id'), 'publishers', ['Id'], unique=False)
    op.create_table('book_authors',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['authors.Id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['books.Id'], ),
    sa.PrimaryKeyConstraint('book_id', 'author_id')
    )
    op.create_table('book_genres',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.Id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.Id'], ),
    sa.PrimaryKeyConstraint('book_id', 'genre_id')
    )
    op.create_table('book_publishers',
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('publisher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.Id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publishers.Id'], ),
    sa.PrimaryKeyConstraint('book_id', 'publisher_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('book_publishers')
    op.drop_table('book_genres')
    op.drop_table('book_authors')
    op.drop_index(op.f('ix_publishers_Id'), table_name='publishers')
    op.drop_table('publishers')
    op.drop_index(op.f('ix_genres_Id'), table_name='genres')
    op.drop_table('genres')
    op.drop_index(op.f('ix_books_Id'), table_name='books')
    op.drop_table('books')
    op.drop_index(op.f('ix_authors_Id'), table_name='authors')
    op.drop_table('authors')
    # ### end Alembic commands ###
