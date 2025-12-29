# Project Pratyaharthi

This project is an AI-driven automated video localization suite designed for Chinese Anime Music Video (AMV) edits.

## Setup and Installation

1.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

## Running the Application

1.  **Start the FastAPI server:**
    ```bash
    uvicorn backend.main:app --reload
    ```
    The server will be available at `http://localhost:8000`.

2.  **Open the frontend:**
    Open the `frontend/index.html` file in your web browser.
