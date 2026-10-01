import os
from dotenv import load_dotenv
from groq import Groq
import json



load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=api_key
)

if api_key:
    print("Groq API key loaded successfully.")
else:
    print("Groq API key not found.") 


def generate_llm_response(incident_prompt):
    response = client.chat.completions.create(
        model= "openai/gpt-oss-20b",
        messages=[
            {
                "role":"user",
                "content": incident_prompt
            }
        ],
        response_format={
            "type": "json_object"
        }   
    )
    llm_response = response.choices[0].message.content
    parsed_response = json.loads(llm_response)
    print("Groq response type:", type(llm_response))
    print("Parsed response type:", type(parsed_response))

    return parsed_response





def generate_mock_llm_response(detailed_incident_summary):
    mock_llm_response = f"""1. Summary
The {detailed_incident_summary.get("most_affected_service","")} is the most affected service with {detailed_incident_summary.get("severity","")} severity. It has {detailed_incident_summary.get("highest_error_count",0)} error logs and an average latency of {detailed_incident_summary.get("slowest_service").get("average_latency_ms",0)} ms.

2. Likely cause
The likely cause is timeout-related issues in the payment-service.

3. Suggested next checks
- Check payment-service logs around the affected timestamp.
- Check RDS/database connectivity.
- Check whether recent deployment caused increased latency.
"""
    return mock_llm_response