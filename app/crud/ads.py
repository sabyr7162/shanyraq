from fastapi import HTTPException
from sqlalchemy import select, func

from app.models.ads import ads
from app.models.comments import comments


def create_ad(session, user_id, data: dict):
    data['user_id'] = user_id
    query = ads.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result


def find_ad(session, id):
    query = select(ads).where(ads.c.id == id)
    result = session.execute(query).mappings().fetchone()
    if not result:
        raise HTTPException(status_code=404, detail='Ad not found')
    result = dict(result)

    count_query = select(func.count(comments.c.id)).where(comments.c.ad_id == id)
    total_comments = session.execute(count_query).scalar()
    result['total_comments']= total_comments
    return result


def update_ad(session, id, user_id, data):
    query = ads.update().values(data).where(ads.c.id == id).where(ads.c.user_id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def remove_ad(session, id, user_id):
    query = ads.delete().where(ads.c.id == id).where(ads.c.user_id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount
