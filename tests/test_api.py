from fastapi.testclient import TestClient
from app.api import app
from unittest.mock import patch

client = TestClient(app)


def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_empty_logs_returns_400():

    response = client.post(
        "/analyze-incident",
        json={
            "logs": []
        }
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "No logs available for analysis."
    }

def test_invalid_log_level_returns_422():

    response = client.post(
        "/analyze-incident",
        json={
            "logs": [
                {
                    "service_name": "payment-service",
                    "log_level": "FATAL",
                    "message": "Payment failed",
                    "latency_ms": 2200
                }
            ]
        }
    )

    assert response.status_code == 422

    response_body = response.json()

    assert response_body["detail"][0]["loc"] == [
        "body",
        "logs",
        0,
        "log_level"
    ]

    assert "Log level must be INFO, WARN, or ERROR" in response_body["detail"][0]["msg"]





def test_negative_latency():

    response = client.post(
        "/analyze-incident",
        json={
            "logs": [
                {
                    "service_name": "payment-service",
                    "log_level": "ERROR",
                    "message": "Payment failed",
                    "latency_ms": -2200
                }
            ]
        }
    )

    assert response.status_code == 422

    response_body = response.json()

    assert response_body["detail"][0]["loc"] == [
        "body",
        "logs",
        0,
        "latency_ms"
    ]

    assert "Latency cannot be negative" in response_body["detail"][0]["msg"]



def test_successful_incident_analysis():

    fake_result = {
        "status": "success",
        "summary_saved": True,
        "summary": {
            "error_count_by_service": {
                "payment-service": 1
            },
            "most_affected_service": "payment-service",
            "highest_error_count": 1,
            "severity": "LOW",
            "average_latency_by_service": {
                "payment-service": 2200.0
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
            "root_cause_confirmed": False,
            "suggested_checks": [
                "Review payment-service logs."
            ]
        }
    }

    with patch(
        "app.api.analyze_incident_from_logs",
        return_value=fake_result
    ):

        response = client.post(
            "/analyze-incident",
            json={
                "logs": [
                    {
                        "service_name": "payment-service",
                        "log_level": "ERROR",
                        "message": "Payment timeout",
                        "latency_ms": 2200
                    }
                ]
            }
        )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["summary_saved"] is True
    assert response.json()["summary"]["most_affected_service"] == "payment-service"
    assert response.json()["llm_response"]["root_cause_confirmed"] is False


def test_internal_service_failure_returns_500():

    fake_result = {
        "status": "failed",
        "summary_saved": False,
        "summary": {},
        "llm_response": "Unexpected analyzer failure"
    }

    with patch(
        "app.api.analyze_incident_from_logs",
        return_value=fake_result
    ):

        response = client.post(
            "/analyze-incident",
            json={
                "logs": [
                    {
                        "service_name": "payment-service",
                        "log_level": "ERROR",
                        "message": "Payment timeout",
                        "latency_ms": 2200
                    }
                ]
            }
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Internal server error"
    }
    