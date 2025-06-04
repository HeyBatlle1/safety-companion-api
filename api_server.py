from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

# Import the core logic
from medical_core import perform_trauma_assessment

app = FastAPI(
    title="Medical MCP API Server",
    description="Provides REST API access to medical MCP functionalities.",
    version="0.1.0"
)

# CORS configuration
# Adjust origins as needed for your Bolt.new frontend (local dev and deployed)
origins = [
    "http://localhost", # Common for local dev
    "http://localhost:3000", # Common React dev port
    "http://localhost:8080", # Another common dev port
    # Add your Bolt.new development and production URLs here
    # e.g., "https://your-bolt-app-dev.netlify.app",
    #       "https://your-bolt-app-prod.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models for API Request/Response ---

class TraumaAssessmentRequest(BaseModel):
    mechanismOfInjury: str = Field(..., example="Fall from 10ft ladder")
    reportedSymptoms: List[str] = Field(..., example=["severe leg pain", "dizziness"])
    conscious: bool = Field(..., example=True)
    age: Optional[int] = Field(None, example=35)
    gender: Optional[Literal["male", "female", "other", "unknown"]] = Field(None, example="female")
    obviousBleeding: Optional[bool] = Field(None, example=False)

class TraumaAssessmentResponse(BaseModel):
    severity_level: Literal["critical", "serious", "moderate", "minor", "unknown"]
    immediate_actions: List[str]
    assessment_steps: List[str]
    red_flags: List[str]
    next_steps: List[str]

class StatusResponse(BaseModel):
    status: str
    version: str
    active_protocols: List[str]

# --- API Endpoints ---

@app.get("/api/status", response_model=StatusResponse, tags=["General"])
async def get_status():
    """
    Provides the operational status of the API server.
    """
    return {
        "status": "Medical MCP API Server is running",
        "version": app.version,
        "active_protocols": ["trauma_assessment"] # Add more as they are implemented
    }

@app.post("/api/medical/trauma-assessment", response_model=TraumaAssessmentResponse, tags=["Medical Protocols"])
async def handle_trauma_assessment(request_data: TraumaAssessmentRequest):
    """
    Processes a trauma assessment request using the medical core logic.
    """
    try:
        # Convert Pydantic model to dict for the core logic function
        patient_data_dict = request_data.model_dump()
        
        # Call the core logic function
        result = perform_trauma_assessment(patient_data_dict)
        
        # Ensure the result from core logic matches the expected response structure
        # (Pydantic will validate this on return if response_model is used correctly)
        if "Error:" in result.get("immediate_actions", [""])[0]: # Basic check for error from core
             raise HTTPException(status_code=400, detail=result.get("immediate_actions")[0])

        return result
    except HTTPException as http_exc:
        raise http_exc # Re-raise FastAPI's HTTP exceptions
    except Exception as e:
        # Catch any other unexpected errors from the core logic or processing
        print(f"Error during trauma assessment: {e}") # Log the error server-side
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# To run this server (from the directory containing api_server.py):
# uvicorn api_server:app --reload --port 8002 
# (or any other port, e.g., 8000 if not conflicting)
