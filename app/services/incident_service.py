from app.incident_summary import (
    create_detailed_incident_summary,
    create_incident_prompt,
    create_llm_context,
    save_incident_summary,
)
from app.log_analyzer import (
    calculate_average_latency_by_service,
    count_error_types,
    count_errors_by_service,
    count_high_latency_by_service,
    extract_error_messages,
    find_most_common_error_type,
    find_slowest_service,
)
from pydantic import ValidationError
from app.schemas import IncidentLLMResponse
from pathlib import Path
from app.llm_client import generate_llm_response
from app.schemas import LogEntry


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOGS_PATH = PROJECT_ROOT / "data" / "logs.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "incident_summary.json"


def validate_logs(logs):
    if not isinstance(logs,list) or not logs:
        return (False,"Logs must be provided as a list.",[])

    validated_logs = []


    for log in logs:
        try:
            validated_log = LogEntry.model_validate(log)
            cleaned_log = validated_log.model_dump()
            validated_logs.append(cleaned_log)
        except ValidationError as e:
            return False, str(e), []

    return (True,"Logs are valid", validated_logs)
          
         


def analyze_incident_from_logs(logs):
    
    try:
        is_valid, validation_message, validated_logs = validate_logs(logs)   

        if not is_valid:
            return {
                "status": "failed",
                "summary_saved": False,
                "summary": {},
                "llm_response": validation_message
                }
        logs = validated_logs
        
        error_count_by_service = count_errors_by_service(logs)
        
        average_latency_by_service = calculate_average_latency_by_service(logs)
        
        slowest_service = find_slowest_service(average_latency_by_service)
        
        high_latency_by_service = count_high_latency_by_service(logs)
        
        error_messages = extract_error_messages(logs)
        
        error_types = count_error_types(error_messages)
        
        most_common_error = find_most_common_error_type(error_types)
        
        detailed_summary = create_detailed_incident_summary(
            error_count_by_service,
            average_latency_by_service,
            slowest_service,
            high_latency_by_service,
            most_common_error,
            )
        
        
        
        


        try:
            llm_context = create_llm_context(detailed_summary)
            incident_prompt = create_incident_prompt(llm_context)
            llm_response = generate_llm_response(incident_prompt)
            validated_llm_response = IncidentLLMResponse.model_validate(llm_response)
            llm_response = validated_llm_response.model_dump()
        except Exception as e:
            print(f"LLM processing failed: {e}")
            llm_response = None  



        try:
            is_saved = save_incident_summary(detailed_summary,OUTPUT_PATH)
        except Exception as e:
            is_saved = False
            print(f"Failed to save incident summary: {e}")

        
        return {
            "status": "success" if is_saved and llm_response is not None else "partial_success",
            "summary_saved": is_saved,
            "summary": detailed_summary,
            "llm_response": llm_response
            }
    except Exception as e:
            return {
                "status": "failed",
                "summary_saved": False,
                "summary": {},
                "llm_response": f"Incident analysis failed: {str(e)}"
            }

