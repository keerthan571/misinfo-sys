# AI-Driven Misinformation Analysis System

This is a clean, modular, and beginner-friendly boilerplate for your VTU final year project.

## Project Structure

- `backend/`: FastAPI application containing all the ML, NLP, Graph, and OCR logic.
- `frontend/`: React + Vite application for the user interface.

## Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- Tesseract OCR installed on your system (for the OCR module).
- (Optional) Neo4j Desktop or AuraDB for graph database.

## Setup Instructions

### 1. Backend Setup

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. You can view the API documentation (Swagger UI) at: `http://localhost:8000/docs`

### 2. Frontend Setup

1. Open a **new** terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. The application will be running at `http://localhost:5173/` (or the port shown in your terminal).

## Modules Overview

- **NLP Service (`backend/app/services/nlp_service.py`)**: Uses Scikit-Learn (TF-IDF + Logistic Regression) to detect fake news.
- **Graph Service (`backend/app/services/graph_service.py`)**: Placeholder for Neo4j queries to track the propagation of posts.
- **Influence Service (`backend/app/services/influence_service.py`)**: Logic for identifying key spreaders in the network.
- **Prediction Service (`backend/app/services/prediction_service.py`)**: Predictive modeling placeholder to forecast reach.
- **OCR Service (`backend/app/services/ocr_service.py`)**: Uses Tesseract OCR to extract text from images.

**Good luck with your project viva!** This boilerplate is designed to be easily extensible. Read the comments in the code to understand where you need to implement your custom algorithms.
