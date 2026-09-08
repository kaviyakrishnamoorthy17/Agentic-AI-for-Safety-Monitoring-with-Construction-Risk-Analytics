from ultralytics import YOLO
import cv2
import sys
import os

# Allow importing from the analytics folder
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analytics"))
from site_risk_agent import check_hazards

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "models"))
from database import save_hazard
# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    # Run detection
    results = model(frame)

    # Draw detection boxes
    annotated_frame = results[0].plot() # type: ignore

    # Check for hazards using our Site Risk Agent
    hazards = check_hazards(results)

    # Save and print any hazards found this frame
    for hazard in hazards:
        save_hazard(hazard['risk_type'], hazard['severity'])
        print(f"[HAZARD] {hazard['risk_type']} - Severity: {hazard['severity']} - Time: {hazard['detected_at']}")

    # Show the frame
    cv2.imshow("Site Risk Monitoring", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()