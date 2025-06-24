# app/api/routes_infer.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import cv2, numpy as np, base64, hashlib, uuid, json
from ..core.yolo import get_det_model, get_cls_models

router = APIRouter()

class InferResult(BaseModel):
    frame_id: str
    boxes: list   # [{bbox, label, conf}]
    image_b64: str

@router.post("/infer", response_model=InferResult)
async def infer_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "Not an image")

    det_model   = get_det_model()
    cls_models  = get_cls_models()
    det_res     = det_model(frame)[0]

    output = []
    for box in det_res.boxes:
        x1,y1,x2,y2 = map(int, box.xyxy[0])
        cls_name = det_res.names[int(box.cls[0])]
        roi = frame[y1:y2, x1:x2]
        if cls_name.lower() in cls_models:
            cls_res   = cls_models[cls_name.lower()](roi)[0]
            state_lbl = cls_res.names[int(cls_res.probs.top1)]
        else:
            state_lbl = "unknown"
        output.append({
            "bbox": [x1,y1,x2,y2],
            "label": f"{cls_name}:{state_lbl}",
            "conf":  float(box.conf[0])
        })

    # draw for quick preview
    preview = frame.copy()
    for o in output:
        x1,y1,x2,y2 = o["bbox"]
        cv2.rectangle(preview,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.putText(preview,o["label"],(x1,y1-6),
                    cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)
    _, jpeg = cv2.imencode('.jpg', preview)
    img_b64 = base64.b64encode(jpeg).decode()

    return InferResult(
        frame_id=str(uuid.uuid4()),
        boxes=output,
        image_b64=img_b64
    )

