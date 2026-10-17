from sqlalchemy import Table, Column, String, Integer, ForeignKey, Float, Text
from app.database import metadata



ads = Table(
    'ads',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('type', String),
    Column('price', Integer),
    Column('address', String),
    Column('area', Float),
    Column('rooms_count', Integer),
    Column('description', Text)
)