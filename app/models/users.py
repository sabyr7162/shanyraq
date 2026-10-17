from sqlalchemy import Table, Column, Integer, String
from app.database import metadata



users = Table(
    'users',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('username', String, unique=True),
    Column('phone', String),
    Column('hashed_password', String),
    Column('name', String),
    Column('city', String)
)
