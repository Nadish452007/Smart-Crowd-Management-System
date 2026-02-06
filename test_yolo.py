import cv2
import os

# UPDATED path to match the double extension seen in your screenshot
video_path = r"C:\Users\Nadish\Downloads\railway_demo.mp4.mp4"

# Check if the file exists before opening
if not os.path.exists(video_path):
    print(f"Video file not found at {video_path}")
    exit()

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video or cannot read the frame.")
        break

    cv2.imshow("Video Playback", frame)

    # Press ESC key to exit early
    if cv2.waitKey(25) & 0xFF == 27:
        print("Playback stopped by user.")
        break

cap.release()
cv2.destroyAllWindows()