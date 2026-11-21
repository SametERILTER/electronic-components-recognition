import os
import glob
from ultralytics import YOLO

def test_real():
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

    model = YOLO(model_path)
    image_paths = glob.glob("real_images/*.*")

    if not image_paths:
        print("real_images/ klasorunde hic gorsel bulunamadi!")
        print("Lutfen telefonunuzla cektiginiz 5 fotografi 'real_images' klasorune koyun.")
        return

    print(f"{len(image_paths)} adet gercek gorsel test ediliyor...")
    os.makedirs("real_images_results", exist_ok=True)

    results = model.predict(
        source="real_images",
        conf=0.25,
        save=True,
        project="real_images_results",
        name="predictions",
        exist_ok=True
    )

    print("\n" + "=" * 60)
    print("GERCEK GORUNTULERLE TEST SONUCLARI:")
    print("=" * 60)
    for res in results:
        img_name = os.path.basename(res.path)
        cls_counts = {}
        for b in res.boxes:
            c = res.names[int(b.cls[0])]
            cls_counts[c] = cls_counts.get(c, 0) + 1
        print(f"Fotoğraf: {img_name} -> Tespitler: {cls_counts if cls_counts else 'Tespit yok'}")
    print("=" * 60)
    print("Isaretlenmis gorseller 'real_images_results/predictions' klasorune kaydedildi.")

if __name__ == "__main__":
    test_real()
