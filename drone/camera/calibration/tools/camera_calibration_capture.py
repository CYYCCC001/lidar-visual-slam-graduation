#!/usr/bin/env python3
import os
import sys
import cv2


DEVICE = "/dev/video0"
OUTPUT_DIR = "/home/nvidia/camera_calibration_images_live40"
WIDTH = 1280
HEIGHT = 720
TARGET_COUNT = 40
PATTERN = (9, 6)  # inner corners: columns x rows


def existing_count():
    if not os.path.isdir(OUTPUT_DIR):
        return 0
    names = os.listdir(OUTPUT_DIR)
    numbers = []
    for name in names:
        if not name.startswith("calib_") or not name.endswith(".jpg"):
            continue
        try:
            numbers.append(int(name[6:-4]))
        except ValueError:
            pass
    return max(numbers, default=0)


def find_corners(gray):
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
    found, corners = cv2.findChessboardCorners(gray, PATTERN, flags)
    if found:
        criteria = (
            cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001,
        )
        corners = cv2.cornerSubPix(
            gray,
            corners,
            (11, 11),
            (-1, -1),
            criteria,
        )
    return found, corners


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    saved = existing_count()

    print("Opening camera:", DEVICE)
    print("Output directory:", OUTPUT_DIR)
    print("Existing images:", saved)
    print("Controls: SPACE or s = save, q or ESC = quit")
    print("A green 9x6 corner overlay is required before saving.")

    cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(
            "Cannot open /dev/video0. Close GStreamer and other camera programs."
        )

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera format reported by OpenCV: {actual_width}x{actual_height}")

    try:
        cv2.namedWindow("C330 calibration", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("C330 calibration", WIDTH, HEIGHT)
    except cv2.error as exc:
        cap.release()
        raise RuntimeError(
            "OpenCV cannot create a GUI window. Run this on the desktop terminal, "
            "not a headless shell, and check DISPLAY."
        ) from exc

    try:
        while saved < TARGET_COUNT:
            ok, frame = cap.read()
            if not ok or frame is None:
                print("Camera frame read failed.", file=sys.stderr)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = find_corners(gray)
            display = frame.copy()

            if found:
                cv2.drawChessboardCorners(display, PATTERN, corners, True)
                color = (0, 220, 0)
                message = "READY: press SPACE or s to save"
            else:
                color = (0, 0, 255)
                message = "MOVE BOARD: 9x6 corners not found"

            cv2.putText(
                display,
                f"{message}   SAVED: {saved}/{TARGET_COUNT}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("C330 calibration", display)
            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):
                break

            if key in (ord("s"), 32, 10, 13):
                if not found:
                    print("Not saved: complete 9x6 corners were not detected.")
                    continue

                saved += 1
                path = os.path.join(OUTPUT_DIR, f"calib_{saved:02d}.jpg")
                ok = cv2.imwrite(
                    path,
                    frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 95],
                )
                if not ok or not os.path.isfile(path) or os.path.getsize(path) == 0:
                    saved -= 1
                    print("Save failed:", path, file=sys.stderr)
                else:
                    print(f"Saved {saved}/{TARGET_COUNT}: {path}")

    finally:
        cap.release()
        cv2.destroyAllWindows()

    print(f"Capture finished. Valid images saved: {saved}")
    print("Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
