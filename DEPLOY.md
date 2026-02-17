# Deployment Guide for MyPocketLawyer

This guide explains how to deploy the MyPocketLawyer application using Docker.

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine or server.
- A **Google Gemini API Key**.

## Deployment Steps

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <repository-url>
    cd MyPocketLawyer-Clean
    ```

2.  **Environment Setup**:
    Create a `.env` file in the root directory if it doesn't exist:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

3.  **Build and Run**:
    Run the following command to build the Docker image and start the container:
    ```bash
    docker-compose up --build
    ```
    *Note: This process may take a few minutes as it builds the frontend and installs backend dependencies.*

4.  **Ingest Data (If needed)**:
    If your vector database is empty or you want to refresh it with data from `processeddata/`, run:
    ```bash
    docker-compose run --rm app python backend/ingest.py
    ```

5.  **Access the Application**:
    Open your browser and navigate to:
    ```
    http://localhost:8000
    ```

## Troubleshooting

- **"docker: command not found"**: Ensure Docker Desktop (Windows/Mac) or Docker Engine (Linux) is installed and running.
- **Port Conflicts**: If port 8000 is in use, modify `docker-compose.yml` to map a different host port (e.g., `"8080:8000"`).
- **Frontend not loading**: Ensure the build process in the Dockerfile finished successfully. Check logs with `docker-compose logs`.

## Project Structure for Deployment

- **Frontend**: A React/Vite app located in `frontend/`. It is built into static files (`frontend/dist`) during the Docker build.
- **Backend**: A FastAPI app located in `backend/`. It serves the API at `/chat` and the frontend static files at `/`.
- **Database**: Uses ChromaDB for vector storage, persisted in `chroma_db/`.

