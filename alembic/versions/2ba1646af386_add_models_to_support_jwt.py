"""Add models to support JWT

Revision ID: 2ba1646af386
Revises: ab88b18f64fb
Create Date: 2023-09-01 16:58:49.395476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ba1646af386'
down_revision: Union[str, None] = 'ab88b18f64fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tokenpayload',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('sub', sa.String(), nullable=False),
    sa.Column('exp', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_tokenpayload_Id'), 'tokenpayload', ['Id'], unique=False)
    op.create_table('tokenschema',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(), nullable=False),
    sa.Column('refresh_token', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_tokenschema_Id'), 'tokenschema', ['Id'], unique=False)
    op.create_table('userauth',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_index(op.f('ix_userauth_Id'), 'userauth', ['Id'], unique=False)
    op.create_table('userout',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userout')
    op.drop_index(op.f('ix_userauth_Id'), table_name='userauth')
    op.drop_table('userauth')
    op.drop_index(op.f('ix_tokenschema_Id'), table_name='tokenschema')
    op.drop_table('tokenschema')
    op.drop_index(op.f('ix_tokenpayload_Id'), table_name='tokenpayload')
    op.drop_table('tokenpayload')
    # ### end Alembic commands ###
