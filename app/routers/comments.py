from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from app.core.security import token_verify, bearer
from app.database import get_db
from app.crud.comments import create_comment, find_comments, update_comment, remove_comment
from app.schemas.comments import PostCommentRequest, UpdateCommentRequest

router = APIRouter()

@router.post('/shanyraks/{id}/comments', status_code=200)
def post_comment(
    id:int,
    body: PostCommentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db)
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    comment = body.model_dump()['comment']
    query_result = create_comment(session, id, user_id, comment)
    if not query_result:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"detail": "OK"}


@router.get('/shanyraks/{id}/comments')
def get_comments(id:str, session: Annotated[Session, Depends(get_db)]):
    result = find_comments(session, id)
    return {'comments': result}


@router.patch('/shanyraks/{id}/comments/{comment_id}', status_code=200)
def patch_comment(
    comment_id: int,
    body: UpdateCommentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db),
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    content = body.model_dump()['comment']
    query_result = update_comment(session, comment_id, user_id, content)
    if not query_result:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"detail": "OK"}


@router.delete('/shanyraks/{id}/comments/{comment_id}', status_code=200)
def delete_comment(
    comment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db)
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    result = remove_comment(session, comment_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not Found")
    return {"detail": "OK"}
