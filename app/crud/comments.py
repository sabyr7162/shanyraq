from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy import select

from app.models.comments import comments
from app.models.ads import ads
from app.crud.ads import find_ad


def create_comment(session, id, user_id, comment):
    add_exists= find_ad(session, id)
    if not add_exists:
        raise HTTPException(status_code=404, detail='add does not exist')

    data = {'ad_id': id, 'author_id': user_id, 'content': comment}
    data['created_at'] = datetime.now(timezone.utc)
    query = comments.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def find_comments(session, id):
    add_exists= find_ad(session, id)
    if not add_exists:
        raise HTTPException(status_code=404, detail='add does not exist')
    cols = [col for col in comments.c if col.name != 'ad_id']
    query = select(*cols).where(comments.c.ad_id == id)
    result = session.execute(query).mappings().fetchall()
    return result


def update_comment(session, comment_id, user_id, comment):
    # created_at = datetime.now(timezone.utc)
    data = {
        'content': comment
    }
    query = comments.update().values(data).where(comments.c.id == comment_id).where(comments.c.author_id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def remove_comment(session, comment_id, user_id):
    query = comments.delete().where(comments.c.id == comment_id).where(comments.c.author_id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount