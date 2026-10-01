from unittest.mock import patch

from app.services.incident_service import analyze_incident_from_logs


def test_groq_failure_preserves_summary():

    logs = [
        {
            "service_name": "payment-service",
            "log_level": "ERROR",
            "message": "Payment request timeout",
            "latency_ms": 2200
        }
    ]

    with patch(
        "app.services.incident_service.generate_llm_response",
        side_effect=ConnectionError("Test: Groq unavailable")
    ), patch(
        "app.services.incident_service.save_incident_summary",
        return_value=True
    ):

        result = analyze_incident_from_logs(logs)

    assert result["status"] == "partial_success"

    assert result["summary_saved"] is True

    assert result["summary"]

    assert result["summary"]["most_affected_service"] == "payment-service"

    assert result["llm_response"] is None



def test_save_failure_preserves_llm_response():

    logs = [
        {
            "service_name": "payment-service",
            "log_level": "ERROR",
            "message": "Payment request timeout",
            "latency_ms": 2200
        }
    ]

    fake_llm_response = {
        "summary": "Payment-service recorded one timeout error.",
        "likely_cause": "The exact root cause is not confirmed.",
        "root_cause_confirmed": False,
        "suggested_checks": [
            "Review payment-service logs."
        ]
    }

    with patch(
        "app.services.incident_service.generate_llm_response",
        return_value=fake_llm_response
    ), patch(
        "app.services.incident_service.save_incident_summary",
        return_value=False
    ):

        result = analyze_incident_from_logs(logs)

    assert result["status"] == "partial_success"

    assert result["summary_saved"] is False

    assert result["summary"]

    assert result["summary"]["most_affected_service"] == "payment-service"

    assert result["llm_response"]["root_cause_confirmed"] is False



def test_groq_and_save_failure_preserve_summary():

    logs = [
        {
            "service_name": "payment-service",
            "log_level": "ERROR",
            "message": "Payment request timeout",
            "latency_ms": 2200
        }
    ]

    with patch(
        "app.services.incident_service.generate_llm_response",
        side_effect=ConnectionError("Test: Groq unavailable")
    ), patch(
        "app.services.incident_service.save_incident_summary",
        side_effect=PermissionError("Test: cannot save file")
    ):

        result = analyze_incident_from_logs(logs)

    assert result["status"] == "partial_success"

    assert result["summary_saved"] is False

    assert result["summary"]

    assert result["summary"]["most_affected_service"] == "payment-service"

    assert result["llm_response"] is None


def test_incident_analysis_calculations_are_correct():

    logs = [
        {
            "service_name": "payment-service",
            "log_level": "ERROR",
            "message": "Database timeout",
            "latency_ms": 2200
        },
        {
            "service_name": "payment-service",
            "log_level": "ERROR",
            "message": "Payment timeout",
            "latency_ms": 1800
        },
        {
            "service_name": "payment-service",
            "log_level": "WARN",
            "message": "High latency detected",
            "latency_ms": 1200
        },
        {
            "service_name": "checkout-service",
            "log_level": "ERROR",
            "message": "Lambda timeout",
            "latency_ms": 1500
        },
        {
            "service_name": "order-api",
            "log_level": "INFO",
            "message": "Order created successfully",
            "latency_ms": 300
        }
    ]

    fake_llm_response = {
        "summary": "Test summary",
        "likely_cause": "Root cause not confirmed",
        "root_cause_confirmed": False,
        "suggested_checks": [
            "Review logs"
        ]
    }

    with patch(
        "app.services.incident_service.generate_llm_response",
        return_value=fake_llm_response
    ), patch(
        "app.services.incident_service.save_incident_summary",
        return_value=True
    ):

        result = analyze_incident_from_logs(logs)

    summary = result["summary"]

    assert summary["error_count_by_service"] == {
        "payment-service": 2,
        "checkout-service": 1
    }

    assert summary["most_affected_service"] == "payment-service"

    assert summary["highest_error_count"] == 2

    assert summary["severity"] == "MEDIUM"

    assert summary["average_latency_by_service"]["payment-service"] == 1733.33

    assert summary["slowest_service"]["service_name"] == "payment-service"

    assert summary["high_latency_by_service"]["payment-service"] == 3

    assert summary["most_common_error_type"]["error_type"] == "timeout"

    assert summary["most_common_error_type"]["count"] == 3