# main.py

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from database import Base, engine, scheduler
from routers import auth, users, posts, comments


app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
