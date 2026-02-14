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

1.  **Set the Groq API Key:**
    This application requires an API key from Groq to parse commands. You must set it as an environment variable.

    On **Linux/macOS**:
    ```bash
    export GROQ_API_KEY="YOUR_API_KEY_HERE"
    ```

    On **Windows (Command Prompt)**:
    ```bash
    set GROQ_API_KEY="YOUR_API_KEY_HERE"
    ```

    On **Windows (PowerShell)**:
    ```powershell
    $env:GROQ_API_KEY="YOUR_API_KEY_HERE"
    ```

2.  **Start the FastAPI server:**
    ```bash
    uvicorn backend.main:app --reload
    ```
    The server will be available at `http://localhost:8000`.

3.  **Open the application in your browser:**
    Navigate to `http://localhost:8000` in your web browser.
