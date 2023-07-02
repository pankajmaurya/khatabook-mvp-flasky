"""Initial migration.

Revision ID: 364e376254e7
Revises: 
Create Date: 2023-07-02 21:23:48.380581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '364e376254e7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('khata_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('farmer_name', sa.String(length=100), nullable=False),
    sa.Column('crop_kind', sa.String(length=100), nullable=False),
    sa.Column('locality', sa.String(length=100), nullable=False),
    sa.Column('farm_area', sa.Float(), nullable=False),
    sa.Column('billed_amount', sa.Float(), nullable=False),
    sa.Column('date_of_activity', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('khata_entry_id', sa.Integer(), nullable=False),
    sa.Column('payment_date', sa.DateTime(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['khata_entry_id'], ['khata_entry.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    op.drop_table('khata_entry')
    # ### end Alembic commands ###
