from fastapi import FastAPI
import os
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from db import init_db
from sockets import router, manager

load_dotenv()
origins = os.getenv("CORS_ORIGINS", "*").split(",")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!"}


@app.on_event("startup")
def on_startup():
    init_db()
    manager.load_solutions_from_db()


app.include_router(router)
