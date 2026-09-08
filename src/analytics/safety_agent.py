from datetime import datetime, timedelta

COOLDOWN_SECONDS = 5
last_logged_time = {}

WORKER_LOG_COOLDOWN_SECONDS = 5
last_worker_log_time = {"last": None}


def should_log(violation_type):
    now = datetime.now()
    if violation_type not in last_logged_time:
        last_logged_time[violation_type] = now
        return True
    if now - last_logged_time[violation_type] > timedelta(seconds=COOLDOWN_SECONDS):
        last_logged_time[violation_type] = now
        return True
    return False


def should_log_worker_presence():
    now = datetime.now()
    if last_worker_log_time["last"] is None:
        last_worker_log_time["last"] = now  #type: ignore
        return True
    if now - last_worker_log_time["last"] > timedelta(seconds=WORKER_LOG_COOLDOWN_SECONDS):
        last_worker_log_time["last"] = now  #type: ignore
        return True
    return False


def check_ppe_violations(results):
    violations = []
    person_count = 0

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = results[0].names[class_id]

        if class_name == "Person":
            person_count += 1

        if class_name == "NO-Hardhat":
            if should_log("Missing Hardhat"):
                violations.append({
                    "violation_type": "Missing Hardhat",
                    "severity": "High",
                    "detected_at": datetime.now()
                })

        elif class_name == "NO-Safety Vest":
            if should_log("Missing Safety Vest"):
                violations.append({
                    "violation_type": "Missing Safety Vest",
                    "severity": "High",
                    "detected_at": datetime.now()
                })

        elif class_name == "NO-Mask":
            if should_log("Missing Mask"):
                violations.append({
                    "violation_type": "Missing Mask",
                    "severity": "Medium",
                    "detected_at": datetime.now()
                })

    return violations, person_count