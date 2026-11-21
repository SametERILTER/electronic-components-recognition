import io
import os
import time
import base64
import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
import uvicorn
import torch

app = FastAPI(
    title="Elektronik Komponent Tespiti",
    version="1.0.0"
)

# Static samples folder
SAMPLES_DIR = os.path.abspath("sample_images")
if os.path.exists(SAMPLES_DIR):
    app.mount("/static/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

MODEL_PATHS = [
    "weights/best.pt",
    "runs/detect/runs/detect/electronic_components_yolov8/weights/best.pt",
    "runs/detect/electronic_components_yolov8/weights/best.pt"
]
_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        for p in MODEL_PATHS:
            if os.path.exists(p):
                try:
                    _model_instance = YOLO(p)
                    break
                except Exception as e:
                    print(f"Model yüklenirken hata: {e}")
    return _model_instance

DEVICE_NAME = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Derin Öğrenme Ödev2 - Elektronik Komponent Tespiti</title>
    <style>
        :root {
            --bg-page: #000000;
            --bg-card: #1c1c1e;
            --bg-subtle: #2c2c2e;
            --bg-hover: #3a3a3c;
            --text-main: #f5f5f7;
            --text-secondary: #86868b;
            --accent: #0071e3;
            --accent-hover: #0077ed;
            --divider: #2c2c2e;
            --border-radius-card: 16px;
            --border-radius-elem: 10px;
            --border-radius-pill: 980px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
            border: none;
            outline: none;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-page);
            color: var(--text-main);
            line-height: 1.47059;
            padding: 36px 20px;
        }

        .container {
            max-width: 1080px;
            margin: 0 auto;
        }

        /* Apple Header */
        header {
            padding-bottom: 24px;
            margin-bottom: 24px;
        }

        .title-group h1 {
            font-size: 24px;
            font-weight: 600;
            letter-spacing: -0.016em;
            color: var(--text-main);
        }

        /* 2 Sütunlu Izgara */
        .grid-layout {
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 20px;
            align-items: start;
        }

        @media (max-width: 860px) {
            .grid-layout {
                grid-template-columns: 1fr;
            }
        }

        /* Apple Koyu Kartlar */
        .card {
            background: var(--bg-card);
            border-radius: var(--border-radius-card);
            padding: 22px;
        }

        .card-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 14px;
            letter-spacing: -0.01em;
        }

        /* Yükleme Alanı */
        .dropzone {
            background: var(--bg-subtle);
            border-radius: var(--border-radius-elem);
            padding: 26px 16px;
            text-align: center;
            cursor: pointer;
            transition: background-color 0.15s;
        }

        .dropzone:hover {
            background-color: var(--bg-hover);
        }

        .dropzone input {
            display: none;
        }

        .dropzone-text {
            font-size: 14px;
            color: var(--text-main);
            font-weight: 500;
        }

        .dropzone-sub {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        .preview-box {
            display: none;
            position: relative;
            margin-top: 14px;
            border-radius: var(--border-radius-elem);
            overflow: hidden;
            background: #000000;
        }

        .preview-box img {
            width: 100%;
            max-height: 200px;
            object-fit: contain;
            display: block;
        }

        .btn-change {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: #ffffff;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: var(--border-radius-pill);
            cursor: pointer;
            backdrop-filter: blur(8px);
        }

        /* Hızlı Test Örnekleri */
        .samples-block {
            margin-top: 18px;
        }

        .samples-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }

        .samples-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .sample-item {
            background: var(--bg-subtle);
            color: var(--text-main);
            padding: 9px 12px;
            border-radius: var(--border-radius-elem);
            font-size: 12px;
            font-weight: 500;
            text-align: left;
            cursor: pointer;
            transition: background-color 0.15s;
        }

        .sample-item:hover {
            background: var(--bg-hover);
        }

        /* Parametre Ayarları */
        .param-group {
            margin-top: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .param-row {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .param-header {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: var(--text-secondary);
        }

        .param-val {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            color: var(--text-main);
            font-weight: 500;
        }

        input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 4px;
            background: var(--bg-hover);
            border-radius: 2px;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.5);
            cursor: pointer;
        }

        /* Apple Mavi Pill Buton */
        .btn-submit {
            margin-top: 20px;
            width: 100%;
            background: var(--accent);
            color: #ffffff;
            padding: 12px;
            font-size: 14px;
            font-weight: 500;
            border-radius: var(--border-radius-pill);
            cursor: pointer;
            transition: background-color 0.15s;
        }

        .btn-submit:hover:not(:disabled) {
            background: var(--accent-hover);
        }

        .btn-submit:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        /* Sağ Panel */
        .results-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        /* Metrikler */
        .metrics-bar {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }

        .metric-box {
            background: var(--bg-card);
            border-radius: var(--border-radius-card);
            padding: 16px 18px;
        }

        .metric-label {
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 400;
        }

        .metric-value {
            font-size: 22px;
            font-weight: 600;
            color: var(--text-main);
            margin-top: 2px;
            letter-spacing: -0.02em;
        }

        /* Görüntü Kutusu */
        .viewer-box {
            background: var(--bg-card);
            border-radius: var(--border-radius-card);
            overflow: hidden;
        }

        .viewer-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 18px;
            border-bottom: 1px solid var(--divider);
        }

        .tabs {
            display: flex;
            gap: 4px;
        }

        .tab-btn {
            background: transparent;
            color: var(--text-secondary);
            font-size: 13px;
            padding: 5px 12px;
            border-radius: var(--border-radius-pill);
            cursor: pointer;
            transition: all 0.15s;
        }

        .tab-btn.active {
            background: var(--bg-subtle);
            color: var(--text-main);
            font-weight: 500;
        }

        .btn-dl {
            background: var(--bg-subtle);
            color: var(--text-main);
            font-size: 12px;
            padding: 6px 14px;
            border-radius: var(--border-radius-pill);
            cursor: pointer;
            transition: background-color 0.15s;
        }

        .btn-dl:hover {
            background: var(--bg-hover);
        }

        .image-stage {
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #000000;
            padding: 14px;
        }

        .image-stage img {
            max-width: 100%;
            max-height: 500px;
            object-fit: contain;
            display: block;
            border-radius: 8px;
        }

        .placeholder-text {
            color: var(--text-secondary);
            font-size: 14px;
        }

        /* Komponent Tablosu */
        .table-card {
            background: var(--bg-card);
            border-radius: var(--border-radius-card);
            padding: 20px;
            display: none;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-top: 10px;
        }

        th, td {
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid var(--divider);
        }

        th {
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 12px;
        }

        td {
            color: var(--text-main);
        }

        .count-badge {
            background: var(--bg-subtle);
            color: var(--text-main);
            padding: 3px 10px;
            border-radius: var(--border-radius-pill);
            font-size: 12px;
            font-weight: 500;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Apple Header -->
        <header>
            <div class="title-group">
                <h1>Derin Öğrenme Ödev2 - Elektronik Komponent Tespiti</h1>
            </div>
        </header>

        <div class="grid-layout">
            <!-- Sol Panel -->
            <div class="card">
                <div class="card-title">Görsel Seçimi</div>

                <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" accept="image/*" onchange="onFileSelected(this.files[0])">
                    <div id="dropPrompt">
                        <div class="dropzone-text">Fotoğraf seçin</div>
                        <div class="dropzone-sub">veya buraya sürükleyin</div>
                    </div>
                    <div class="preview-box" id="previewBox">
                        <img id="previewImg" alt="Önizleme">
                        <button type="button" class="btn-change" onclick="clearImage(event)">Değiştir</button>
                    </div>
                </div>

                <!-- Örnekler -->
                <div class="samples-block">
                    <div class="samples-label">Örnekler:</div>
                    <div class="samples-grid">
                        <button type="button" class="sample-item" onclick="loadSample('sample_ic.jpg')">Entegre (IC)</button>
                        <button type="button" class="sample-item" onclick="loadSample('sample_resistor.jpg')">Direnç</button>
                        <button type="button" class="sample-item" onclick="loadSample('sample_capacitor.jpg')">Kondansatör</button>
                        <button type="button" class="sample-item" onclick="loadSample('sample_transistor.jpg')">Transistör</button>
                    </div>
                </div>

                <!-- Ayarlar -->
                <div class="param-group">
                    <div class="param-row">
                        <div class="param-header">
                            <span>Güven Eşiği</span>
                            <span class="param-val" id="confText">0.25</span>
                        </div>
                        <input type="range" id="confSlider" min="0.10" max="0.90" step="0.05" value="0.25" oninput="document.getElementById('confText').innerText=parseFloat(this.value).toFixed(2)">
                    </div>

                    <div class="param-row">
                        <div class="param-header">
                            <span>IoU Eşiği</span>
                            <span class="param-val" id="iouText">0.45</span>
                        </div>
                        <input type="range" id="iouSlider" min="0.10" max="0.90" step="0.05" value="0.45" oninput="document.getElementById('iouText').innerText=parseFloat(this.value).toFixed(2)">
                    </div>
                </div>

                <button class="btn-submit" id="btnSubmit" onclick="runInference()">Tespit Et</button>
            </div>

            <!-- Sağ Panel -->
            <div class="results-container">
                <!-- Metrikler -->
                <div class="metrics-bar">
                    <div class="metric-box">
                        <div class="metric-label">Tahmin Süresi</div>
                        <div class="metric-value" id="valLatency">--</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Toplam Adet</div>
                        <div class="metric-value" id="valCount">--</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Sınıf Çeşidi</div>
                        <div class="metric-value" id="valClasses">--</div>
                    </div>
                </div>

                <!-- Görüntü Kutusu -->
                <div class="viewer-box">
                    <div class="viewer-header">
                        <div class="tabs">
                            <button type="button" class="tab-btn active" id="tabAnn" onclick="switchTab('ann')">Tespit Sonucu</button>
                            <button type="button" class="tab-btn" id="tabOrig" onclick="switchTab('orig')">Orijinal</button>
                        </div>
                        <button type="button" class="btn-dl" id="btnDl" style="display:none;" onclick="downloadImage()">Görseli Kaydet</button>
                    </div>

                    <div class="image-stage">
                        <span class="placeholder-text" id="stagePlaceholder">Görsel bekleniyor</span>
                        <img id="mainResultImg" style="display:none;" alt="Sonuç Görseli">
                    </div>
                </div>

                <!-- Tespit Listesi Tablosu -->
                <div class="table-card" id="tableCard">
                    <div class="card-title" style="margin-bottom: 0;">Tespit Edilen Komponentler</div>
                    <table>
                        <thead>
                            <tr>
                                <th>Komponent</th>
                                <th>Adet</th>
                                <th>Ortalama Güven</th>
                            </tr>
                        </thead>
                        <tbody id="tableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentFile = null;
        let originalB64 = null;
        let annotatedB64 = null;

        function onFileSelected(file) {
            if (!file) return;
            currentFile = file;
            const r = new FileReader();
            r.onload = e => {
                originalB64 = e.target.result;
                document.getElementById('previewImg').src = originalB64;
                document.getElementById('previewBox').style.display = 'block';
                document.getElementById('dropPrompt').style.display = 'none';
            };
            r.readAsDataURL(file);
        }

        function clearImage(e) {
            if (e) e.stopPropagation();
            currentFile = null;
            originalB64 = null;
            annotatedB64 = null;
            document.getElementById('fileInput').value = '';
            document.getElementById('previewBox').style.display = 'none';
            document.getElementById('dropPrompt').style.display = 'block';
            document.getElementById('mainResultImg').style.display = 'none';
            document.getElementById('stagePlaceholder').style.display = 'block';
            document.getElementById('btnDl').style.display = 'none';
            document.getElementById('tableCard').style.display = 'none';
            document.getElementById('valLatency').innerText = '--';
            document.getElementById('valCount').innerText = '--';
            document.getElementById('valClasses').innerText = '--';
        }

        async function loadSample(name) {
            try {
                const res = await fetch('/static/samples/' + name);
                const blob = await res.blob();
                const f = new File([blob], name, { type: "image/jpeg" });
                onFileSelected(f);
            } catch (err) {
                alert('Örnek dosya yüklenemedi: ' + err.message);
            }
        }

        async function runInference() {
            if (!currentFile) {
                alert('Lütfen önce bir görsel seçin.');
                return;
            }

            const btn = document.getElementById('btnSubmit');
            btn.disabled = true;
            btn.innerText = 'İşleniyor...';

            const formData = new FormData();
            formData.append('file', currentFile);
            formData.append('conf', document.getElementById('confSlider').value);
            formData.append('iou', document.getElementById('iouSlider').value);

            try {
                const res = await fetch('/predict', { method: 'POST', body: formData });
                const data = await res.json();

                btn.disabled = false;
                btn.innerText = 'Tespit Et';

                if (data.error) {
                    alert('Hata: ' + data.error);
                    return;
                }

                annotatedB64 = 'data:image/jpeg;base64,' + data.image_base64;

                // Değerler
                document.getElementById('valLatency').innerText = data.inference_ms.toFixed(1) + ' ms';
                document.getElementById('valCount').innerText = data.total_detections;
                document.getElementById('valClasses').innerText = Object.keys(data.class_counts).length;

                // Görsel alanı
                document.getElementById('stagePlaceholder').style.display = 'none';
                document.getElementById('mainResultImg').style.display = 'block';
                document.getElementById('btnDl').style.display = 'block';
                switchTab('ann');

                // Tablo
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = '';
                const classes = Object.keys(data.class_stats);

                if (classes.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3" style="color:var(--text-secondary);">Komponent bulunamadı.</td></tr>';
                } else {
                    classes.forEach(c => {
                        const s = data.class_stats[c];
                        tbody.innerHTML += `
                            <tr>
                                <td><strong>${c}</strong></td>
                                <td><span class="count-badge">${s.count}</span></td>
                                <td>%${(s.avg_conf * 100).toFixed(1)}</td>
                            </tr>
                        `;
                    });
                }
                document.getElementById('tableCard').style.display = 'block';

            } catch (err) {
                btn.disabled = false;
                btn.innerText = 'Tespit Et';
                alert('İstek sırasında hata oluştu: ' + err.message);
            }
        }

        function switchTab(t) {
            const img = document.getElementById('mainResultImg');
            const tabAnn = document.getElementById('tabAnn');
            const tabOrig = document.getElementById('tabOrig');

            if (t === 'ann') {
                tabAnn.classList.add('active');
                tabOrig.classList.remove('active');
                img.src = annotatedB64;
            } else {
                tabOrig.classList.add('active');
                tabAnn.classList.remove('active');
                img.src = originalB64;
            }
        }

        function downloadImage() {
            if (!annotatedB64) return;
            const a = document.createElement('a');
            a.download = 'tespit_sonucu.jpg';
            a.href = annotatedB64;
            a.click();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    conf: float = 0.25,
    iou: float = 0.45
):
    m = get_model()
    if m is None:
        return JSONResponse({
            "error": "Model henüz eğitilmedi veya ağırlık dosyası bulunamadı. Lütfen önce 'train.py' scriptini çalıştırarak modeli eğitin."
        }, status_code=400)

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        np_img = np.array(image)

        start_time = time.time()
        results = m.predict(source=np_img, conf=conf, iou=iou, device=0 if torch.cuda.is_available() else "cpu")
        inference_ms = (time.time() - start_time) * 1000

        res = results[0]
        annotated_bgr = res.plot(line_width=2, font_size=1)
        annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

        # Base64 export
        pil_res = Image.fromarray(annotated_rgb)
        buf = io.BytesIO()
        pil_res.save(buf, format="JPEG", quality=90)
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # İstatistikler
        class_counts = {}
        class_conf_sums = {}

        for box in res.boxes:
            c_id = int(box.cls[0])
            c_name = res.names[c_id]
            c_conf = float(box.conf[0])

            class_counts[c_name] = class_counts.get(c_name, 0) + 1
            class_conf_sums[c_name] = class_conf_sums.get(c_name, 0.0) + c_conf

        class_stats = {}
        for c_name, count in class_counts.items():
            class_stats[c_name] = {
                "count": count,
                "avg_conf": class_conf_sums[c_name] / count
            }

        return {
            "inference_ms": inference_ms,
            "total_detections": len(res.boxes),
            "class_counts": class_counts,
            "class_stats": class_stats,
            "image_base64": img_b64
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
