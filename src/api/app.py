import sys
import os

# Allow importing from analytics and models folders
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analytics"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from risk_score import get_risk_score
from safety_score import get_safety_score
from database import Session, SiteRisk, PPEViolation

app = Flask(__name__)
CORS(app)  # allows a frontend on a different port to call this API


@app.route("/api/risk-score", methods=["GET"])
def risk_score_endpoint():
    """Returns the current risk score for project_id=1 as JSON."""
    result = get_risk_score(project_id=1)
    return jsonify(result)


@app.route("/api/hazards", methods=["GET"])
def hazards_endpoint():
    """Returns all hazard records currently stored in the database."""
    session = Session()
    hazards = session.query(SiteRisk).all()
    session.close()

    hazard_list = [
        {
            "risk_id": h.risk_id,
            "project_id": h.project_id,
            "risk_type": h.risk_type,
            "severity": h.severity,
            "detected_at": h.detected_at.isoformat()
        }
        for h in hazards
    ]
    return jsonify(hazard_list)


@app.route("/api/safety-score", methods=["GET"])
def safety_score_endpoint():
    """Returns the current PPE safety score for project_id=1 as JSON."""
    result = get_safety_score(project_id=1)
    return jsonify(result)


@app.route("/api/ppe-violations", methods=["GET"])
def ppe_violations_endpoint():
    """Returns all PPE violation records currently stored in the database."""
    session = Session()
    violations = session.query(PPEViolation).all()
    session.close()

    violation_list = [
        {
            "violation_id": v.violation_id,
            "project_id": v.project_id,
            "violation_type": v.violation_type,
            "timestamp": v.timestamp.isoformat()
        }
        for v in violations
    ]
    return jsonify(violation_list)


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Serves the site risk dashboard UI."""
    return send_from_directory("static", "dashboard.html")


@app.route("/safety-dashboard", methods=["GET"])
def safety_dashboard():
    """Serves the safety analytics dashboard UI."""
    return send_from_directory("static", "safety_dashboard.html")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Site Risk Monitoring API is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)