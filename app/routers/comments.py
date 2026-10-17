from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.security import token_verify, bearer
from app.database import get_db
from app.crud.comments import create_comment, find_comments, update_comment, remove_comment

router = APIRouter()

@router.post('/shanyraks/{id}/comments')
def post_comment(
    id:int,
    comment: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db)
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    query_result = create_comment(session, id, user_id, comment)
    if query_result:
        return status.HTTP_200_OK
    else:
        return status.HTTP_404_NOT_FOUND


@router.get('/shanyraks/{id}/comments')
def get_comments(id:str, session: Annotated[Session, Depends(get_db)]):
    result = find_comments(session, id)
    return {'comments': result}


@router.patch('/shanyraks/{id}/comments/{comment_id}')
def patch_comment(
    comment_id: int,
    content: str,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db),
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    query_result = update_comment(session, comment_id, user_id, content)
    if query_result:
        return status.HTTP_200_OK
    return status.HTTP_304_NOT_MODIFIED


@router.delete('/shanyraks/{id}/comments/{comment_id}')
def delete_comment(
    comment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db)
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    result = remove_comment(session, comment_id, user_id)
    if result:
        return status.HTTP_200_OK
    return status.HTTP_404_NOT_FOUND