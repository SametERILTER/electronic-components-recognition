import os
import time
import cv2
import gradio as gr
from ultralytics import YOLO

MODEL_PATH = "runs/detect/electronic_components_yolov8/weights/best.pt"

# Egitilmis model varsa onu yukle, yoksa uyar
if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
else:
    print(f"Uyari: {MODEL_PATH} henuz olusmadi. Egitim sonrasi uygulama aktif olacaktir.")
    model = None

def detect_components(image, conf_threshold, iou_threshold):
    if model is None:
        return image, "Model henuz egitilmedi! Lutfen once train.py calistirin."
    
    if image is None:
        return None, "Lutfen bir gorsel yukleyin."

    start_time = time.time()
    results = model.predict(source=image, conf=conf_threshold, iou=iou_threshold)
    elapsed_ms = (time.time() - start_time) * 1000

    # Sonuclari gorsel uzerine ciz
    res = results[0]
    annotated_img = res.plot() # BGR format
    annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)

    # Tespit edilen komponentlerin istatistigi
    detected_classes = {}
    boxes = res.boxes
    for box in boxes:
        cls_id = int(box.cls[0])
        cls_name = res.names[cls_id]
        conf = float(box.conf[0])
        detected_classes[cls_name] = detected_classes.get(cls_name, 0) + 1

    summary_text = f"### Tahmin Suresi: {elapsed_ms:.1f} ms\n\n"
    if detected_classes:
        summary_text += "**Tespit Edilen Komponentler:**\n"
        for name, count in detected_classes.items():
            summary_text += f"- **{name}**: {count} adet\n"
    else:
        summary_text += "Belirtilen guven esiginde hicbir komponent tespit edilemedi."

    return annotated_rgb, summary_text

# Gradio Arayuzu
demo = gr.Interface(
    fn=detect_components,
    inputs=[
        gr.Image(type="numpy", label="Görsel Yükle (Devre Kartı veya Komponent)"),
        gr.Slider(minimum=0.1, maximum=1.0, value=0.25, step=0.05, label="Güven Eşiği (Confidence Threshold)"),
        gr.Slider(minimum=0.1, maximum=1.0, value=0.45, step=0.05, label="IoU Eşiği (NMS Threshold)")
    ],
    outputs=[
        gr.Image(type="numpy", label="Tespit Sonucu"),
        gr.Markdown(label="Tespit Özeti & Performans")
    ],
    title="Elektronik Komponent Tespiti (Electronic Components Recognition)",
    description="YOLOv8 derin ogrenme modeli ile elektronik devre kartlarindaki komponentleri (Resistor, Capacitor, IC, Led, Transistor vb.) tespit edin.",
    examples=[]
)

if __name__ == "__main__":
    demo.launch(share=False)
