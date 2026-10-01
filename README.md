# CloudOps AI Assistant

CloudOps AI Assistant is a Python and FastAPI-based incident analysis API that analyzes service logs, calculates operational metrics, and uses an LLM to generate structured incident explanations.

The current version is a portfolio-ready MVP. It accepts logs through an API, performs deterministic Python-based analysis, sends the resulting incident context to Groq, validates the LLM output using Pydantic, and returns a structured JSON response.

Repository: https://github.com/Rishav478/cloudops-ai-assistant

---

## Overview

CloudOps teams often need to quickly understand what happened during an incident.

This project demonstrates how traditional log-analysis logic and an LLM can work together:

```text
Service Logs
     |
     v
FastAPI
     |
     v
Pydantic Validation
     |
     v
Python Log Analysis
     |
     v
Incident Summary
     |
     v
Groq LLM
     |
     v
Structured JSON Response
     |
     v
Pydantic LLM Validation
     |
     v
API Response
```

The Python layer calculates the incident facts. The LLM is used to explain those facts in simple language rather than replacing deterministic analysis.

---

## Features

- FastAPI-based REST API
- Swagger/OpenAPI interface
- Pydantic request validation
- Service log validation and normalization
- Error counting by service
- Average latency calculation
- Slowest-service identification
- High-latency event detection
- Error-type classification
- Most common error-type detection
- Incident severity calculation
- Structured Groq LLM responses
- Pydantic validation of LLM output
- Guardrails against unsupported root-cause claims
- Graceful degradation when the LLM is unavailable
- Graceful handling of file-saving failures
- HTTP `400`, `422`, and `500` error handling
- Automated API and service tests using Pytest
- Docker support
- Environment-variable based secret management

---

## Tech Stack

| Technology    | Purpose                          |
| ------------- | -------------------------------- |
| Python        | Core application logic           |
| FastAPI       | REST API                         |
| Pydantic      | Input and LLM-output validation  |
| Groq API      | LLM-powered incident explanation |
| Pytest        | Automated testing                |
| HTTPX         | FastAPI test client support      |
| Docker        | Containerization                 |
| python-dotenv | Environment variable loading     |

---

## Project Architecture

```text
                        Client / Swagger
                              |
                              v
                       FastAPI Endpoint
                              |
                              v
                    Pydantic Input Validation
                              |
                              v
                       Incident Service
                              |
              +---------------+---------------+
              |                               |
              v                               v
       Python Log Analysis              Incident Context
              |                               |
              v                               v
       Incident Metrics                  Groq LLM
              |                               |
              |                               v
              |                    Structured JSON Output
              |                               |
              |                               v
              |                    Pydantic LLM Validation
              |                               |
              +---------------+---------------+
                              |
                              v
                    Save Incident Summary
                              |
                              v
                      FastAPI Response
```

The application is designed to degrade gracefully.

If Groq becomes unavailable, the Python-generated incident analysis can still be returned.

If the incident summary cannot be saved to disk, the calculated analysis and LLM response can still be returned.

---

## Project Structure

