# 🍽️ Realtime Dispatch Monitoring System

An intelligent dispatch monitoring system for a commercial kitchen.  
Built with **FastAPI**, **YOLO** (Ultralytics) and **OpenCV**,  
including:
- Realtime object detection (dish & tray)
- State classification for each detected item
- Easy user feedback to improve the AI model (in progress)

---

##  **Features**

Realtime video feed (from webcam or video file)  
Automatic detection and classification  
Visual bounding boxes and labels  
Web UI to capture frames, draw/edit bounding boxes, and submit feedback  (in progress)
Feedback is saved as image + JSON for easy retraining                    (in progress)
Fully containerized with **Docker + Docker Compose**

---

## 📂 **Project Structure**

project/
├── app/ # FastAPI backend
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
---

## ⚙️ **Prerequisites**

- Python **3.10+**
- `pip` or `venv`
- Optional: **Docker & Docker Compose**

---

## ⚡ **How to Run Locally**

# Clone the repository
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000

# Open browser:
http://127.0.0.1:8000
