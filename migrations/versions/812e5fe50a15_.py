"""empty message

Revision ID: 812e5fe50a15
Revises: 
Create Date: 2023-09-26 10:31:35.079310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '812e5fe50a15'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('reference', sa.Integer(), nullable=False),
    sa.Column('package', sa.String(), nullable=False),
    sa.Column('duration', sa.String(), nullable=False),
    sa.Column('price', sa.String(), nullable=False),
    sa.Column('speed', sa.String(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('password'),
    sa.UniqueConstraint('reference'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###