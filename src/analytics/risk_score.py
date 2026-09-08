import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from datetime import datetime, timedelta
from database import Session, SiteRisk

# How much each severity level contributes to the score
SEVERITY_WEIGHTS = {
    "Low": 1,
    "Medium": 3,
    "High": 5
}

# Only count hazards from the last N minutes when scoring "current" risk
LOOKBACK_MINUTES = 10

# Score thresholds for classifying overall risk level
RISK_LEVELS = [
    (0, "Low"),
    (5, "Medium"),
    (12, "High"),
    (20, "Critical")
]


def get_risk_score(project_id=1):
    """
    Looks at recent hazards for a project and returns:
    { "score": int, "level": str, "hazard_count": int }
    """
    session = Session()
    cutoff = datetime.now() - timedelta(minutes=LOOKBACK_MINUTES)

    recent_hazards = (
        session.query(SiteRisk)
        .filter(SiteRisk.project_id == project_id)
        .filter(SiteRisk.detected_at >= cutoff)
        .all()
    )
    session.close()

    score = 0
    for hazard in recent_hazards:
        score += SEVERITY_WEIGHTS.get(hazard.severity, 0) # type: ignore

    level = "Low"
    for threshold, label in RISK_LEVELS:
        if score >= threshold:
            level = label

    return {
        "score": score,
        "level": level,
        "hazard_count": len(recent_hazards)
    }


if __name__ == "__main__":
    result = get_risk_score()
    print(f"Current risk score: {result['score']} ({result['level']}) "
          f"based on {result['hazard_count']} recent hazard(s)")