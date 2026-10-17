from pydantic import BaseModel





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