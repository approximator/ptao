"""Added settings table

Revision ID: 8abc70088073
Revises: 49567e164192
Create Date: 2018-08-17 15:33:35.039703

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8abc70088073'
down_revision = '49567e164192'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('status_and_settings', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('pause_update', sa.Boolean(), nullable=False), sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('status_and_settings')
