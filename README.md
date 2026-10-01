# CloudOps AI Assistant

CloudOps AI Assistant is a Python and FastAPI-based incident analysis API that analyzes service logs, calculates operational metrics, and uses an LLM to generate a structured incident explanation.

## Features

- Analyze service logs submitted through a FastAPI endpoint
- Count errors by service
- Calculate average latency by service
- Identify the slowest service
- Detect high-latency events
- Identify common error types
- Generate incident severity
- Generate structured LLM incident explanations using Groq
- Validate API input and LLM output using Pydantic
- Gracefully handle LLM failures and file-saving failures
- Automated API and service tests using pytest

## Tech Stack

- Python
- FastAPI
- Pydantic
- Groq API
- Pytest
- HTTPX

## Project Architecture

The application follows a simple layered flow:

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
      +----------------------+
      |                      |
      v                      v
Python Log Analysis      Groq LLM
      |                      |
      v                      v
Incident Metrics      Structured JSON Response
      |                      |
      +----------+-----------+
                 |
                 v
        Pydantic LLM Validation
                 |
                 v
        Save Incident Summary
                 |
                 v
          FastAPI Response
```

## Project Structure

```text
CloudOps/
├── app/
│   ├── services/
│   │   └── incident_service.py
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
│   └── incident_summary.json
│
├── tests/
│   ├── test_api.py
│   └── test_incident_service.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

```

## How the API Works

The FastAPI application exposes endpoints for checking service health and analyzing incident logs.

### GET /health

Checks whether the API is running.

Example response:

```json
{
  "status": "healthy"
}
```

### POST /analyze-incident

Accepts service logs and analyzes them.

Example request:

{
"logs": [
{
"service_name": "payment-service",
"log_level": "ERROR",
"message": "Payment request timeout",
"latency_ms": 2200
}
]
}

The API:

- validates the logs using Pydantic
- calculates error counts and latency metrics
- creates an incident summary
- sends the incident context to Groq
- validates the structured LLM response
- saves the incident summary
- returns the analysis as JSON
  Possible results:
- success — analysis, LLM response, and file saving succeed
- partial_success — Python analysis succeeds but Groq or file saving fails
- 400 — no logs were provided
- 422 — invalid log data
- 500 — unexpected internal failure

## Setup and Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd CloudOps

```

### 2. Install dependencies

python -m pip install -r requirements.txt

### 3. Configure the Groq API key

Create a .env file in the project root.
You can use .env.example as a reference:
GROQ_API_KEY=your_groq_api_key_here

Replace the placeholder with your actual Groq API key.

### 4. Start the FastAPI application

python -m uvicorn app.api:app --reload

### 5. Open Swagger

After the server starts, open:
http://127.0.0.1:8000/docs

Swagger can be used to test the /health and /analyze-incident endpoints.

### 6. Run automated tests

python -m pytest -v

## Testing and Reliability

The project includes automated tests for both the API layer and the incident service.

Current test coverage includes:

- health endpoint
- empty log validation
- invalid log level validation
- negative latency validation
- successful incident analysis
- internal API failure handling
- Groq failure handling
- file-saving failure handling
- combined Groq and file-saving failure
- incident analysis calculation correctness

Run the test suite with:

```bash
python -m pytest -v
```

## Docker

Build the Docker image:

docker build -t cloudops-ai-assistant .

Run the container:

docker run --rm -p 8000:8000 --env-file .env cloudops-ai-assistant

## Future Improvements

Planned improvements include:

- AWS CloudWatch Logs integration
- CloudWatch Metrics and Alarms integration
- IAM-based AWS authentication
- Runbook retrieval using RAG
- Improved incident severity scoring
- Evidence validation for LLM-generated explanations
- Production logging and monitoring
- Cloud deployment
