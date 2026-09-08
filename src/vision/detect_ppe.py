from ultralytics import YOLO
import cv2
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analytics"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))

from safety_agent import check_ppe_violations, should_log_worker_presence
from database import save_ppe_violation, log_worker_detection
from email_alert import send_alert_email


model = YOLO("runs/detect/ppe_detector_continued/weights/best.pt")
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    results = model(frame)
    annotated_frame = results[0].plot()  # type: ignore

    violations, person_count = check_ppe_violations(results)

    if person_count > 0 and should_log_worker_presence():
        log_worker_detection()

    for v in violations:
        save_ppe_violation(v['violation_type'])
        print(f"[VIOLATION] {v['violation_type']} - Severity: {v['severity']} - Time: {v['detected_at']}")

        if v['severity'] == "High":
            send_alert_email(v['violation_type'], v['severity'], v['detected_at'])

    cv2.imshow("PPE Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()