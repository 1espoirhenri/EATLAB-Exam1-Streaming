// ===============================
// app.js – Live ⇄ Capture (phiên bản tối giản – không bảng)
// ===============================

const API = window.location.origin + "/api";
let canvas, drawMode = false, startX, startY, tempRect, capturedImg = null;

window.addEventListener("DOMContentLoaded", () => {
  // Khởi tạo Fabric
  canvas = new fabric.Canvas("canvas", { selection: false });
  canvas.upperCanvasEl.style.position = "absolute";
  canvas.backgroundColor = "#fff";

  addHud();
  bindButtons();
  bindCanvasEvents();

  // Ẩn canvas khi đang live
  document.getElementById("canvas").style.display = "none";
});

// ===== HUD & Crosshair =====
const crossV = new fabric.Line([0, 0, 0, 0], { stroke: "#0ff", selectable: false });
const crossH = new fabric.Line([0, 0, 0, 0], { stroke: "#0ff", selectable: false });
const HUD = new fabric.Text("", {
  left: 10,
  top: 10,
  fontSize: 14,
  fill: "#fff",
  backgroundColor: "rgba(0,0,0,.5)",
  selectable: false,
});
function addHud() {
  canvas.add(crossV, crossH, HUD);
  canvas.bringToFront(crossV);
  canvas.bringToFront(crossH);
  canvas.bringToFront(HUD);
}

// ===== Capture Frame =====
function captureFrame() {
  const img = new Image();
  img.onload = () => {
    // Chuyển UI
    document.getElementById("live").style.display = "none";
    document.getElementById("canvas").style.display = "block";

    canvas.clear();
    canvas.setWidth(img.width);
    canvas.setHeight(img.height);

    const bg = new fabric.Image(img, { selectable: false, evented: false });
    canvas.add(bg);
    canvas.sendToBack(bg);

    capturedImg = img;
    addHud();
  };
  img.src = `/api/current_frame?ts=${Date.now()}`;
}

// ===== Khôi phục live video =====
function backToLive() {
  capturedImg = null;
  drawMode = false;
  tempRect = null;

  document.getElementById("canvas").style.display = "none";
  const liveImg = document.getElementById("live");
  liveImg.style.display = "block";
  liveImg.src = `/video_feed?ts=${Date.now()}`;

  const btnDraw = document.getElementById("btnDraw");
  btnDraw.innerText = "Vẽ BBox";
  canvas.defaultCursor = "default";

  canvas.clear();
  addHud();
}

// ===== Gửi feedback =====
async function sendFeedback() {
  if (!capturedImg) {
    alert("Chưa chụp frame!");
    return;
  }

  const cTmp = document.createElement("canvas");
  cTmp.width = capturedImg.width;
  cTmp.height = capturedImg.height;
  cTmp.getContext("2d").drawImage(capturedImg, 0, 0);
  const blob = await new Promise((r) => cTmp.toBlob(r, "image/jpeg"));

  const rects = canvas.getObjects("rect").map((r) => ({
    bbox: [
      Math.min(r.left, r.left + r.width),
      Math.min(r.top, r.top + r.height),
      Math.max(r.left, r.left + r.width),
      Math.max(r.top, r.top + r.height),
    ].map(Math.round),
    label: r.get("label") || "unknown",
  }));

  if (rects.length === 0) {
    alert("Chưa có bbox!");
    return;
  }

  const fd = new FormData();
  fd.append("file", blob, "frame.jpg");
  fd.append("bboxes", JSON.stringify(rects));
  const res = await fetch(`${API}/feedback`, { method: "POST", body: fd });
  if (res.ok) {
    alert("Feedback saved!  Cảm ơn bạn.");
    backToLive();
  } else {
    alert(`Error: ${await res.text()}`);
  }
}

// ===== Bind Buttons =====
function bindButtons() {
  document.getElementById("btnCapture").onclick = captureFrame;
  const btnDraw = document.getElementById("btnDraw");
  btnDraw.onclick = () => {
    drawMode = !drawMode;
    canvas.defaultCursor = drawMode ? "crosshair" : "default";
    btnDraw.innerText = drawMode ? "Đang vẽ (bấm để dừng)" : "Vẽ BBox";
  };
  document.getElementById("btnSave").onclick = sendFeedback;
  document.getElementById("btnBack").onclick = backToLive;
}

// ===== Canvas events =====
function bindCanvasEvents() {
  canvas.on("mouse:move", (e) => {
    const p = canvas.getPointer(e.e);
    crossV.set({ x1: p.x, y1: 0, x2: p.x, y2: canvas.height });
    crossH.set({ x1: 0, y1: p.y, x2: canvas.width, y2: p.y });

    if (drawMode && tempRect) {
      tempRect.set({ width: p.x - startX, height: p.y - startY });
      HUD.set({ text: `${Math.abs(tempRect.width) | 0}×${Math.abs(tempRect.height) | 0}` });
    } else {
      HUD.set({ text: `(${p.x | 0},${p.y | 0})` });
    }
    canvas.renderAll();
  });

  canvas.on("mouse:down", (e) => {
    if (!drawMode) return;
    const p = canvas.getPointer(e.e);
    startX = p.x;
    startY = p.y;
    tempRect = new fabric.Rect({
      left: startX,
      top: startY,
      width: 1,
      height: 1,
      stroke: "#ff0",
      strokeWidth: 2,
      strokeDashArray: [6, 4],
      fill: "rgba(255,255,0,.15)",
      selectable: false,
    });
    canvas.add(tempRect);
    canvas.bringToFront(tempRect);
  });

  canvas.on("mouse:up", () => {
    if (!drawMode || !tempRect) return;
    tempRect.set({ stroke: "red", strokeDashArray: null, fill: "rgba(0,0,0,0)", selectable: true });
    tempRect.set("label", prompt("Nhãn cho bbox:", "dish:empty") || "unknown");
    tempRect = null;
    HUD.set({ text: "" });
  });
}
