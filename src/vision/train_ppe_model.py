from ultralytics import YOLO
import os

# Get the path to the data.yaml file (relative to this script's location)
current_dir = os.path.dirname(__file__)
data_yaml_path = os.path.join(current_dir, "..", "analytics", "data", "ppe_dataset", "ppe_data.yaml")

# Load a small pretrained YOLOv8 model as our starting point
model = YOLO("runs/detect/ppe_detector_quick/weights/best.pt")

# Train it on our PPE dataset
# epochs = how many times it goes through the full dataset (start small to test, increase later)
# imgsz = image size used during training (640 is a common default)
results = model.train(
    data=data_yaml_path,
    epochs=15,        # fewer passes (was 20)
    imgsz=320,        # smaller images (was 640) = much faster math
    batch=4,          # smaller batch = less memory/CPU load per step
    name="ppe_detector_continued",
)

print("Training complete! Check the runs/detect/ppe_detector/weights/ folder for your trained model.")      