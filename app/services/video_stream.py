# app/services/video_stream.py
import cv2, base64, asyncio
from fastapi import WebSocket, APIRouter
router_ws = APIRouter()

@router_ws.websocket("/ws/rtsp")
async def ws_rtsp(websocket: WebSocket, url: str):
    await websocket.accept()
    cap = cv2.VideoCapture(url)
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        # (gọi infer như trên hoặc chỉ gửi raw frame)
        _, jpg = cv2.imencode('.jpg', frame)
        await websocket.send_bytes(jpg.tobytes())
        await asyncio.sleep(0.04)   # 25 fps
