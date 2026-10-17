from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.users import users





def create_user(session: Session, data:dict):
    query =  users.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result 


def update_user(session, user_id, data:dict):
    # new_dict = {key:value for key, value in data.items() if value is not None }
    query = users.update().values(data).where(users.c.id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def find_username(session, username):
    query = select(users).where(users.c.username == username)
    result = session.execute(query).mappings().first()
    return result


def find_user(session, user_id):
    selected_cols = [col for col in users.c if col.name != "password"]
    query = select(*selected_cols).where(users.c.id == user_id)
    result = session.execute(query).mappings().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return result