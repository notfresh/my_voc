"""关联word和解释

Revision ID: 7c2e3dec4856
Revises: ed53cb6cf1cd
Create Date: 2018-06-27 08:33:12.498604

"""

# revision identifiers, used by Alembic.
revision = '7c2e3dec4856'
down_revision = 'ed53cb6cf1cd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'word_interpretation', 'words', ['word_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'word_interpretation', type_='foreignkey')
    # ### end Alembic commands ###
