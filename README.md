# AVES - Adaptive Vision Enhancement System

AVES enhances driving video for difficult visibility conditions, then overlays road-user detection, scene metrics, and warning signals for a judge-ready demo.

## Run the FastAPI backend

```powershell
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API docs open at `http://127.0.0.1:8000/docs`.

## Run the React dashboard

```powershell
cd frontend
npm install
npm run dev
```

Dashboard opens at `http://127.0.0.1:5173` and connects to the API at `http://127.0.0.1:8000`.

## Demo flow

1. Start the backend.
2. Start the dashboard.
3. Choose the day or night sample.
4. Click `Analyze Frame` for instant metrics and before/after output.
5. Click `Process Video` to generate `output/enhanced.mp4` and `output/comparison.mp4`.

The original CLI pipeline is still available with:

```powershell
python main.py --cli
```
