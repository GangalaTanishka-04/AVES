"""
AVES Configuration File
All configurable parameters for the project.
"""

import os

# --------------------------------------------------
# Project Directories
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

DAY_VIDEO = os.path.join(DATA_DIR, "day_samples", "sample.mp4")
NIGHT_VIDEO = os.path.join(DATA_DIR, "night_samples", "sample.mp4")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# --------------------------------------------------
# Display Settings
# --------------------------------------------------

WINDOW_NAME = "AVES - Adaptive Vision Enhancement System"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

SHOW_FPS = True

# --------------------------------------------------
# Video Settings
# --------------------------------------------------

DEFAULT_VIDEO = DAY_VIDEO

# ESC key
EXIT_KEY = 27

# --------------------------------------------------
# Enhancement Parameters
# (Used later)
# --------------------------------------------------

GLARE_THRESHOLD = 230

DARK_THRESHOLD = 65

CLAHE_CLIP_LIMIT = 2.5

CLAHE_GRID_SIZE = (8, 8)

GAMMA = 1.6

# --------------------------------------------------
# YOLO Settings
# (Later)
# --------------------------------------------------

YOLO_MODEL = "yolov8n.pt"

CONFIDENCE_THRESHOLD = 0.35