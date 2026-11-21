import os
import time
from ultralytics import YOLO

def evaluate():
    paths = [
        "runs/detect/runs/detect/electronic_components_yolov8/weights/best.pt",
        "runs/detect/electronic_components_yolov8/weights/best.pt"
    ]
    model_path = None
    for p in paths:
        if os.path.exists(p):
            model_path = p
            break

    if not model_path:
        print("HATA: Model agirlik dosyasi (best.pt) bulunamadi.")
        return

    data_path = os.path.abspath("ElectronicComponentsDataset/data.yaml")
    model = YOLO(model_path)

    print("=" * 60)
    print("TEST KUMESI UZERINDE PERFORMANS DEGERLENDIRMESI...")
    print(f"Model: {model_path}")
    print("=" * 60)

    # Test kumesi uzerinde dogrulama
    metrics = model.val(
        data=data_path,
        split="test",
        imgsz=640,
        batch=16,
        device=0
    )

    print("\n" + "=" * 60)
    print("ODEVI RAPORU ICIN PERFORMANS METRIKLERI:")
    print("=" * 60)
    print(f"mAP@50       : {metrics.box.map50:.4f}")
    print(f"mAP@50-95    : {metrics.box.map:.4f}")
    print(f"Precision (P): {metrics.box.mp:.4f}")
    print(f"Recall (R)   : {metrics.box.mr:.4f}")
    
    # Ortalama cikarim (inference) suresi
    # speed sozlugu preprocess, inference, loss, postprocess icerir
    inference_ms = metrics.speed.get("inference", 0.0)
    print(f"Inference Time: {inference_ms:.2f} ms / goruntu")
    print("=" * 60)
    print("Sinif Bazli mAP50 Degerleri:")
    for i, c_name in enumerate(metrics.names.values()):
        ap50 = metrics.box.ap50[i] if i < len(metrics.box.ap50) else 0.0
        print(f"  - {c_name:12s}: {ap50:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    evaluate()
