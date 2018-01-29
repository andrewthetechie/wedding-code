"""empty message

Revision ID: b2e4ebe53383
Revises: 41d203d5bb31
Create Date: 2018-01-28 21:27:13.459050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2e4ebe53383'
down_revision = '41d203d5bb31'
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
    sa.Column('rsvp_notes', sa.Text(), nullable=True),
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
