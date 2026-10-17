from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from pathlib import Path
from pwdlib import PasswordHash
from sqlalchemy import Table, Column, MetaData, Integer, String, JSON, create_engine, inspect, select, ForeignKey, Float, Text, DateTime, func
from sqlalchemy.orm import Session, sessionmaker
from typing import Annotated
from datetime import datetime, timezone, timedelta
import jwt 

database_path = Path(__file__).resolve().parents[1]/"shanyraq.db"
engine = create_engine(f'sqlite:///{database_path}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

password_hash = PasswordHash.recommended()
SECRET_KEY = "sectrdlf;askdgkasldgklsd,lgds,rweasdf;elwr,dasf,dfghjkkoproewr"
ALGORITHM = "HS256"
bearer = HTTPBearer()


app = FastAPI()



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


comments = Table(
    'comments',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('ad_id', Integer, ForeignKey('ads.id'), nullable=False),
    Column('author_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('content', Text, nullable=False),
    Column('created_at', DateTime)

)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def initialize_database():
    with engine.begin() as connection:
        metadata.create_all(connection)


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


def create_ad(session, user_id, data: dict):
    data['user_id'] = user_id
    query = ads.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result


def find_ad(session, id):
    query = select(ads).where(ads.c.id == id)
    result = session.execute(query).mappings().fetchone()
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


def create_comment(session, id, user_id, comment):
    data = {'ad_id': id, 'author_id': user_id, 'content': comment}
    data['created_at'] = datetime.now(timezone.utc)
    query = comments.insert().values(data)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def find_comments(session, id):
    cols = [col for col in comments.c if col.name != 'ad_id']
    query = select(*cols).where(comments.c.ad_id == id)
    result = session.execute(query).mappings().fetchall()
    return result


def update_comment(session, id, user_id, comment):
    created_at = datetime.now(timezone.utc)
    data = {
        'content': comment,
        'created_at': created_at
    }
    query = comments.update().values(data).where(comments.c.id == id).where(comments.c.author_id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def remove_comment(session, id, user_id):
    query = comments.delete().where(comments.c.id == id).where(comments.c.author_id == user_id)
    result = session.execute(query)
    session.commit()
    return result.rowcount


def create_token(user_id):
    data = {
        'sub': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def token_verify(credentials):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload


class UpadateUserRequest(BaseModel):
    phone: str | None = None
    name: str | None = None
    city: str| None = None


class UpadateUserResponse(BaseModel):
    phone: str
    name: str
    city: str


class RegisterUserRequest(BaseModel):
    username: str
    phone: str
    password: str
    name: str
    city: str


class RegisterUserResponse(BaseModel):
    username: str
    phone: str
    name: str
    city: str


class UserInfo(BaseModel):
    id: int
    username: str
    phone: str
    name: str
    city: str


class PostAdsRequest(BaseModel):
    type: str
    price: float
    address: str
    area: float
    rooms_count: int
    description: str


class UpdateAdsRequest(BaseModel):
    type: str | None = None
    price: float| None = None
    address: str| None = None
    area: float| None = None
    rooms_count: int| None = None
    description: str| None = None


@app.post("/auth/users", response_model=RegisterUserResponse, status_code=status.HTTP_200_OK)
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


@app.post("/auth/users/login", status_code=status.HTTP_200_OK)
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


@app.patch('/auth/users/me', status_code=status.HTTP_200_OK, response_model = UpadateUserResponse)
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


@app.get("/auth/users/me", status_code=status.HTTP_200_OK, response_model=UserInfo)
def get_me(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    payload = token_verify(credentials)
    user = find_user(session, payload['sub'])
    return user


@app.post("/shanyraks", status_code=status.HTTP_200_OK)
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


@app.get("/shanyraks/{id}")
def get_ad(
    id:int,
    session:Session = Depends(get_db), 
):
    return find_ad(session, id)


@app.patch('/shanyraks/{id}')
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


@app.delete('/shanyraks/{id}')
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


@app.post('/shanyraks/{id}/comments')
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


@app.get('/shanyraks/{id}/comments')
def get_comments(id:str, session: Annotated[Session, Depends(get_db)]):
    result = find_comments(session, id)
    return {'comments': result}


@app.patch('/shanyraks/{id}/comments/{comment_id}')
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


@app.delete('/shanyraks/{id}/comments/{comment_id}')
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





initialize_database()   
    




