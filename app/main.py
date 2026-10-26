from fastapi import FastAPI

from .routers.users import router as UserRouter
from .routers.ads import router as AdsRouter
from .routers.comments import router as CommentsRouter
from .database import initialize_database


app = FastAPI()
app.include_router(UserRouter)
app.include_router(AdsRouter)
app.include_router(CommentsRouter)
initialize_database()   
    




