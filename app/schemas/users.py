from pydantic import BaseModel


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