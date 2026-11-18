from fastapi import FastAPI
from sqlmodel import Session , select
from contextlib import asynccontextmanager
from database import create_db_and_tables, engine
from fastapi.middleware.cors import CORSMiddleware

import hashlib
from models import Survey , users

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:3000",  # React development server
    "https://example.com",    # Production frontend
    "*"
] # Define allowed origins (domains that can access your API)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allow these origins
    allow_credentials=True,       # Allow cookies, authentication headers
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/Survey/{id}")
async def read_employee(id):
    with Session(engine) as session:
        print(id,'--------------------------------------------------------------')
        user = session.get(Survey, id)
        return {"message": user}
    

@app.post("/Survey")
async def root(users  : Survey):
    with Session(engine) as session:
        session.add(users)
        session.commit()
        session.refresh(users)
        return {"message": users}


@app.post("/usersRegister")
async def register(user : users):
    with Session(engine) as session:
        if session.exec(select(users).where(users.name == user.name)).first():
            return {"status": "exists"}
        user.password = hashlib.sha256(user.password.encode()).hexdigest()
        session.add(user)
        session.commit()
        return {"status": "success"}


@app.post("/usersLogin")
async def login(user : users):
    with Session(engine) as session:
        found = session.exec(select(users).where(users.name == user.name)).first()
        Input_hashed = hashlib.sha256(user.password.encode()).hexdigest()
        if found and found.password == Input_hashed:
            return {"status": "success"}
        return {"status": "failed"}
