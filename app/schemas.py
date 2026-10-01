from pydantic import BaseModel,field_validator
from typing import Optional

class LogEntry(BaseModel):
    timestamp: Optional[str] = None
    service_name: str
    log_level: str
    message: Optional[str] = None
    latency_ms: float
    request_id: Optional[str] = None
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized_value = value.upper()

        if normalized_value not in {"INFO", "WARN", "ERROR"}:
            raise ValueError("Log level must be INFO, WARN, or ERROR")

        return normalized_value
    
    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, value: str)-> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Service name cannot be empty")

        return cleaned_value

    @field_validator("latency_ms")
    @classmethod
    def validate_latency_ms(cls, value: float)-> float:
        final_value = value

        if final_value < 0:
            raise ValueError("Latency cannot be negative")

        return final_value


class IncidentLLMResponse(BaseModel):
    summary: str
    likely_cause: str
    root_cause_confirmed: bool
    suggested_checks: list[str]