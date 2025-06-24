﻿# 🍽️ Realtime Dispatch Monitoring System

An intelligent dispatch monitoring system for a commercial kitchen.  
Built with **FastAPI**, **YOLO** and **OpenCV**,  
including:

- Realtime object detection (dish & tray)
- State classification for each detected item
- Easy user feedback to improve the AI model (in progress)

---

## **Features**

Realtime video feed (from webcam or video file)  
Automatic detection and classification  
Visual bounding boxes and labels  
Web UI to capture frames, draw/edit bounding boxes, and submit feedback
Feedback is saved as image + JSON for easy retraining (in progress)

Fully containerized with **Docker + Docker Compose**

---

## 📂 **Project Structure**

```plaintext
project/
├── app/ # FastAPI backend
│ ├── another folders
│ ├── main.py
│ ├── streaming.py
├── web/ # Frontend (HTML, CSS, JS)
│ ├── index.html
│ ├── js/
│ ├── css/
├── models/ # YOLO models (best.pt, best_tray.pt, best_dish.pt)
├── feedback_frames/ # Saved user feedback (auto-created)
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── README.md
```

---

## ⚙️ **Prerequisites**

- Python **3.10+**
- `pip` or `venv`
- Optional: **Docker & Docker Compose**

---

# ⚡ **How to Run Locally**

# ☁️Clone from Github

## Clone the repository

git clone https://github.com/1espoirhenri/EATLAB-Exam1-Streaming.git
cd /EATLAB-Exam1-Streaming

## Install dependencies

pip install -r requirements.txt

## Run FastAPI server

uvicorn app.main:app --reload --port 8000

## Open browser:

http://127.0.0.1:8000

# 🐳 Clone from Docker Compose

## Pull project from Docker Compose

docker pull 1espoirhenri/dispatch-monitoring:latest

## Run with this command

docker run -d \
 -p 8000:8000 \
 -v $PWD/feedback_frames:/app/feedback_frames \
 --name dispatch_monitoring \
 1espoirhenri/dispatch-monitoring:latest

## Open browser:

http://127.0.0.1:8000
