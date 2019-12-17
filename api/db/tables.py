import sqlalchemy as sa
from sqlalchemy import MetaData, ForeignKey

metadata = MetaData()

users = sa.Table(
    'users', metadata,
    sa.Column('id', sa.Integer, primary_key=True, index=True),
    sa.Column('name', sa.String(20), unique=False, nullable=False),
    sa.Column('last_name', sa.String(20), unique=False, nullable=False),
    sa.Column('email', sa.String(50), unique=True, nullable=False),
    sa.Column('password', sa.Text, nullable=False),
)

images = sa.Table(
    'images', metadata,
    sa.Column('id', sa.Integer, primary_key=True, index=True),
    sa.Column('product_id', sa.String(20), unique=False, nullable=False),
    sa.Column('image_url', sa.String, nullable=False),
    sa.Column('user_id', sa.Integer, ForeignKey('users.id', ondelete='CASCADE'))
)