from fastapi import FastAPI

from app.routers.user import router
from app.database.database import dbmanager


app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup():
    await dbmanager.init_db()


@app.on_event("shutdown")
async def shutdown():
    await dbmanager.close()