const API = window.location.origin + "/api";
const canvas = new fabric.Canvas('canvas', { selection: false });
canvas.backgroundColor = '#fff';

let drawMode = false;
let startX, startY, tempRect;
const crossV = new fabric.Line([0,0,0,0], {stroke:'#0ff', selectable:false});
const crossH = new fabric.Line([0,0,0,0], {stroke:'#0ff', selectable:false});
const HUD    = new fabric.Text('', {
  left:10, top:10, fontSize:14,
  fill:'#fff', backgroundColor:'rgba(0,0,0,.5)',
  selectable:false
});
canvas.add(crossV, crossH, HUD);
canvas.bringToFront(crossV); canvas.bringToFront(crossH); canvas.bringToFront(HUD);

let capturedImg = null;

document.getElementById('btnCapture').addEventListener('click', () => {
  const imgEl = document.getElementById('live');

  // Tạo <img> để vẽ lại
  const img = new Image();
  img.crossOrigin = 'Anonymous';
  img.onload = () => {
    canvas.setWidth(img.width);
    canvas.setHeight(img.height);
    canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas), {
      originX: 'left',
      originY: 'top'
    });

    capturedImg = img;
    alert("Đã chụp frame từ video feed. Giờ bạn có thể vẽ bbox hoặc chỉnh lại.");
  };
  img.src = "/api/current_frame?ts=" + Date.now();

  // Xóa bbox cũ
  canvas.getObjects('rect').forEach(o => canvas.remove(o));
});

document.getElementById('btnDraw').addEventListener('click', () => {
  drawMode = !drawMode;
  canvas.defaultCursor = drawMode ? 'crosshair' : 'default';
  document.getElementById('btnDraw').innerText = drawMode ? 'Đang vẽ (bấm để dừng)' : 'Vẽ BBox';
});

canvas.on('mouse:move', (e) => {
  const p = canvas.getPointer(e.e);
  crossV.set({ x1:p.x, y1:0, x2:p.x, y2:canvas.height });
  crossH.set({ x1:0, y1:p.y, x2:canvas.width, y2:p.y });

  if (drawMode && tempRect) {
    tempRect.set({ width: p.x-startX, height: p.y-startY });
    HUD.set({ text: `${Math.abs(tempRect.width).toFixed(0)}×${Math.abs(tempRect.height).toFixed(0)}` });
  } else {
    HUD.set({ text: `(${p.x.toFixed(0)},${p.y.toFixed(0)})` });
  }
  canvas.renderAll();
});

canvas.on('mouse:down', (e) => {
  if (!drawMode) return;
  const p = canvas.getPointer(e.e);
  startX = p.x; startY = p.y;
  tempRect = new fabric.Rect({
    left: startX, top: startY, width: 1, height: 1,
    stroke: '#ff0', strokeWidth: 2, strokeDashArray: [6, 4],
    fill: 'rgba(255,255,0,.15)', selectable: false
  });
  canvas.add(tempRect);
  canvas.bringToFront(tempRect);
});

canvas.on('mouse:up', () => {
  if (!drawMode || !tempRect) return;
  tempRect.set({
    stroke: 'red', strokeDashArray: null,
    fill: 'rgba(0,0,0,0)', selectable: true
  });
  const label = prompt('Nhãn cho bbox:', 'dish:empty') || 'unknown';
  tempRect.set('label', label);
  tempRect.set('pred', '');
  tempRect = null; HUD.set({ text: '' });
});

// Save feedback
document.getElementById('btnSave').addEventListener('click', async () => {
  if (!capturedImg) {
    alert('Chưa chụp frame!');
    return;
  }

  // Lưu ảnh chụp
  const temp = document.createElement('canvas');
  temp.width = capturedImg.width;
  temp.height = capturedImg.height;
  temp.getContext('2d').drawImage(capturedImg, 0, 0);
  const blob = await new Promise(resolve => temp.toBlob(resolve, 'image/jpeg'));

  const fd = new FormData();
  fd.append('file', blob, 'frame.jpg');

  // Lưu bbox kèm ảnh
  const rects = canvas.getObjects('rect').map(r => ({
    bbox: [
      Math.min(r.left, r.left + r.width),
      Math.min(r.top, r.top + r.height),
      Math.max(r.left, r.left + r.width),
      Math.max(r.top, r.top + r.height)
    ].map(x => Math.round(x)),
    label: r.get('label')
  }));

  fd.append('bboxes', JSON.stringify(rects));

  const res = await fetch(`${API}/feedback`, { method: 'POST', body: fd });
  if (res.ok) {
    alert('Đã lưu feedback!');
  } else {
    alert('Lỗi: ' + await res.text());
  }
});
