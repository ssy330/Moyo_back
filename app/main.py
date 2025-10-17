from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db
from app import models
from app.routers import auth as auth_router  


from app.database import engine
import os
print(">>> USING DB:", os.path.abspath(engine.url.database))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth API Example")

app.include_router(auth_router.router)  
