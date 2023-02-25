from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from psycopg2.errorcodes import UNIQUE_VIOLATION

from .routers import post, user, auth, vote

app = FastAPI()



origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://google.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)

app.include_router(post.router)

app.include_router(auth.router)

app.include_router(vote.router)



@app.get("/")
def root():
    return {"message": "Hello World######"}






