"""Create table 'orders'

Revision ID: 1941399e9735
Revises: c3e78c2918fa
Create Date: 2024-10-23 13:25:05.685340

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1941399e9735'
down_revision = 'c3e78c2918fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('status', sa.Enum('pending', 'in_transition', 'delivered', name='statusenum'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    sa.Enum('pending', 'in_transition', 'delivered', name='statusenum').drop(op.get_bind())
    # ### end Alembic commands ###
