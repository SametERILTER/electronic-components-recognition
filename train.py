import os
import time
from ultralytics import YOLO

def train():
    # 1. Model secimi (YOLOv8 Nano - Hizli, yuksek performansli ve 6GB VRAM icin ideal)
    model = YOLO("yolov8n.pt")

    data_path = os.path.abspath("ElectronicComponentsDataset/data.yaml")
    
    print("=" * 60)
    print("MODEL EGITIMI BASLIYOR...")
    print(f"Veri Seti: {data_path}")
    print("Mimari: YOLOv8 Nano (yolov8n.pt)")
    print("Donanim: GPU (NVIDIA RTX 4050)")
    print("=" * 60)

    start_time = time.time()

    # 2. Egitim hiperparametreleri (Odev raporu icin not edilecek degerler)
    results = model.train(
        data=data_path,
        epochs=25,              # 25 epoch genelde bu boyuttaki veri seti icin yuksek basarim saglar
        imgsz=640,              # Standart girdi cozunurlugu
        batch=16,               # 6GB VRAM icin dengeli batch boyutu
        device=0,               # NVIDIA GPU (0 numarali aygit)
        workers=4,              # Veri yukleme islemci thread sayisi
        optimizer="AdamW",      # Odev raporunda aciklanacak optimizer
        lr0=0.001,              # Baslangic ogrenme orani (Initial Learning Rate)
        lrf=0.01,               # Nihai ogrenme orani carpani
        patience=10,            # Early stopping (asiri ogrenmeyi engellemek icin 10 epoch iyilesme olmazsa durdur)
        save=True,
        project="runs/detect",
        name="electronic_components_yolov8",
        exist_ok=True
    )

    elapsed_time = time.time() - start_time
    print("=" * 60)
    print(f"EGITIM TAMAMLANDI! Toplam Egitim Suresi: {elapsed_time / 60:.2f} dakika ({elapsed_time:.1f} saniye)")
    print(f"En iyi model agirliklari: runs/detect/electronic_components_yolov8/weights/best.pt")
    print("=" * 60)

if __name__ == "__main__":
    train()
