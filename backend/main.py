from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth
from app.routes import analyze
from app.routes import dashboard


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"]
)


app.include_router(
    analyze.router,
    prefix="/api/analyze",
    tags=["Analyze"]
)


app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@app.get("/")
def home():
    return {
        "status":"Backend running"
    }