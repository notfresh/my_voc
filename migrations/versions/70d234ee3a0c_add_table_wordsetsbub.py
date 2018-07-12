"""add table  wordsetsbub 

Revision ID: 70d234ee3a0c
Revises: 1b6435c8f6e4
Create Date: 2018-07-12 23:30:51.164924

"""

# revision identifiers, used by Alembic.
revision = '70d234ee3a0c'
down_revision = '1b6435c8f6e4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('word_set_sub',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('word_id', sa.Integer(), nullable=True),
    sa.Column('set_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_word_set_sub_set_id'), 'word_set_sub', ['set_id'], unique=False)
    op.create_index(op.f('ix_word_set_sub_word_id'), 'word_set_sub', ['word_id'], unique=False)
    op.add_column('word_set', sa.Column('set_title', sa.String(length=128), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('word_set', 'set_title')
    op.drop_index(op.f('ix_word_set_sub_word_id'), table_name='word_set_sub')
    op.drop_index(op.f('ix_word_set_sub_set_id'), table_name='word_set_sub')
    op.drop_table('word_set_sub')
    # ### end Alembic commands ###
