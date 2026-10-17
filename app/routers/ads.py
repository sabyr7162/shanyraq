from fastapi import APIRouter, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.ads import PostAdsRequest, UpdateAdsRequest
from app.database import get_db
from app.core.security import token_verify, bearer
from app.crud.ads import create_ad, find_ad, update_ad, remove_ad

router = APIRouter(prefix='/shanyraks')



@router.post("", status_code=status.HTTP_200_OK)
def post_ad(
    body: PostAdsRequest,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    payload = token_verify(credentials)
    user_id = payload.get("sub")
    data = body.model_dump()

    result = create_ad(session, user_id, data)
    return result.inserted_primary_key[0]


@router.get("/{id}")
def get_ad(
    id:int,
    session:Session = Depends(get_db), 
):
    return find_ad(session, id)


@router.patch('/{id}')
def change_ad(
    id: int,
    body: UpdateAdsRequest,
    session : Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    data = body.model_dump(exclude_unset=True)
    query_result = update_ad(session, id, user_id, data)
    if query_result:
        return status.HTTP_200_OK
    else:
        return status.HTTP_404_NOT_FOUND


@router.delete('/{id}')
def delete_ad(
    id: int, 
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db)
):
    payload = token_verify(credentials)
    user_id = payload.get('sub')
    query_result = remove_ad(session, id, user_id)
    if query_result:
        return status.HTTP_200_OK
    else:
        return status.HTTP_404_NOT_FOUND