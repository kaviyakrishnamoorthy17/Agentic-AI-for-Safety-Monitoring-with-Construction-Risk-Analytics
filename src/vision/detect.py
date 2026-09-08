from ultralytics import YOLO
import cv2

# Load a pretrained YOLOv8 model (small version, fast for testing)
model = YOLO("yolov8n.pt")

# Open the laptop webcam (0 = default camera)
cap = cv2.VideoCapture(0)

while True:
    # Read one frame from the webcam
    success, frame = cap.read()
    if not success:
        break

    # Run YOLOv8 detection on this frame
    results = model(frame)

    # Draw the detection boxes on the frame
    annotated_frame = results[0].plot() # type: ignore

    # Show the frame in a window
    cv2.imshow("Construction Site Detection", annotated_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()