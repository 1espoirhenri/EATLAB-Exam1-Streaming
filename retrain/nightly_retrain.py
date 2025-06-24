#!/usr/bin/env python3
"""
$ python retrain/nightly_retrain.py          # tự gọi trong cron 02:00 mỗi đêm

Yêu cầu:
    pip install ultralytics tqdm sqlalchemy pyyaml opencv-python-headless
"""
from __future__ import annotations

import os, shutil, json, subprocess, datetime, uuid
from pathlib import Path
from typing import List

import cv2
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import SessionLocal
from app.db import models

# ---------- helper ----------
def ensure_dirs():
    for p in [
        settings.FEEDBACK_IMAGE_DIR,
        settings.YOLO_DATASET_DIR / "images" / "train",
        settings.YOLO_DATASET_DIR / "labels" / "train",
    ]:
        p.mkdir(parents=True, exist_ok=True)


def fetch_unexported(db: Session):
    """
    Trả về list[models.Feedback] chưa export.
    Bạn cần tạo cột 'exported' INT default 0 trong bảng feedback (manual hoặc Alembic).
    """
    return db.query(models.Feedback).filter(models.Feedback.exported == 0).all()


def mark_exported(db: Session, ids: List[str]):
    if not ids:
        return
    db.query(models.Feedback).filter(models.Feedback.id.in_(ids)).update(
        {"exported": 1}, synchronize_session=False
    )
    db.commit()


def write_yolo_row(txt_path: Path, cls_id: int, xyxy: list[int], img_w: int, img_h: int):
    """Append 1 dòng nhãn YOLO vào file .txt"""
    x1, y1, x2, y2 = xyxy
    cx = (x1 + x2) / 2.0 / img_w
    cy = (y1 + y2) / 2.0 / img_h
    w = (x2 - x1) / img_w
    h = (y2 - y1) / img_h
    with txt_path.open("a") as f:
        f.write(f"{cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")


def create_dataset(rows: List[models.Feedback]) -> bool:
    """
    Copy frames & sinh label .txt
    Return True nếu có dữ liệu mới.
    """
    if not rows:
        print("No new feedback ➜ skip retrain.")
        return False

    for r in rows:
        # ===== 1) Xác định file frame gốc =====
        # Khi infer, bạn nên lưu frame JPEG vào FEEDBACK_IMAGE_DIR
        # với tên = <frame_id>.jpg  (frame_id chính là r.frame_hash)
        src_img = settings.FEEDBACK_IMAGE_DIR / f"{r.frame_hash}.jpg"
        if not src_img.exists():
            print(f"[WARN] missing frame file {src_img}")
            continue

        # ===== 2) Copy sang dataset/images/train =====
        dst_img = (
            settings.YOLO_DATASET_DIR
            / "images"
            / "train"
            / f"{r.frame_hash}.jpg"
        )
        if not dst_img.exists():
            shutil.copy2(src_img, dst_img)

        # ===== 3) Viết label txt =====
        dst_txt = (
            settings.YOLO_DATASET_DIR
            / "labels"
            / "train"
            / f"{r.frame_hash}.txt"
        )
        img = cv2.imread(str(src_img))
        h, w = img.shape[:2]

        # mapping class → id
        # (Tự định nghĩa cho project, ví dụ 0:dish_clean 1:dish_dirty 2:tray_full 3:tray_empty …)
        def class_id(name: str) -> int:
            mapping = {
                "dish:clean": 0,
                "dish:dirty": 1,
                "tray:full": 2,
                "tray:empty": 3,
            }
            return mapping.get(name.lower(), 0)

        lbl = r.pred_label if r.accepted else r.user_label
        if not lbl:
            continue

        write_yolo_row(dst_txt, class_id(lbl), r.bbox, w, h)

    # ===== 4) Tạo dataset.yaml (nếu chưa có) =====
    yaml_path = settings.YOLO_DATASET_DIR / "dataset.yaml"
    if not yaml_path.exists():
        yaml_path.write_text(
            f"""path: {settings.YOLO_DATASET_DIR}
                train: images/train
                val: images/train   # tạm thời, bạn có thể tách val sau
                test: images/train
                names:
                0: dish_clean
                1: dish_dirty
                2: tray_full
                3: tray_empty
                """
        )

    return True


def train_yolo():
    """
    Gọi Ultralytics CLI fine‑tune tiếp.
    """
    cmd = [
        "yolo",
        "detect",
        "train",
        f"data={settings.YOLO_DATASET_DIR / 'dataset.yaml'}",
        f"model={settings.DET_WEIGHT}",      # sử dụng weight hiện tại làm warm‑start
        f"epochs={settings.YOLO_EPOCHS}",
        f"imgsz={settings.YOLO_IMAGE_SIZE}",
        f"batch={settings.YOLO_BATCH}",
        f"device={settings.DEVICE}",
        "--name",
        f"auto_{datetime.date.today()}",
        "--resume",                          # nếu đã từng train, CLI sẽ nối tiếp
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

    # Tìm weight tốt nhất sinh ra
    run_dir = Path("runs/detect") / f"auto_{datetime.date.today()}"
    best_pt = run_dir / "weights" / "best.pt"
    if best_pt.exists():
        settings.CURRENT_WEIGHT_FILE.write_text(str(best_pt.resolve()))
        print(f"[INFO] New weight saved ➜ {best_pt}")
    else:
        print("[WARN] training finished but best.pt not found!")


def main():
    ensure_dirs()
    db = SessionLocal()
    try:
        rows = fetch_unexported(db)
        if not create_dataset(rows):
            return
        mark_exported(db, [r.id for r in rows])
    finally:
        db.close()

    # Train
    train_yolo()


if __name__ == "__main__":
    main()
