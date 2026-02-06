from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")   # lightweight + fast


def detect_crowd(frame):

    results = model(frame, conf=0.4)

    person_count = 0

    for r in results:
        boxes = r.boxes

        if boxes is not None:
            for box in boxes:

                cls = int(box.cls[0])

                # class 0 = person (COCO dataset)
                if cls == 0:
                    person_count += 1

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

    return frame, person_count
