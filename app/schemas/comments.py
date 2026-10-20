from pydantic import BaseModel


class PostCommentRequest(BaseModel):
    comment: str


class UpdateCommentRequest(BaseModel):
    comment: str