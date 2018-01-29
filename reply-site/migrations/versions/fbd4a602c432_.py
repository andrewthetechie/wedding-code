"""empty message

Revision ID: fbd4a602c432
Revises: af115760e99d
Create Date: 2018-01-28 14:24:26.671041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbd4a602c432'
down_revision = 'af115760e99d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('total_attendees', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.String(length=255), nullable=True),
    sa.Column('email_address', sa.String(length=255), nullable=True),
    sa.Column('physical_address', sa.String(length=255), nullable=True),
    sa.Column('date_saved', sa.Boolean(), nullable=True),
    sa.Column('rsvp', sa.Boolean(), nullable=True),
    sa.Column('stop_notifications', sa.Boolean(), nullable=True),
    sa.Column('last_notified', sa.DateTime(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('guests')
    # ### end Alembic commands ###