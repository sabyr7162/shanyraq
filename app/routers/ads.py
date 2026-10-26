from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.schemas.ads import PostAdsRequest, UpdateAdsRequest
from app.database import get_db
from app.core.security import token_verify, oauth2_scheme
from app.crud.ads import create_ad, find_ad, update_ad, remove_ad

router = APIRouter(prefix='/shanyraks')



@router.post("", status_code=status.HTTP_200_OK)
def post_ad(
    body: PostAdsRequest,
    session: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    payload = token_verify(token)
    user_id = payload.get("sub")
    data = body.model_dump()

    result = create_ad(session, user_id, data)
    return {'id': result.inserted_primary_key[0]}


@router.get("/{id}")
def get_ad(
    id:int,
    session:Session = Depends(get_db), 
):
    result =  find_ad(session, id)
    return result


@router.patch('/{id}')
def change_ad(
    id: int,
    body: UpdateAdsRequest,
    session : Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    payload = token_verify(token)
    user_id = payload.get('sub')
    data = body.model_dump(exclude_unset=True)
    query_result = update_ad(session, id, user_id, data)
    if not query_result:
        raise HTTPException(status_code=404, detail='Ad not found or unauthorized')
    return status.HTTP_200_OK


@router.delete('/{id}')
def delete_ad(
    id: int, 
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db)
):
    payload = token_verify(token)
    user_id = payload.get('sub')
    query_result = remove_ad(session, id, user_id)
    if not query_result:
        raise HTTPException(status_code=404, detail='Ad not found or unauthorized')
    return status.HTTP_200_OK