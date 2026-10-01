from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.incident_service import analyze_incident_from_logs
from app.schemas import IncidentLLMResponse, LogEntry




class IncidentAnalysisRequest(BaseModel):
    logs: List[LogEntry]




class IncidentAnalysisResponse(BaseModel):
    status: str
    summary_saved: bool
    summary: dict
    llm_response: IncidentLLMResponse | str | None



app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "CloudOps AI Assistant API is running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/analyze-incident",response_model = IncidentAnalysisResponse)
def analyze_incident(request: IncidentAnalysisRequest):

        if not request.logs:
            raise HTTPException(
                status_code=400,
                detail= "No logs available for analysis."
            )
        logs = [log.model_dump() for log in request.logs]
        result = analyze_incident_from_logs(logs)

        if result["status"]== "failed":
             raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )


        return result 




        