```text
cloudops-ai-assistant/
|
├── app/
│   ├── services/
│   │   └── incident_service.py
│   │
│   ├── __init__.py
│   ├── api.py
│   ├── incident_summary.py
│   ├── llm_client.py
│   ├── log_analyzer.py
│   └── schemas.py
│
├── data/
│   └── logs.json
│
├── output/
│   └── .gitkeep
│
├── tests/
│   ├── test_api.py
│   └── test_incident_service.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## How the Application Works

### 1. Logs are submitted to the API

The client sends service logs to:

```http
POST /analyze-incident
```

### 2. Pydantic validates the logs

Each log is validated using the `LogEntry` schema.

The validation includes checks such as:

- required service name
- supported log level
- non-negative latency
- valid field types
- normalization of log-level values

For example:

```text
error
```

is normalized to:

```text
ERROR
```

### 3. Python analyzes the logs

The application calculates deterministic incident metrics including:

```text
error_count_by_service
average_latency_by_service
slowest_service
high_latency_by_service
most_common_error_type
severity
```

### 4. Incident context is generated

The deterministic metrics are converted into context for the LLM.

### 5. Groq generates a structured explanation

The LLM is instructed to return JSON containing:

```json
{
  "summary": "...",
  "likely_cause": "...",
  "root_cause_confirmed": false,
  "suggested_checks": ["..."]
}
```

### 6. Pydantic validates the LLM response

The response is checked against `IncidentLLMResponse`.

This verifies that the expected fields and data types are present before the response is returned to the API client.

---

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

---

### Analyze Incident

```http
POST /analyze-incident
```

Example request:

```json
{
  "logs": [
    {
      "timestamp": "2026-09-20T10:00:00",
      "service_name": "payment-service",
      "log_level": "ERROR",
      "message": "Payment request timeout",
      "latency_ms": 2200,
      "request_id": "req-201"
    },
    {
      "timestamp": "2026-09-20T10:01:00",
      "service_name": "order-api",
      "log_level": "INFO",
      "message": "Order created successfully",
      "latency_ms": 300,
      "request_id": "req-202"
    }
  ]
}
```

Example response:

```json
{
  "status": "success",
  "summary_saved": true,
  "summary": {
    "error_count_by_service": {
      "payment-service": 1
    },
    "most_affected_service": "payment-service",
    "highest_error_count": 1,
    "severity": "LOW",
    "average_latency_by_service": {
      "payment-service": 2200.0,
      "order-api": 300.0
    },
    "slowest_service": {
      "service_name": "payment-service",
      "average_latency_ms": 2200.0
    },
    "high_latency_by_service": {
      "payment-service": 1
    },
    "most_common_error_type": {
      "error_type": "timeout",
      "count": 1
    }
  },
  "llm_response": {
    "summary": "Payment-service recorded one timeout error.",
    "likely_cause": "The exact root cause is not confirmed.",
    "root_cause_confirmed": false,
    "suggested_checks": ["Review payment-service logs."]
  }
}
```

---

## Response Statuses

The application uses both HTTP status codes and application-level status values.

### Application Status

`success`

The Python analysis completed, the LLM response was generated and validated, and the incident summary was saved.

`partial_success`

The deterministic Python analysis completed, but one of the optional downstream operations failed.

Examples:

```text
Groq unavailable
File saving failed
Groq and file saving both failed
```

The Python-generated incident analysis is preserved whenever possible.

### HTTP Status Codes

| HTTP Code | Meaning                                |
| --------- | -------------------------------------- |
| `200`     | Request processed successfully         |
| `400`     | No logs were supplied                  |
| `422`     | Request failed Pydantic validation     |
| `500`     | Unexpected internal processing failure |

---

## LLM Guardrails

The prompt used by the application includes rules designed to reduce unsupported claims.

The LLM is instructed to:

- use only the provided incident context
- separate observed evidence from inference
- avoid inventing infrastructure problems
- avoid claiming a root cause unless evidence confirms it
- avoid treating correlation as causation
- preserve the meaning of calculated counts
- treat timeout errors as symptoms unless evidence proves otherwise
- return structured JSON instead of unrestricted text

The LLM explanation complements the deterministic Python analysis rather than replacing it.

---

## Graceful Degradation

A major design goal of this project is preserving useful incident information when optional components fail.

### Groq Failure

```text
Python analysis     -> succeeds
Groq                -> fails
File save           -> succeeds

Result              -> partial_success
Summary             -> preserved
LLM response        -> null
```

### File Save Failure

```text
Python analysis     -> succeeds
Groq                -> succeeds
File save           -> fails

Result              -> partial_success
Summary             -> preserved
LLM response        -> preserved
```

### Groq and File Save Failure

```text
Python analysis     -> succeeds
Groq                -> fails
File save           -> fails

