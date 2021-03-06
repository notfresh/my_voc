"""add passage_html

Revision ID: dc0b6b28fb75
Revises: 43c8b531af6b
Create Date: 2018-07-11 21:07:32.205230

"""

# revision identifiers, used by Alembic.
revision = 'dc0b6b28fb75'
down_revision = '43c8b531af6b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('passages', sa.Column('passage_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('passages', 'passage_html')
    # ### end Alembic commands ###
