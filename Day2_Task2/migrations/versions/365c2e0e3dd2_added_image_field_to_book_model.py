"""Added image field to Book model

Revision ID: 365c2e0e3dd2
Revises: ca78f9a91e90
Create Date: 2024-09-10 23:37:58.695379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '365c2e0e3dd2'
down_revision = 'ca78f9a91e90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.LargeBinary(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_column('image')

    # ### end Alembic commands ###
