from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import modular routers
from .routes import detect, graph, influence, predict

app = FastAPI(
    title="Misinformation Analysis System API",
    description="Backend API for the VTU final year project.",
    version="1.0.0"
)

# CORS setup to allow the React frontend to communicate with the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(detect.router, prefix="/api/detect", tags=["Detection"])
app.include_router(graph.router, prefix="/api/graph", tags=["Graph & Propagation"])
app.include_router(influence.router, prefix="/api/influence", tags=["Influence Detection"])
app.include_router(predict.router, prefix="/api/predict", tags=["Spread Prediction"])

@app.get("/")
def root():
    return {"message": "Welcome to the Misinformation Analysis System API. Go to /docs for Swagger UI."}
