"""change table move set_id from mywords to words

Revision ID: 1b6435c8f6e4
Revises: d80f981410e8
Create Date: 2018-07-12 18:43:00.803479

"""

# revision identifiers, used by Alembic.
revision = '1b6435c8f6e4'
down_revision = 'd80f981410e8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('words', sa.Column('set_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_words_set_id'), 'words', ['set_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_words_set_id'), table_name='words')
    op.drop_column('words', 'set_id')
    # ### end Alembic commands ###
