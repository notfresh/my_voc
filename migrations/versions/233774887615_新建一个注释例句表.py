"""新建一个注释例句表

Revision ID: 233774887615
Revises: cc0e9db443ea
Create Date: 2018-06-29 21:25:23.563921

"""

# revision identifiers, used by Alembic.
revision = '233774887615'
down_revision = 'cc0e9db443ea'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('word_interpretation_examples',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('interpretation_id', sa.Integer(), nullable=True),
    sa.Column('example', sa.String(length=1024), nullable=False),
    sa.ForeignKeyConstraint(['interpretation_id'], ['word_interpretation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_word_interpretation_examples_interpretation_id'), 'word_interpretation_examples', ['interpretation_id'], unique=False)
    op.drop_table('word_interpretation_example')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('word_interpretation_example',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('interpretation_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('example', mysql.VARCHAR(length=1024), nullable=False),
    sa.ForeignKeyConstraint(['interpretation_id'], ['word_interpretation.id'], name='word_interpretation_example_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.drop_index(op.f('ix_word_interpretation_examples_interpretation_id'), table_name='word_interpretation_examples')
    op.drop_table('word_interpretation_examples')
    # ### end Alembic commands ###
