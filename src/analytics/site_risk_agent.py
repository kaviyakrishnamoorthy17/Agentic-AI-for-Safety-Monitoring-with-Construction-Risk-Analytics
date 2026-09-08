from datetime import datetime, timedelta

# Define a "restricted zone" as a rectangle on the frame (x1, y1, x2, y2)
RESTRICTED_ZONE = (0, 0, 200, 480)

# How many people at once counts as "overcrowding"
CROWD_LIMIT = 3

# How many seconds to wait before allowing the SAME hazard type to log again
COOLDOWN_SECONDS = 5

# Keeps track of the last time each hazard type was logged
last_logged_time = {}


def should_log(risk_type):
    """
    Checks if enough time has passed since this risk_type was last logged.
    Returns True if it's okay to log again, False if still in cooldown.
    """
    now = datetime.now()

    if risk_type not in last_logged_time:
        last_logged_time[risk_type] = now
        return True

    time_since_last = now - last_logged_time[risk_type]

    if time_since_last > timedelta(seconds=COOLDOWN_SECONDS):
        last_logged_time[risk_type] = now
        return True

    return False


def check_hazards(results):
    """
    Takes YOLOv8 results for one frame and returns a list of hazard dictionaries.
    Only returns a hazard if it isn't still in cooldown.
    """
    hazards = []

    person_count = 0
    person_boxes = []

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = results[0].names[class_id]

        if class_name == "person":
            person_count += 1
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            person_boxes.append((x1, y1, x2, y2))

    # RULE 1: Too many people clustered together
    if person_count >= CROWD_LIMIT:
        if should_log("Overcrowding"):
            hazards.append({
                "risk_type": "Overcrowding",
                "severity": "Medium",
                "detected_at": datetime.now()
            })

    # RULE 2: A person is inside the restricted zone
    for (x1, y1, x2, y2) in person_boxes:
        rx1, ry1, rx2, ry2 = RESTRICTED_ZONE
        if x1 < rx2 and x2 > rx1 and y1 < ry2 and y2 > ry1:
            if should_log("Restricted Zone Entry"):
                hazards.append({
                    "risk_type": "Restricted Zone Entry",
                    "severity": "High",
                    "detected_at": datetime.now()
                })
            break  # only need to log this once per frame, even with multiple people

    return hazards