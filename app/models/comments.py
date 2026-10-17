from sqlalchemy import Table, Column, Integer, ForeignKey, Text, DateTime
from app.database import metadata


comments = Table(
    'comments',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('ad_id', Integer, ForeignKey('ads.id'), nullable=False),
    Column('author_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('content', Text, nullable=False),
    Column('created_at', DateTime)

)