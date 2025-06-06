from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

# Import the core logic
from medical_core import perform_trauma_assessment

# Imports for database operations
from sqlalchemy.orm import Session
import json
# Assuming database.py defines SessionLocal and the InjuryRecord SQLAlchemy model
# e.g., from .database import SessionLocal, InjuryRecord
# For now, using placeholder if direct import fails, adjust path as needed for your project structure
try:
    from database import SessionLocal, InjuryRecord
except ImportError:
    print("Warning: 'database.py' not found or 'SessionLocal'/'InjuryRecord' not defined. Database endpoints will fail.")
    # Define placeholders if not found, to allow server to start for non-DB endpoints
    class InjuryRecord: pass 
    class SessionLocal: pass

app = FastAPI(
    title="Medical MCP API Server",
    description="Provides REST API access to medical MCP functionalities.",
    version="0.1.0"
)

# CORS configuration
# Adjust origins as needed for your Bolt.new frontend (local dev and deployed)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Add this line for your Vite frontend
    "http://localhost:8080",
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

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/api/injuries", tags=["Database"])
async def save_injury_record(request_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Save injury record to database"""
    try:
        # Convert complex fields to JSON strings if DB model expects strings
        reported_symptoms_json = json.dumps(request_data.get("reportedSymptoms", []))
        assessment_result_json = json.dumps(request_data.get("assessmentResult", {}))

        # Create SQLAlchemy model instance
        # Ensure field names here match your InjuryRecord SQLAlchemy model columns
        injury_record_db = InjuryRecord(
            user_id=request_data.get("userId"),
            mechanism_of_injury=request_data.get("mechanismOfInjury"),
            reported_symptoms=reported_symptoms_json,
            severity_level=request_data.get("severityLevel"),
            conscious=request_data.get("conscious"),
            age=request_data.get("age"),
            gender=request_data.get("gender"),
            obvious_bleeding=request_data.get("obviousBleeding"),
            assessment_result=assessment_result_json
            # created_at is usually handled by the DB (e.g., default=func.now())
        )
        
        db.add(injury_record_db)
        db.commit()
        db.refresh(injury_record_db)
        
        # Return the created record, matching frontend's InjuryRecord structure
        return {
            "id": injury_record_db.id, # Assuming id is auto-generated
            "userId": injury_record_db.user_id,
            "mechanismOfInjury": injury_record_db.mechanism_of_injury,
            "reportedSymptoms": json.loads(injury_record_db.reported_symptoms) if injury_record_db.reported_symptoms else [],
            "severityLevel": injury_record_db.severity_level,
            "conscious": injury_record_db.conscious,
            "age": injury_record_db.age,
            "gender": injury_record_db.gender,
            "obviousBleeding": injury_record_db.obvious_bleeding,
            "assessmentResult": json.loads(injury_record_db.assessment_result) if injury_record_db.assessment_result else {},
            "createdAt": injury_record_db.created_at.isoformat() if hasattr(injury_record_db, 'created_at') and injury_record_db.created_at else None
        }
    except Exception as e:
        db.rollback()
        print(f"Error in save_injury_record: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save injury record: {str(e)}")

@app.get("/api/injuries/{user_id}", tags=["Database"])  
async def get_injury_history(user_id: str, db: Session = Depends(get_db)):
    """Get injury history for a user"""
    try:
        # Assuming InjuryRecord is your SQLAlchemy model
        # and it has a 'created_at' field for ordering
        db_records = db.query(InjuryRecord).filter(InjuryRecord.user_id == user_id).order_by(InjuryRecord.created_at.desc() if hasattr(InjuryRecord, 'created_at') else InjuryRecord.id.desc()).all()
        
        response_records = []
        for r in db_records:
            response_records.append({
                "id": r.id,
                "userId": r.user_id,
                "mechanismOfInjury": r.mechanism_of_injury,
                "reportedSymptoms": json.loads(r.reported_symptoms) if r.reported_symptoms else [],
                "severityLevel": r.severity_level,
                "conscious": r.conscious,
                "age": r.age,
                "gender": r.gender,
                "obviousBleeding": r.obvious_bleeding,
                "assessmentResult": json.loads(r.assessment_result) if r.assessment_result else {},
                "createdAt": r.created_at.isoformat() if hasattr(r, 'created_at') and r.created_at else None
            })
        return response_records
    except Exception as e:
        print(f"Error in get_injury_history for user {user_id}: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get injury history: {str(e)}")

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
