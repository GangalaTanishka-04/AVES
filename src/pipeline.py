"""
pipeline.py

Core video processing pipeline for AVES.
Every frame passes through this class.

Future Flow:

Capture Frame
      │
      ▼
Object Detection
      │
      ▼
Day/Night Detection
      │
      ▼
Image Enhancement
      │
      ▼
Output Rendering
"""

import cv2
import time
import numpy as np

import src.config as config


class VideoPipeline:

    def __init__(self, source=config.DEFAULT_VIDEO):

        self.source = source

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception(f"Cannot open video source:\n{source}")

        self.prev_time = time.time()

        self.frame_count = 0

        self.fps = 0

        print("Video Pipeline Initialized Successfully")

    # ----------------------------------------------------

    def calculate_fps(self):

        current_time = time.time()

        self.fps = 1 / (current_time - self.prev_time)

        self.prev_time = current_time

    # ----------------------------------------------------

    def preprocess_frame(self, frame):

        """
        Reserved for future resizing,
        color conversion etc.
        """

        frame = cv2.resize(
            frame,
            (config.FRAME_WIDTH, config.FRAME_HEIGHT)
        )

        return frame

    # ----------------------------------------------------

    def process_frame(self, frame):

        """
        Complete processing pipeline.

        Later this function will call:

        detect.py

        glare.py

        nightmode.py

        enhance.py
        """

        processed_frame = frame.copy()

        return processed_frame

    # ----------------------------------------------------

    def draw_information(self, frame):

        if config.SHOW_FPS:

            cv2.putText(
                frame,
                f"FPS : {int(self.fps)}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.putText(
            frame,
            "AVES",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        return frame

    # ----------------------------------------------------

    def create_comparison(self, original, processed):

        comparison = np.hstack((original, processed))

        return comparison

    # ----------------------------------------------------

    def display_frame(self, frame):

        cv2.imshow(config.WINDOW_NAME, frame)

    # ----------------------------------------------------

    def run(self):

        while True:

            ret, frame = self.cap.read()

            if not ret:
                print("End of video.")
                break

            self.calculate_fps()

            frame = self.preprocess_frame(frame)

            processed = self.process_frame(frame)

            processed = self.draw_information(processed)

            comparison = self.create_comparison(frame, processed)

            self.display_frame(comparison)

            self.frame_count += 1

            key = cv2.waitKey(1)

            if key == config.EXIT_KEY:
                break

        self.cap.release()

        cv2.destroyAllWindows()

        print(f"Processed {self.frame_count} frames.")