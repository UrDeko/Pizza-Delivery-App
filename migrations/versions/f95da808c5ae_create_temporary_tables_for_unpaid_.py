"""Create temporary tables for unpaid orders

Revision ID: f95da808c5ae
Revises: 40000c8655a4
Create Date: 2024-10-25 14:26:24.092379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f95da808c5ae'
down_revision = '40000c8655a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('unpaid_orders',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unpaid_order_items',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('unpaid_order_id', sa.Integer(), nullable=False),
    sa.Column('pizza_size_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['unpaid_order_id'], ['unpaid_orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('unpaid_order_items')
    op.drop_table('unpaid_orders')
    # ### end Alembic commands ###
