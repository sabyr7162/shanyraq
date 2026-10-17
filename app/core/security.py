from pwdlib import PasswordHash
from fastapi.security import HTTPBearer
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta

import jwt


password_hash = PasswordHash.recommended()
SECRET_KEY = "sectrdlf;askdgkasldgklsd,lgds,rweasdf;elwr,dasf,dfghjkkoproewr"
ALGORITHM = "HS256"
bearer = HTTPBearer()


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