"""empty message

Revision ID: 959bff62220e
Revises: 8cde01a9c42f
Create Date: 2020-12-15 06:04:43.569574

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '959bff62220e'
down_revision = '8cde01a9c42f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project_comment', sa.Column('hide', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project_comment', 'hide')
    # ### end Alembic commands ###
