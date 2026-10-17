from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.users import RegisterUserResponse, RegisterUserRequest, UpadateUserRequest, UpadateUserResponse, UserInfo
from app.crud.users import find_username, create_user, find_user, update_user
from app.database import get_db
from app.core.security import password_hash, create_token, token_verify, bearer


router = APIRouter()


@router.post("/auth/users", response_model=RegisterUserResponse, status_code=status.HTTP_200_OK)
def register(body: RegisterUserRequest, session: Session = Depends(get_db)):
    if find_username(session, body.username):
        raise HTTPException(status_code=403, detail="username already taken")

    hashed_password = password_hash.hash(body.password)
    data = body.model_dump()
    data["hashed_password"] = hashed_password
    data.pop('password')

    result = create_user(session, data)
    user_id = result.inserted_primary_key[0]

    return find_user(session, user_id)


@router.post("/auth/users/login", status_code=status.HTTP_200_OK)
def login(
    session: Annotated[Session, Depends(get_db)],
    username: str = Form(...), 
    password: str = Form(...),
):
    data = find_username(session, username)
    if not data or not password_hash.verify(password, data.hashed_password):
        raise HTTPException(status_code=404, detail="Invalid login or password")
    user_id = data['id']
    token = create_token(user_id)

    return {"access_token": token, "token_type": "bearer"}


@router.patch('/auth/users/me', status_code=status.HTTP_200_OK, response_model = UpadateUserResponse)
def update(
    body: UpadateUserRequest, 
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_db)
):
    payload = token_verify(credentials)
    data = body.model_dump(exclude_unset=True)
    user_id = payload.get('sub')
    query_result = update_user(session, user_id, data)
    if query_result:
        return find_user(session, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


@router.get("/auth/users/me", status_code=status.HTTP_200_OK, response_model=UserInfo)
def get_me(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    payload = token_verify(credentials)
    user = find_user(session, payload['sub'])
    return user