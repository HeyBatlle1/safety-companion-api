# Python Medical MCP Server

This project provides a Python-based server with a dual interface:
1.  A direct Model Context Protocol (MCP) interface (handled by your existing script, e.g., `your_original_mcp_script.py`).
2.  An HTTP REST API interface (via FastAPI in `api_server.py`) for web clients like Bolt.new.

Both interfaces utilize a shared core medical logic module (`medical_core.py`).

## Features

-   **Shared Medical Logic**: Core medical assessment functions are centralized in `medical_core.py`.
-   **FastAPI HTTP Server**: Exposes medical logic via RESTful endpoints.
    -   `POST /api/medical/trauma-assessment`: For performing trauma assessments.
    -   `GET /api/status`: To check the server's operational status.
-   **CORS Enabled**: Configured for frontend applications.
-   **Pydantic Validation**: Automatic request and response validation for API endpoints.
-   **PM2 Ready**: Instructions provided for running both the direct MCP script and the API server using PM2.

## Project Structure

```
python_mcp_server/
├── your_original_mcp_script.py  (Your existing script for direct MCP communication)
├── medical_core.py        (Shared core medical logic)
├── api_server.py          (FastAPI HTTP server)
├── requirements.txt       (Python dependencies)
├── .gitignore             (Standard Python .gitignore)
└── README.md              (This file)
```

## Setup and Installation

1.  **Clone the repository (if you haven't already for your existing script):**
    If this code is part of a larger repository that you've cloned, navigate to the `python_mcp_server` directory.

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment. If you don't have one for this project yet:
    ```bash
    cd python_mcp_server
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Servers

You will typically run two Python processes:
-   Your original script for direct MCP communication.
-   The new `api_server.py` for HTTP REST API access.

It's recommended to use a process manager like PM2.

### Using PM2

Ensure PM2 is installed (`npm install -g pm2`).

1.  **Start your existing Python MCP script (for direct MCP protocol):**
    (Replace `your_original_mcp_script.py` with the actual name of your script. Ensure it's updated to import logic from `medical_core.py`.)
    ```bash
    # Navigate to python_mcp_server directory first if not already there
    # Ensure your virtual environment is NOT active when running PM2 with --interpreter,
    # or provide the full path to the python interpreter from the venv.
    # Best practice: Deactivate venv, then let PM2 use the venv's interpreter path.
    # Example: pm2 start your_original_mcp_script.py --name "python-mcp-direct" --interpreter /path/to/your/venv/bin/python
    
    # Simpler if running from an already activated venv (but PM2 might behave differently):
    pm2 start your_original_mcp_script.py --name "python-mcp-direct" --interpreter python3
    ```

2.  **Start the FastAPI HTTP API server (e.g., on port 8002):**
    ```bash
    # Ensure you are in the python_mcp_server directory
    pm2 start "uvicorn api_server:app --host 0.0.0.0 --port 8002" --name "python-mcp-http-api"
    ```
    *Note: Adjust the port `8002` if needed.*

3.  **Check Status:**
    ```bash
    pm2 list
    ```

4.  **Save PM2 Process List (for auto-restart on boot):**
    ```bash
    pm2 save
    ```
    (You might need to run `pm2 startup` first to configure PM2 startup scripts for your OS.)

### Manual Startup (for development/testing without PM2)

1.  **Terminal 1 (Direct MCP Script):**
    ```bash
    cd python_mcp_server
    source venv/bin/activate
    python your_original_mcp_script.py
    ```

2.  **Terminal 2 (FastAPI HTTP Server):**
    ```bash
    cd python_mcp_server
    source venv/bin/activate
    uvicorn api_server:app --reload --host 0.0.0.0 --port 8002
    ```

## API Endpoints

-   **`GET /api/status`**
    -   Description: Returns the status of the HTTP API server.
    -   Response: `{"status": "Medical MCP API Server is running", "version": "0.1.0", "active_protocols": ["trauma_assessment"]}`

-   **`POST /api/medical/trauma-assessment`**
    -   Description: Performs a trauma assessment.
    -   Request Body (JSON):
        ```json
        {
          "mechanismOfInjury": "Fall from 10ft ladder",
          "reportedSymptoms": ["severe leg pain", "dizziness"],
          "conscious": true,
          "age": 35, // optional
          "gender": "female", // optional
          "obviousBleeding": false // optional
        }
        ```
    -   Response Body (JSON):
        ```json
        {
          "severity_level": "serious",
          "immediate_actions": ["Ensure scene safety.", "Call for emergency medical services..."],
          "assessment_steps": ["Check for responsiveness...", "..."],
          "red_flags": ["High-risk mechanism of injury..."],
          "next_steps": ["Reassess ABCDEs frequently...", "..."]
        }
        ```

## Development

-   The core medical logic resides in `medical_core.py`.
-   The FastAPI application and its endpoints are defined in `api_server.py`.
-   Remember to update the `origins` list in `api_server.py` for CORS if your frontend URLs change.
