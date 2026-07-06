"""
FastAPI server for AVES - Adaptive Vision Enhancement System.

Run the API with:
    uvicorn main:app --reload

Run the original full-video pipeline with:
    python main.py --cli
"""

import base64
import os
import tempfile
import time
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import src.config as config
from src.detect import ObjectDetector
from src.enhancement import ImageEnhancer
from src.hazard import HazardDetector
from src.output import OutputManager
from src.pipeline import VideoPipeline
from src.scene_analyzer import SceneAnalyzer

app = FastAPI(
    title="AVES API",
    description="Adaptive Vision Enhancement System backend for demo analysis and video processing.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path(config.OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/outputs",
    StaticFiles(directory="output", html=False, check_dir=True),
    name="outputs"
)

scene_analyzer = SceneAnalyzer()
enhancer = ImageEnhancer()
detector = ObjectDetector()
hazard_detector = HazardDetector()
output_manager = OutputManager()


class SampleRequest(BaseModel):
    sample: Literal["day", "night"] = "night"


class VideoRequest(BaseModel):
    sample: Literal["day", "night"] = "night"


def _video_path(sample: str) -> Path:
    return Path(config.DAY_VIDEO if sample == "day" else config.NIGHT_VIDEO)


def _image_to_data_url(frame) -> str:
    ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
    if not ok:
        raise HTTPException(status_code=500, detail="Could not encode analysis frame.")
    encoded = base64.b64encode(buffer).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _scene_payload(scene):
    return {
        "mode": scene.mode,
        "brightness": round(scene.brightness, 2),
        "contrast": round(scene.contrast, 2),
        "saturation": round(scene.saturation, 2),
        "glarePercent": round(scene.glare_percent, 2),
        "darkPercent": round(scene.dark_percent, 2),
        "exposure": scene.exposure,
    }


def _detection_payload(detection):
    return {
        "vehicles": detection["vehicles"],
        "persons": detection["persons"],
        "trafficLights": detection["traffic_lights"],
        "objects": [
            {
                "label": item["label"].title(),
                "box": list(item["box"]),
                "distance": item["distance"],
                "confidence": round(float(item["confidence"]), 3),
            }
            for item in detection["objects"]
        ],
    }


def analyze_frame(frame):
    started = time.perf_counter()
    frame = cv2.resize(frame, (config.PROCESS_WIDTH, config.PROCESS_HEIGHT), interpolation=cv2.INTER_AREA)

    scene = scene_analyzer.analyze(frame)
    enhanced = enhancer.enhance(frame, scene)
    detection = detector.detect(enhanced)

    annotated = hazard_detector.process(detection["frame"], detection)
    annotated = hazard_detector.draw_warning(annotated)
    annotated = output_manager.draw_dashboard(annotated, scene, detection, 0.0)
    comparison = output_manager.comparison(frame, annotated)
    comparison = output_manager.draw_labels(comparison)

    return {
        "scene": _scene_payload(scene),
        "detections": _detection_payload(detection),
        "warning": hazard_detector.warning or "CLEAR",
        "processingMs": round((time.perf_counter() - started) * 1000, 1),
        "detectorAvailable": detector.available,
        "images": {
            "original": _image_to_data_url(frame),
            "enhanced": _image_to_data_url(annotated),
            "comparison": _image_to_data_url(comparison),
        },
    }


@app.get("/api/health")
def health():
    return {
        "status": "ready",
        "name": "AVES",
        "detectorAvailable": detector.available,
        "processSize": {"width": config.PROCESS_WIDTH, "height": config.PROCESS_HEIGHT},
        "outputDir": str(OUTPUT_DIR),
    }


@app.get("/api/samples")
def samples():
    return {
        "samples": [
            {"id": "day", "label": "Day glare sample", "available": _video_path("day").exists()},
            {"id": "night", "label": "Night headlight sample", "available": _video_path("night").exists()},
        ],
        "outputs": {
            "enhanced": "/outputs/enhanced.mp4" if Path(config.OUTPUT_ENHANCED).exists() else None,
            "comparison": "/outputs/comparison.mp4" if Path(config.OUTPUT_COMPARISON).exists() else None,
        },
    }


@app.post("/api/analyze-sample")
def analyze_sample(payload: SampleRequest):
    path = _video_path(payload.sample)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Sample video not found: {path}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise HTTPException(status_code=422, detail="Could not open sample video.")

    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise HTTPException(status_code=422, detail="Could not read the first frame from the sample video.")

    result = analyze_frame(frame)
    result["source"] = {"type": "sample", "sample": payload.sample, "path": str(path)}
    return result


@app.post("/api/analyze-upload")
async def analyze_upload(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Upload an image or a short video file.")

    suffix = Path(file.filename or "upload").suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if suffix in {".mp4", ".mov", ".avi", ".mkv"}:
            cap = cv2.VideoCapture(tmp_path)
            ret, frame = cap.read()
            cap.release()
        else:
            image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
            ret, frame = image is not None, image

        if not ret:
            raise HTTPException(status_code=422, detail="Could not read a frame from the uploaded file.")

        result = analyze_frame(frame)
        result["source"] = {"type": "upload", "filename": file.filename}
        return result
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


@app.post("/api/process-video")
def process_video(payload: VideoRequest):

    print("1. Endpoint called")

    path = _video_path(payload.sample)

    previous_preview = config.SHOW_PREVIEW

    try:
        config.SHOW_PREVIEW = False

        print("2. Creating pipeline")

        pipeline = VideoPipeline(str(path))

        print("3. Running pipeline")

        pipeline.run()

        print("4. Pipeline finished")

    finally:
        config.SHOW_PREVIEW = previous_preview

    print("5. Returning response")

    return {
        "status": "complete",
        "sample": payload.sample,
        "outputs": {
            "enhanced": "/outputs/enhanced.mp4",
            "comparison": "/outputs/comparison.mp4",
        },
    }


@app.get("/")
def root():
    return {"message": "AVES API is running. Open the React dashboard on http://localhost:5173."}


@app.get("/download/{name}")
def download_output(name: Literal["enhanced.mp4", "comparison.mp4"]):
    path = OUTPUT_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Output file has not been generated yet.")
    return FileResponse(path, media_type="video/mp4", filename=name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AVES backend")
    parser.add_argument("--cli", action="store_true", help="Run the original video pipeline")
    args = parser.parse_args()

    if args.cli:
        VideoPipeline(config.DEFAULT_VIDEO).run()
    else:
        import uvicorn

        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
