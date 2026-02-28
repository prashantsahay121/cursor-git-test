import cv2
import threading

# Replace with your mobile IP
IP_CAMERA_URL = "http://192.168.1.11:8080/video"

latest_frame = None
camera_running = False


def start_camera():
    global latest_frame, camera_running

    cap = cv2.VideoCapture(IP_CAMERA_URL)

    if not cap.isOpened():
        print("Cannot access mobile camera")
        return

    camera_running = True
    print("Mobile camera started...")

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        latest_frame = frame
        small_frame = cv2.resize(frame, (640, 480))
        cv2.imshow("Mobile Camera", small_frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def capture_current_frame(output_path="captured.jpg"):
    global latest_frame

    if latest_frame is None:
        print("No frame available")
        return None

    cv2.imwrite(output_path, latest_frame)
    return output_path


def stop_camera():
    global camera_running
    camera_running = False