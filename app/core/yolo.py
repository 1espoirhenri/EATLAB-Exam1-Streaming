# app/core/yolo.py
from ultralytics import YOLO
from functools import lru_cache

@lru_cache(maxsize=1)
def get_det_model():
    return YOLO("./app/models/best.pt")

@lru_cache(maxsize=1)
def get_cls_models():
    return {
        "dish": YOLO("./app/models/best_dish.pt"),
        "tray": YOLO("./app/models/best_tray.pt")
    }
