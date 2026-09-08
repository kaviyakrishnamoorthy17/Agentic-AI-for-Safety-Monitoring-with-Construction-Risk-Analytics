from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# This creates (or connects to) a file called site_risk.db in your project folder
engine = create_engine("sqlite:///site_risk.db")

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True)
    project_name = Column(String)
    location = Column(String)
    start_date = Column(DateTime)
    status = Column(String)


class SiteRisk(Base):
    __tablename__ = "site_risks"

    risk_id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    risk_type = Column(String)
    severity = Column(String)
    detected_at = Column(DateTime)


class PPEViolation(Base):
    __tablename__ = "ppe_violations"

    violation_id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    worker_id = Column(Integer, nullable=True)
    violation_type = Column(String)
    timestamp = Column(DateTime)


class WorkerDetection(Base):
    __tablename__ = "worker_detections"

    detection_id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    timestamp = Column(DateTime)


# Create a reusable session so other files can save/query data
Session = sessionmaker(bind=engine)


def init_db():
    """Creates the tables in the database file. Run this once."""
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")


def save_hazard(risk_type, severity, project_id=1):
    """Saves a single hazard record into the site_risks table."""
    session = Session()
    new_risk = SiteRisk(
        project_id=project_id,
        risk_type=risk_type,
        severity=severity,
        detected_at=datetime.now()
    )
    session.add(new_risk)
    session.commit()
    session.close()


def save_ppe_violation(violation_type, severity=None, project_id=1):
    """Saves a single PPE violation record into the ppe_violations table."""
    session = Session()
    new_violation = PPEViolation(
        project_id=project_id,
        violation_type=violation_type,
        timestamp=datetime.now()
    )
    session.add(new_violation)
    session.commit()
    session.close()


def log_worker_detection(project_id=1):
    """Logs that at least one worker (person) was seen in a frame."""
    session = Session()
    new_detection = WorkerDetection(
        project_id=project_id,
        timestamp=datetime.now()
    )
    session.add(new_detection)
    session.commit()
    session.close()


# This only runs when you execute this file directly (python src/models/database.py)
if __name__ == "__main__":
    init_db()