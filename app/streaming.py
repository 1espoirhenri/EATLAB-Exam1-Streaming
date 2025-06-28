from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import StreamingResponse, PlainTextResponse, JSONResponse
from ultralytics import YOLO
import cv2
import shutil, uuid, json
from pathlib import Path
import io

router = APIRouter()

# === Cấu hình đường dẫn ===
BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_DIR = BASE_DIR / "feedback_frames"
FEEDBACK_DIR.mkdir(exist_ok=True)

# === Load mô hình ===
det_model = YOLO("./app/models/best.pt")
cls_tray = YOLO("./app/models/best_tray.pt")
cls_dish = YOLO("./app/models/best_dish.pt")

cap = cv2.VideoCapture(0)
last_frame = None
last_detections = []  # Lưu kết quả detect gần nhất

# === Stream video detect real-time ===
def gen_frames():
    global last_frame, last_detections
    while True:
        success, frame = cap.read()
        if not success:
            break

        last_frame = frame.copy()
        last_detections = []

        # B1: Detect
        det_results = det_model.predict(frame, conf=0.3, verbose=False)[0]

        for box in det_results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            det_label = det_results.names[cls_id]

            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            if det_label.lower() == "tray":
                cls_result = cls_tray(roi, verbose=False)[0]
            elif det_label.lower() == "dish":
                cls_result = cls_dish(roi, verbose=False)[0]
            else:
                cls_result = None

            if cls_result:
                cls_label = cls_result.names[int(cls_result.probs.top1)]
            else:
                cls_label = "unknown"

            label_text = f"{det_label}:{cls_label}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, label_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            last_detections.append({
                "bbox": [x1, y1, x2, y2],
                "label": label_text
            })

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


# === API ===

@router.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(),
                             media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/api/current_frame")
def get_frame():
    global last_frame
    if last_frame is None:
        return PlainTextResponse("Frame not ready yet", status_code=404)
    ret, jpeg = cv2.imencode('.jpg', last_frame)
    return StreamingResponse(io.BytesIO(jpeg.tobytes()), media_type="image/jpeg")

@router.get("/api/last_detections")
def get_last_detections():
    return JSONResponse(content=last_detections)

@router.post("/api/feedback")
async def save_feedback(file: UploadFile, bboxes: str = Form(...)):
    frame_id = str(uuid.uuid4())
    FEEDBACK_DIR.mkdir(exist_ok=True)
    with open(FEEDBACK_DIR / f"{frame_id}.jpg", "wb") as f:
        shutil.copyfileobj(file.file, f)
    with open(FEEDBACK_DIR / f"{frame_id}.json", "w") as f:
        json.dump(json.loads(bboxes), f, indent=2)
    return {"status": "saved", "frame_id": frame_id}
