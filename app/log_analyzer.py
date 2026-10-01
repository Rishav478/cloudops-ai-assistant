
def count_errors_by_service(logs):
    error_count_by_service = {}
    for log in logs:
        if log.get("log_level","").upper() == "ERROR":
            service_name = log.get("service_name", "unknown-service")
            if service_name in error_count_by_service:
                error_count_by_service[service_name] += 1
            else:
                error_count_by_service[service_name] = 1
    return error_count_by_service


def find_high_latency_logs(logs, threshold_ms=1000):
    high_latency_logs =  []

    for log in logs:
        latency = log.get("latency_ms", 0)
        if latency > threshold_ms:
            high_latency_logs.append(log)
    return high_latency_logs

def calculate_average_latency_by_service(logs):
    latency_sum_by_service = {}
    latency_count_by_service = {}

    for log in logs:
        service_name = log.get("service_name","Unknown Service")
        latency = log.get("latency_ms",0)
        if service_name in latency_count_by_service:
            latency_sum_by_service[service_name] += latency
            latency_count_by_service[service_name] += 1
        else:
            latency_sum_by_service[service_name] = latency
            latency_count_by_service[service_name] = 1

    average_latency_by_service = {}

    for service_name, latency in latency_sum_by_service.items():
        count = latency_count_by_service[service_name]
        average = round(latency/count,2)
        average_latency_by_service[service_name] = average

    return average_latency_by_service


def find_slowest_service(average_latency_by_service):
    slowest_latency = 0
    slowest_service_name = None
    slowest_service = {}

    if not average_latency_by_service:
        slowest_service["service_name"] = None
        slowest_service["average_latency_ms"] = 0
        return slowest_service
    else:
        for service_name,latency in average_latency_by_service.items():
            if slowest_latency < latency:
                slowest_latency = latency
                slowest_service_name = service_name
        slowest_service["service_name"] = slowest_service_name
        slowest_service["average_latency_ms"] = slowest_latency
        return slowest_service

def count_high_latency_by_service(logs, threshold_ms=1000):
    high_latency_by_service = {}

    for log in logs:
        service_name = log.get("service_name","unknown-service")
        latency = log.get("latency_ms",0)
        if latency > threshold_ms:
            if service_name in high_latency_by_service:
                high_latency_by_service[service_name] +=1
            else:
                high_latency_by_service[service_name] = 1

    return high_latency_by_service    

def find_logs_by_request_id(logs, request_id):
    matching_logs = []

    for log in logs:
        log_req_id = log.get("request_id","unknown_id")
        if request_id == log_req_id:
            matching_logs.append(log)

    return matching_logs

def extract_error_messages(logs):
    error_messages = []

    for log in logs:
        if log.get("log_level","").upper() == "ERROR":
            message = log.get("message") or "No error message available"
            error_messages.append(message)
    return error_messages

def count_error_types(error_messages):
    error_type_count = {}

    for err in error_messages:
        message = err.lower()
        matched = False
        if "timeout" in message:
            matched = True
            if "timeout" in error_type_count:
                error_type_count["timeout"] += 1
            else:
                error_type_count["timeout"] = 1
        if "connection" in message:
            matched = True
            if "connection_issue" in error_type_count:
                error_type_count["connection_issue"] += 1
            else:
                error_type_count["connection_issue"] = 1
        if "throttl" in message:
            matched = True
            if "throttling" in error_type_count:
                error_type_count["throttling"] += 1
            else:
                error_type_count["throttling"] = 1
        if not matched:
            if "unknown_error" in error_type_count:
                error_type_count["unknown_error"] += 1
            else:
                error_type_count["unknown_error"] = 1
    return error_type_count

def find_most_common_error_type(error_type_count):
    most_common_error_type = {}
    most_common_err = None
    total_err_count = 0
    if not error_type_count:
        most_common_error_type["error_type"] = most_common_err
        most_common_error_type["count"] = total_err_count
        return most_common_error_type
    for err,count in error_type_count.items():
        if total_err_count < count:
            total_err_count = count
            most_common_err = err
    most_common_error_type["error_type"] = most_common_err
    most_common_error_type["count"] = total_err_count
    return most_common_error_type






