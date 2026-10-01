import json



def create_incident_summary(error_count_by_service):
    
    most_affected_service_name = None
    highest_error_count = 0

    for service_name,count in error_count_by_service.items():
        if count > highest_error_count:
            most_affected_service_name = service_name
            highest_error_count = count

    if (highest_error_count >= 3):
        severity = "HIGH"
    elif (highest_error_count == 2):
        severity = "MEDIUM"
    elif (highest_error_count ==1):
        severity = "LOW" 
    else:
        severity = "HEALTHY"     

    incident_summary = {
    "error_count_by_service": error_count_by_service,
    "most_affected_service": most_affected_service_name,
    "highest_error_count": highest_error_count,
    "severity": severity
    }
    return incident_summary 


def save_incident_summary(incident_summary,filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(incident_summary, file, indent=4)
        return True
    except Exception as e:
        print(f"Error: failed to save incident summary. Reason: {e}")
        return False

def create_detailed_incident_summary(
    error_count_by_service,
    average_latency_by_service,
    slowest_service,
    high_latency_by_service,
    most_common_error_type
):
    most_affected_service_name = None
    highest_error_count = 0
    
    for service_name,count in error_count_by_service.items():
        if count > highest_error_count:
                most_affected_service_name = service_name
                highest_error_count = count
    
    if (highest_error_count >= 3):
        severity = "HIGH"
    elif (highest_error_count == 2):
        severity = "MEDIUM"
    elif (highest_error_count ==1):
        severity = "LOW" 
    else:
        severity = "HEALTHY"     
    
    detailed_incident_summary = {
        "error_count_by_service": error_count_by_service,
        "most_affected_service": most_affected_service_name,
        "highest_error_count": highest_error_count,
        "severity": severity,
        "average_latency_by_service": average_latency_by_service,
        "slowest_service": slowest_service,
        "high_latency_by_service": high_latency_by_service,
        "most_common_error_type": most_common_error_type
        }
    return detailed_incident_summary

def format_incident_summary(detailed_incident_summary):
    slowest_service = detailed_incident_summary.get("slowest_service",{})
    most_common_error_type = detailed_incident_summary.get("most_common_error_type",{})
    slowest_service_value = slowest_service.get('average_latency_ms')

    formatted_incident_summary = (f"""
Incident Summary:
Most affected service is {detailed_incident_summary['most_affected_service']}.
Highest error count is {detailed_incident_summary['highest_error_count']}.
Severity is {detailed_incident_summary['severity']}.
Slowest service is {slowest_service.get('service_name',None)} with average latency {round(slowest_service_value,3)} ms.
Most common error type is {most_common_error_type.get('error_type',None)}, seen {most_common_error_type.get('count',0)} times.
High latency count by service: {detailed_incident_summary['high_latency_by_service']}
""")
    return formatted_incident_summary


def create_llm_context(detailed_incident_summary):
    slowest_service = detailed_incident_summary.get("slowest_service",{})
    slowest_service_value = slowest_service.get('average_latency_ms',0)
    most_common_error_type = detailed_incident_summary.get("most_common_error_type",{})

    llm_context = (f"""
CloudOps Incident Context:
Severity: {detailed_incident_summary['severity']}
Most affected service: {detailed_incident_summary['most_affected_service']}
Highest error count: {detailed_incident_summary['highest_error_count']}
Slowest service: {slowest_service.get('service_name',None)}
Average latency: {round(slowest_service_value,2)} ms
Most common error type: {most_common_error_type.get('error_type',None)}
High latency count by service: {detailed_incident_summary['high_latency_by_service']}
""") 
    return llm_context

def create_incident_prompt(llm_context):

    incident_prompt = f"""
You are a CloudOps AI Assistant.

Explain the incident in simple English.

Rules:
- Use only the provided incident context.
- Do not invent services, metrics, logs, deployments, infrastructure problems, or root causes.
- Clearly separate observed evidence from inference.
- If the exact root cause is not confirmed, say that it is not confirmed.
- A likely cause must be directly supported by the provided evidence.
- Suggested next checks may recommend investigation steps, but do not state those checks as known causes.
- Do not claim CPU, memory, database, deployment, network, or dependency problems unless the context explicitly contains evidence for them.
- Do not infer causation from correlation. If two signals occur together, describe them as associated unless the context proves that one caused the other.
- When reporting counts, preserve their exact meaning. For example, count=2 for an error type means that error type occurred 2 times.
- Do not assume that two metrics with the same count refer to the same log events unless the context explicitly links those events.
- Treat errors such as timeouts as observed symptoms unless the provided evidence proves they are the underlying cause.
- Do not state that an error caused latency or that latency caused an error unless the context explicitly establishes that relationship.
- When the evidence only shows multiple signals occurring in the same service, describe them as associated signals.
- Never state that one observed signal contributes to, causes, or leads to another observed signal unless the provided context explicitly proves that relationship. When causality is unknown, describe the signals as associated.
- When describing a hypothesis, do not use causal phrases such as "leads to", "causes", "results in", or "contributes to" unless the context explicitly proves causation. Use "associated with", "co-occurs with", or "may be related to" instead.


Incident context:
{llm_context}

Return your answer as a valid JSON object.

Use exactly these fields:

{{
    "summary": "Explain what happened.",
    "likely_cause": "Explain what the evidence suggests and state whether the root cause is confirmed.",
    "root_cause_confirmed": false,
    "suggested_checks": [
        "First investigation step",
        "Second investigation step",
        "Third investigation step"
    ]
}}

Return only the JSON object.
Do not include Markdown headings or code fences.
"""
    return incident_prompt



