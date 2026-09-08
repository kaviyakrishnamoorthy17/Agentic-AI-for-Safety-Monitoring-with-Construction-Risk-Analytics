from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from database import Session, PPEViolation, WorkerDetection


def get_safety_score(project_id=1, minutes=10):
    """
    Looks at PPE violations and worker activity in the last X minutes and calculates:
    - a safety score out of 100
    - overall PPE compliance rate (%)
    - total violation count
    - workers monitored count
    - compliance rate broken down by PPE type (Hardhat, Safety Vest, Mask)
    """
    session = Session()

    cutoff_time = datetime.now() - timedelta(minutes=minutes)

    recent_violations = session.query(PPEViolation).filter(
        PPEViolation.timestamp >= cutoff_time,
        PPEViolation.project_id == project_id
    ).all()

    recent_worker_logs = session.query(WorkerDetection).filter(
        WorkerDetection.timestamp >= cutoff_time,
        WorkerDetection.project_id == project_id
    ).all()

    session.close()

    # Points deducted per violation type
    penalty_per_violation = {
        "Missing Hardhat": 10,
        "Missing Safety Vest": 10,
        "Missing Mask": 5
    }

    total_penalty = 0
    violation_counts = {"Missing Hardhat": 0, "Missing Safety Vest": 0, "Missing Mask": 0}

    for v in recent_violations:
        total_penalty += penalty_per_violation.get(v.violation_type, 5)  # type: ignore
        if v.violation_type in violation_counts:
            violation_counts[v.violation_type] += 1  #type: ignore

    score = max(0, 100 - total_penalty)

    # Compliance rate per PPE type: rough estimate based on violation count vs a baseline
    max_expected_checks = 20  # assumed checks in the window, for a simple rate

    def type_compliance(count):
        return max(0, round(100 - (count / max_expected_checks * 100)))

    ppe_compliance = {
        "Hardhat": type_compliance(violation_counts["Missing Hardhat"]),
        "Safety Vest": type_compliance(violation_counts["Missing Safety Vest"]),
        "Mask": type_compliance(violation_counts["Missing Mask"])
    }

    overall_compliance_rate = round(sum(ppe_compliance.values()) / len(ppe_compliance))

    # Assign a risk level label based on score
    if score >= 80:
        level = "Low"
    elif score >= 60:
        level = "Medium"
    elif score >= 40:
        level = "High"
    else:
        level = "Critical"

    return {
        "score": score,
        "level": level,
        "compliance_rate": overall_compliance_rate,
        "violation_count": len(recent_violations),
        "workers_monitored": len(recent_worker_logs),
        "ppe_compliance": ppe_compliance
    }
    """
    Looks at PPE violations in the last X minutes and calculates:
    - a safety score out of 100
    - PPE compliance rate (%)
    - total violation count
    """
    session = Session()

    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    recent_violations = session.query(PPEViolation).filter(
        PPEViolation.timestamp >= cutoff_time,
        PPEViolation.project_id == project_id
    ).all()

    session.close()

    # Points deducted per violation type
    penalty_per_violation = {
        "Missing Hardhat": 10,
        "Missing Safety Vest": 10,
        "Missing Mask": 5
    }

    total_penalty = 0
    for v in recent_violations:
        total_penalty += penalty_per_violation.get(v.violation_type, 5) # type: ignore

    score = max(0, 100 - total_penalty)

    # Compliance rate: rough estimate based on violation count vs a baseline
    # (fewer violations = higher compliance)
    max_expected_checks = 20  # assumed checks in the window, for a simple rate
    compliance_rate = max(0, round(100 - (len(recent_violations) / max_expected_checks * 100)))

    # Assign a risk level label based on score
    if score >= 80:
        level = "Low"
    elif score >= 60:
        level = "Medium"
    elif score >= 40:
        level = "High"
    else:
        level = "Critical"

    return {
        "score": score,
        "level": level,
        "compliance_rate": compliance_rate,
        "violation_count": len(recent_violations)
    }