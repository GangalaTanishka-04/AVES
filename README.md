# AVES – Adaptive Vision Enhancement System

AVES (Adaptive Vision Enhancement System) is an AI-powered application designed to improve driving visibility under challenging lighting conditions such as nighttime, low-light environments, and glare. The system enhances road scene visibility while providing object detection and scene analysis through an interactive web interface.

## Live Demo

Frontend: https://aves-dashboard.vercel.app

Backend API: https://<your-render-service>.onrender.com

> **Note:** The backend is hosted on Render's free tier. If it has been inactive, open the backend URL above once to wake up the service (30–60 seconds). After that, refresh the frontend to use the application.

## Features

- Image and video upload support
- Low-light image enhancement
- Real-time object detection
- Scene analysis (brightness, contrast, glare, dark area)
- Driver warning generation
- RESTful backend APIs
- Interactive React dashboard
- Responsive user interface

## Tech Stack

### Frontend

- React
- JavaScript
- HTML
- CSS

### Backend

- FastAPI
- Python
- OpenCV

### Tools

- Git
- GitHub
- Vercel
- Render

---

## Project Structure

```
AVES/
│── frontend/
│── backend/
│── assets/
│── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/GangalaTanishka-04/AVES.git
cd AVES
```

### Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## How It Works

1. The user uploads an image or video.
2. The frontend sends the file to the FastAPI backend.
3. OpenCV processes the media and performs scene enhancement.
4. The backend analyzes the scene and detects road users.
5. The processed results are returned through REST APIs.
6. The React dashboard displays:
   - Enhanced output
   - Comparison view
   - Scene metrics
   - Object detection statistics
   - Driver warnings

---

## Future Improvements

- Real-time webcam processing
- Live video streaming
- Lane detection
- Traffic sign recognition
- Distance estimation
- Model optimization for edge devices

---

## Contributors

- Gangala Tanishka
- Kurva Bhavya
- Dhanashree chandekar
- Amlina panigrahi
- Shradhanjali das
- Team AVES

---

## Author

**Gangala Tanishka**

GitHub: https://github.com/GangalaTanishka-04

LinkedIn: https://www.linkedin.com/in/tanishka-gangala-61b19b323/
