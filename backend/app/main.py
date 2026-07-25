from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import client

try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB Atlas")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)

# Import modular routers
from .routes import (
    detect,
    graph,
    influence,
    predict,
    fact_verify,
    ocr,
    analyze,
    auth          # <-- NEW
)

app = FastAPI(
    title="Misinformation Analysis System API",
    description="Backend API for the VTU final year project.",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Register API Routes
# -----------------------------

app.include_router(
    auth.router              # <-- NEW
)

app.include_router(
    analyze.router,
    prefix="/api/analyze",
    tags=["Complete Analysis"]
)

app.include_router(
    detect.router,
    prefix="/api/detect",
    tags=["Detection"]
)

app.include_router(
    fact_verify.router,
    prefix="/api/fact-verify",
    tags=["Fact Verification"]
)

app.include_router(
    ocr.router,
    prefix="/api/ocr",
    tags=["OCR"]
)

app.include_router(
    predict.router,
    prefix="/api/predict",
    tags=["Spread Prediction"]
)

app.include_router(
    graph.router,
    prefix="/api/graph",
    tags=["Graph & Propagation"]
)

app.include_router(
    influence.router,
    prefix="/api/influence",
    tags=["Influence Detection"]
)

# -----------------------------
# Root Endpoint
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to the Misinformation Analysis System API. Go to /docs for Swagger UI."
    }