Result              -> partial_success
Summary             -> preserved
LLM response        -> null
```

This prevents the application from discarding deterministic analysis just because an external dependency fails.

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rishav478/cloudops-ai-assistant.git
cd cloudops-ai-assistant
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the Groq API key

Create a `.env` file in the project root.

Use `.env.example` as a reference:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your real Groq API key.

Do not commit `.env` to GitHub.

### 4. Start the FastAPI server

```bash
python -m uvicorn app.api:app --reload
```

### 5. Open Swagger

Open:

```text
http://127.0.0.1:8000/docs
```

You can use Swagger to test:

```text
GET /health
POST /analyze-incident
```

---

## Running Tests

The project contains automated API and service tests.

Run:

```bash
python -m pytest -v
```

The MVP currently includes 10 automated tests covering:

1. Health endpoint
2. Empty-log validation
3. Invalid log-level validation
4. Negative-latency validation
5. Successful API incident analysis
6. Internal service failure handling
7. Groq failure with summary preservation
8. File-saving failure with LLM-response preservation
9. Combined Groq and file-saving failure
10. Incident-analysis calculation correctness

The tests use mocking where appropriate so they do not depend on Groq availability or intentionally damaging local files.

---

## Docker

### Build the image

From the project root:

```bash
docker build -t cloudops-ai-assistant .
```

### Run the container

```bash
docker run --rm -p 8000:8000 --env-file .env cloudops-ai-assistant
```

Then open:

```text
http://127.0.0.1:8000/docs
```

### Health Check

After the container starts, test:

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## Environment Variables

The application currently requires:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The real `.env` file is excluded from Git using `.gitignore`.

The repository contains `.env.example` so users know which environment variables must be configured.

---

## Security Notes

- API keys are loaded from environment variables.
- `.env` is excluded from Git.
- `.env` is also excluded from the Docker build context using `.dockerignore`.
- LLM output is validated before being returned.
- Unexpected internal failures are not exposed directly as detailed API error messages.

---

## Testing Strategy

The project tests two major layers independently.

### API Tests

API tests verify:

```text
HTTP response codes
Pydantic request validation
FastAPI response behavior
Internal failure handling
```

### Service Tests

Service tests verify:

```text
Incident calculations
Groq failure handling
File-save failure handling
Graceful degradation
Preservation of deterministic analysis
```

External dependencies are mocked during tests where appropriate.

---

## Current MVP Scope

The current version analyzes logs supplied directly through the API.

The project intentionally separates deterministic incident calculations from LLM-generated explanations.

Current flow:

```text
API Logs
   |
   v
Python Analysis
   |
   v
Incident Summary
   |
   v
Groq Explanation
   |
   v
Structured API Response
```

Real AWS service integration is planned as the next development phase rather than being represented as part of the current MVP.

---

## Future Improvements

Planned improvements include:

- AWS CloudWatch Logs integration
- AWS CloudWatch Metrics integration
- AWS CloudWatch Alarms integration
- IAM-based AWS authentication
- Automatic AWS service-health analysis
- Runbook retrieval using RAG
- Vector database integration
- Improved incident severity scoring
- Evidence validation for LLM-generated explanations
- More detailed error-type classification
- Request correlation using request IDs
- Production logging using Python's `logging` module
- Application monitoring and observability
- CI/CD pipeline
- Cloud deployment
- Expanded automated test coverage

---

## Example Future Architecture

The next phase of the project is expected to evolve toward:

```text
User / API Request
        |
        v
CloudOps AI Assistant
        |
        +-----------------------------+
        |                             |
        v                             v
CloudWatch Logs                 CloudWatch Metrics
        |                             |
        +--------------+--------------+
                       |
                       v
               Python Analysis
                       |
                       v
                Incident Context
                       |
            +----------+----------+
            |                     |
            v                     v
       Runbook RAG             Groq LLM
            |                     |
            +----------+----------+
                       |
                       v
              Incident Explanation
                       |
                       v
                  FastAPI
```

---

## Key Engineering Concepts Demonstrated

This project demonstrates practical usage of:

- REST API development
- Python data processing
- Pydantic schemas
- custom field validators
- structured LLM outputs
- JSON parsing
- LLM guardrails
- exception handling
- graceful degradation
- mocking external dependencies
- automated API testing
- service-layer testing
- Docker containerization
- environment-variable management
- layered application architecture

---

## Disclaimer

This project is currently a portfolio MVP.

The generated LLM explanation should be treated as an assistance layer for incident investigation. Deterministic metrics from the Python analyzer remain the primary source of calculated incident data.

The current version does not directly connect to AWS CloudWatch. AWS integration is planned as a future phase.

---

## Author

**Rishav Srivastav**

GitHub: [Rishav478](https://github.com/Rishav478)
