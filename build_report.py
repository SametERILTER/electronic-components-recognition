import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx2pdf import convert

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def format_run(run, font_name="Arial", size_pt=10, bold=False, color_rgb=(0, 0, 0)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def remove_table_borders(table):
    for row in table.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>\n'
                f'  <w:top w:val="none"/>\n'
                f'  <w:left w:val="none"/>\n'
                f'  <w:bottom w:val="none"/>\n'
                f'  <w:right w:val="none"/>\n'
                f'</w:tcBorders>'
            )
            tcPr.append(tcBorders)

def add_clean_heading(doc, text, level=1, space_before=16, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    size = 12.5 if level == 1 else 11
    format_run(run, font_name="Arial", size_pt=size, bold=True, color_rgb=(0, 0, 0))
    return p

def add_clean_paragraph(doc, text, keep_with_next=False, space_before=2, space_after=4, line_spacing=1.15):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if keep_with_next:
        p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    format_run(run, font_name="Arial", size_pt=9.5, bold=False, color_rgb=(20, 20, 20))
    return p

def create_report():
    doc = docx.Document()

    # Sayfa kenar bosluklari
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # ==================== SAYFA 1 ====================
    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(0)
    p_course.paragraph_format.space_after = Pt(3)
    run_course = p_course.add_run("BİL485 DERİN ÖĞRENME")
    format_run(run_course, font_name="Arial", size_pt=13, bold=True, color_rgb=(0, 0, 0))

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("Computer Vision Ödevi Raporu")
    format_run(run_title, font_name="Arial", size_pt=16, bold=True, color_rgb=(0, 0, 0))

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(2)
    p_sub.paragraph_format.space_after = Pt(3)
    run_sub = p_sub.add_run("YOLOv8 ile Elektronik Komponent Tespiti ve FastAPI Uygulaması")
    format_run(run_sub, font_name="Arial", size_pt=10, bold=False, color_rgb=(70, 70, 70))

    p_student1 = doc.add_paragraph()
    p_student1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_student1.paragraph_format.space_before = Pt(6)
    p_student1.paragraph_format.space_after = Pt(1)
    run_s1 = p_student1.add_run("Samet Erilter")
    format_run(run_s1, font_name="Arial", size_pt=10.5, bold=True, color_rgb=(20, 20, 20))

    p_student2 = doc.add_paragraph()
    p_student2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_student2.paragraph_format.space_before = Pt(0)
    p_student2.paragraph_format.space_after = Pt(14)
    run_s2 = p_student2.add_run("24120205002")
    format_run(run_s2, font_name="Arial", size_pt=10.5, bold=True, color_rgb=(40, 40, 40))

    # 1. Bolum
    add_clean_heading(doc, "1. Ödevin Amacı", space_before=18, space_after=8)
    add_clean_paragraph(
        doc,
        "Bu ödevde amaç, açık kaynaklı bir veri seti kullanarak bilgisayarlı görü alanında derin öğrenme modeli "
        "eğitmek, modelin performansını test etmek ve eğitilen modeli bir web arayüzü (FastAPI) üzerinden "
        "çalışan bir uygulama hâline getirmektir. Projede elektronik devre kartlarındaki komponentlerin "
        "(direnç, kondansatör, entegre, transistör vb.) tespiti yapılmıştır.",
        space_before=2, space_after=18, line_spacing=1.2
    )

    # 2. Bolum
    add_clean_heading(doc, "2. Görev (Task)", space_before=26, space_after=8)
    add_clean_paragraph(
        doc,
        "Seçilen görev: Nesne Tespiti (Object Detection).\n"
        "Model, kendisine verilen devre fotoğrafı üzerindeki bileşenleri sınırlayıcı kutular (bounding box) "
        "içine almakta ve hangi sınıfa ait olduğunu (Button, Capacitor, IC, Led, Pot, Resistor, Sensor, Transistor) "
        "tespit etmektedir.",
        space_before=2, space_after=18, line_spacing=1.2
    )

    # 3. Bolum
    add_clean_heading(doc, "3. Model (Architecture)", space_before=26, space_after=8)
    add_clean_paragraph(
        doc,
        "Nesne tespiti için YOLOv8 Nano (yolov8n) modeli seçilmiştir. Model anchor-free (çapasız) yapıya sahiptir, "
        "böylece farklı boyutlardaki komponentleri daha rahat öğrenir. Omurgasında C2f blokları kullanılır. "
        "3.13 milyon parametresiyle hafif, hızlı ve yüksek doğruluk veren bir mimaridir.",
        space_before=2, space_after=18, line_spacing=1.2
    )

    # 4. Bolum
    add_clean_heading(doc, "4. Veri Seti (Dataset)", space_before=26, space_after=8)
    add_clean_paragraph(
        doc,
        "Roboflow üzerinden açık kaynaklı 'Electronic Components Recognition' veri seti indirilmiştir.\n"
        "URL: https://universe.roboflow.com/samu-drioq/electronic-components-d6uul/dataset/2\n"
        "• Eğitim (Train): 8.594 görüntü  |  Doğrulama (Valid): 832 görüntü  |  Test: 417 görüntü (Toplam: 9.843 adet)\n"
        "• 8 Sınıf: Button, Capacitor, IC, Led, Pot, Resistor, Sensor, Transistor",
        space_before=2, space_after=18, line_spacing=1.2
    )

    # 5. Bolum
    add_clean_heading(doc, "5. Model Ayarları ve Eğitim", space_before=26, space_after=8)
    add_clean_paragraph(
        doc,
        "Eğitim parametreleri:\n"
        "• Epoch: 25 (Modelin yeterli öğrenmesi ve aşırı ezberlememesi için seçildi)\n"
        "• Batch Size: 16 (GPU belleğine uygun olması için)\n"
        "• Girdi Boyutu: 640x640 piksel\n"
        "• Optimizer: AdamW (Ağırlık sönümleme desteğiyle daha iyi genelleme yaptığı için tercih edildi)\n"
        "• Öğrenme Oranı (Learning Rate): Başlangıç 0.001 olarak ayarlandı, Cosine çizelgesi ile düşürüldü.\n"
        "• Aktivasyon Fonksiyonu: SiLU (Gizli katmanlarda yumuşak gradyan akışı sağladığı için)\n"
        "• Loss Fonksiyonu: Kutu tahmini için CIoU ve DFL kaybı, sınıflandırma için BCE (Binary Cross-Entropy) kullanıldı.",
        space_before=2, space_after=6, line_spacing=1.2
    )

    # ==================== SAYFA 2 ====================
    doc.add_page_break()

    # 6. Bolum
    add_clean_heading(doc, "6. Performans Değerlendirmesi")
    add_clean_paragraph(
        doc,
        "Model 417 adet bağımsız test görüntüsü üzerinde test edilmiştir:\n"
        "• mAP@50: %91.48 (0.9148)\n"
        "• mAP@50-95: %78.21 (0.7821)\n"
        "• Precision (Kesinlik): %86.37\n"
        "• Recall (Duyarlılık): %87.99\n"
        "• Tahmin Süresi (Inference Time): 3.90 ms / görsel\n"
        "• Toplam Eğitim Süresi: ~36.3 dakika (25 Epoch)\n\n"
        "Sınıf bazlı mAP50 değerleri:\n"
        "Sensor: %99.5 | Transistor: %97.5 | Pot: %96.8 | Resistor: %96.7\n"
        "IC: %92.7 | Button: %90.7 | Capacitor: %80.1 | Led: %77.7",
        keep_with_next=True
    )

    base_dir = "runs/detect/runs/detect/electronic_components_yolov8"
    if os.path.exists(os.path.join(base_dir, "results.png")):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.keep_with_next = True
        p_img.add_run().add_picture(os.path.join(base_dir, "results.png"), width=Inches(6.3))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(6)
        run_cap = p_cap.add_run("Şekil 1: Eğitim Kayıp (Loss) ve mAP Grafikleri")
        format_run(run_cap, font_name="Arial", size_pt=9.5, bold=True, color_rgb=(40, 40, 40))

    # ==================== SAYFA 3 ====================
    # Sekil 2 ve Sekil 3 Buyutulmus Olarak Alt Alta
    doc.add_page_break()

    img_conf = os.path.join(base_dir, "confusion_matrix.png")
    img_pr = os.path.join(base_dir, "BoxPR_curve.png")

    if os.path.exists(img_conf):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(4)
        p_img2.paragraph_format.space_after = Pt(4)
        p_img2.paragraph_format.keep_with_next = True
        p_img2.add_run().add_picture(img_conf, width=Inches(4.2))

        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_before = Pt(2)
        p_cap2.paragraph_format.space_after = Pt(36)  # Daha genis, ferah bosluk
        p_cap2.paragraph_format.keep_with_next = True
        run_cap2 = p_cap2.add_run("Şekil 2: Hata Matrisi (Confusion Matrix)")
        format_run(run_cap2, font_name="Arial", size_pt=9.5, bold=True, color_rgb=(40, 40, 40))

    if os.path.exists(img_pr):
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.paragraph_format.space_before = Pt(8)
        p_img3.paragraph_format.space_after = Pt(4)
        p_img3.paragraph_format.keep_with_next = True
        p_img3.add_run().add_picture(img_pr, width=Inches(4.2))

        p_cap3 = doc.add_paragraph()
        p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap3.paragraph_format.space_before = Pt(0)
        p_cap3.paragraph_format.space_after = Pt(6)
        run_cap3 = p_cap3.add_run("Şekil 3: Precision - Recall (PR) Eğrileri")
        format_run(run_cap3, font_name="Arial", size_pt=9.5, bold=True, color_rgb=(40, 40, 40))

    # ==================== SAYFA 4 ====================
    doc.add_page_break()

    # 7. Bolum
    add_clean_heading(doc, "7. Uygulama", space_before=16, space_after=8)
    add_clean_paragraph(
        doc,
        "Eğitilen model, kullanıcıların tarayıcı üzerinden kolayca devre fotoğrafları yükleyip "
        "modelin tahminlerini görebilmesi için FastAPI kullanılarak çalışan bir web uygulaması hâline getirilmiştir.\n"
        "Uygulamanın özellikleri:\n"
        "• Kullanıcı bilgisayarından herhangi bir devre görseli yükleyebilir veya sürükleyip bırakabilir.\n"
        "• Fotoğraf yüklenmediğinde hemen denenebilmesi için hazır örnek test butonları eklenmiştir.\n"
        "• Model görseli işler, komponentlerin etrafına renkli kutucuklar çizer ve etiketlerini basar.\n"
        "• Ekranda milisaniye cinsinden tahmin süresi, kaç adet komponent bulunduğu ve hangi sınıftan kaç tane tespit edildiği liste olarak gösterilir.\n"
        "• Kullanıcı arayüz üzerinden güven eşiğini (Confidence) kaydırıcı ile kendisi değiştirebilir.",
        space_before=2, space_after=12, line_spacing=1.2
    )

    # ==================== SAYFA 5 ====================
    # 8. Bolum - Gercek Test Fotograflari Galerisi
    doc.add_page_break()
    add_clean_heading(doc, "8. Gerçek Görüntülerle Test ve Değerlendirme", space_before=14, space_after=6)
    add_clean_paragraph(
        doc,
        "Modelin gerçek ortamda nasıl çalıştığını test etmek amacıyla, Arduino başlangıç setindeki parçalar "
        "telefon kamerasıyla oda ışığında ve masa üzerinde fotoğraflanarak modele verilmiştir. "
        "Elde edilen tespit sonuçları Şekil 4 - Şekil 8 arasında gösterilmiştir.",
        space_before=2, space_after=8, line_spacing=1.15
    )

    real_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_results_annotated")
    
    # 2x2 Izgara Tablosu (Sensor, Led, Buton, Direnc)
    grid_items = [
        ("sensor_pred.jpg", "Şekil 4: Ultrasonik Sensör Tespiti (%95 Sensor)"),
        ("ledler_pred.jpg", "Şekil 5: LED Bileşenleri Tespiti (%71 Led)"),
        ("butonlar_pred.jpg", "Şekil 6: Buton Bileşenleri Tespiti (%64 Button)"),
        ("direncler_pred.jpg", "Şekil 7: Direnç Bileşenleri Tespiti (%10 Resistor)"),
    ]

    t_grid = doc.add_table(rows=2, cols=2)
    t_grid.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_grid.autofit = False
    remove_table_borders(t_grid)

    for idx, (img_name, cap_text) in enumerate(grid_items):
        r = idx // 2
        c = idx % 2
        cell = t_grid.rows[r].cells[c]
        cell.width = Inches(3.2)
        img_p = os.path.join(real_dir, img_name)
        if os.path.exists(img_p):
            p_i = cell.paragraphs[0]
            p_i.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_i.paragraph_format.space_before = Pt(1)
            p_i.paragraph_format.space_after = Pt(1)
            p_i.paragraph_format.keep_with_next = True
            p_i.add_run().add_picture(img_p, width=Inches(2.55))

            p_c = cell.add_paragraph()
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_c.paragraph_format.space_before = Pt(0)
            p_c.paragraph_format.space_after = Pt(2)
            run_c = p_c.add_run(cap_text)
            format_run(run_c, font_name="Arial", size_pt=8.5, bold=True, color_rgb=(40, 40, 40))

    # Tekli Merkezli Sekil 8: Arduino Uno Karti
    arduino_p = os.path.join(real_dir, "arduino_pred.jpg")
    if os.path.exists(arduino_p):
        p_ard = doc.add_paragraph()
        p_ard.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ard.paragraph_format.space_before = Pt(4)
        p_ard.paragraph_format.space_after = Pt(1)
        p_ard.paragraph_format.keep_with_next = True
        p_ard.add_run().add_picture(arduino_p, width=Inches(2.7))

        p_ard_c = doc.add_paragraph()
        p_ard_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ard_c.paragraph_format.space_before = Pt(0)
        p_ard_c.paragraph_format.space_after = Pt(4)
        run_ard_c = p_ard_c.add_run("Şekil 8: Arduino Uno Geliştirme Kartı Tespiti (%41 Capacitor)")
        format_run(run_ard_c, font_name="Arial", size_pt=8.5, bold=True, color_rgb=(40, 40, 40))

    # ==================== SAYFA 6 ====================
    # Gercek Sonuclar Tablosu ve Domain Shift Analizi Birlikte
    doc.add_page_break()
    add_clean_heading(doc, "Gerçek Ortam Test Sonuçları Tablosu", level=2, space_before=10, space_after=6)
    
    real_table_data = [
        ("sensor.jpeg", "HC-SR04 Mesafe Sensörü", "Sensor", "%95", "Başarılı Doğru Tespit"),
        ("ledler.jpeg", "5mm Kırmızı LED'ler", "Led", "%71", "Başarılı Doğru Tespit"),
        ("butonlar.jpeg", "4 Bacaklı Push Butonlar", "Button", "%64, %33", "Başarılı Doğru Tespit"),
        ("direncler.jpeg", "Karbon Film Dirençler", "Resistor", "%10 (Capacitor %37)", "Düşük Eşikte Tespit"),
        ("arduino.jpeg", "Arduino Uno R3 Kartı", "Capacitor", "%41", "SMD Blok Soyutlaması")
    ]

    t_real = doc.add_table(rows=1, cols=5)
    t_real.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_real.autofit = False

    t_real_headers = ["Fotoğraf", "Fiziksel Komponent", "Model Tahmini", "Güven", "Sonuç"]
    col_widths = [Inches(1.2), Inches(1.8), Inches(1.2), Inches(0.9), Inches(1.6)]

    hdr_r = t_real.rows[0].cells
    for i, h in enumerate(t_real_headers):
        hdr_r[i].text = h
        hdr_r[i].width = col_widths[i]
        format_run(hdr_r[i].paragraphs[0].runs[0], font_name="Arial", size_pt=9, bold=True, color_rgb=(255, 255, 255))
        set_cell_background(hdr_r[i], "262626")

    for idx, r_data in enumerate(real_table_data):
        row_cells = t_real.add_row().cells
        for col_idx, text_val in enumerate(r_data):
            row_cells[col_idx].text = text_val
            row_cells[col_idx].width = col_widths[col_idx]
            bold_val = (col_idx == 2 or col_idx == 4)
            color_val = (0, 100, 0) if "Başarılı" in text_val else ((0, 0, 0) if col_idx != 4 else (120, 80, 0))
            format_run(row_cells[col_idx].paragraphs[0].runs[0], font_name="Arial", size_pt=8.5, bold=bold_val, color_rgb=color_val)
            bg = "F4F4F5" if idx % 2 == 0 else "FFFFFF"
            set_cell_background(row_cells[col_idx], bg)

    # Tablonun bolunmesini onlemek icin cantSplit ve keep_with_next
    for row_idx, row in enumerate(t_real.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if row_idx < len(t_real.rows) - 1:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True

    # Basari ve Hata Analizi (Domain Shift)
    add_clean_heading(doc, "Başarı ve Hata Analizi (Domain Shift Yorumu)", level=2, space_before=14, space_after=6)
    add_clean_paragraph(
        doc,
        "Elde edilen test sonuçları ve modelin karşılaştığı durumlar aşağıda değerlendirilmiştir:\n"
        "• Alan Kayması (Domain Shift): Eğitim veri setinde yer alan fotoğraflar homojen stüdyo aydınlatması altında, saf beyaz zemin (#FFFFFF) ve tekil makro yakın çekimlerden oluşmaktadır. Telefonla çekilen görüntülerde ise ahşap masa dokusu, çevresel gölgeler ve sıcak oda ışığı yer almaktadır. Buna rağmen model, özgün biçimsel özellikleri korunan ultrasonik sensörde %95, LED'de %71 ve butonlarda %64 güven skoruyla doğru tespit yapmıştır.\n"
        "• Güven Eşiği (Confidence Threshold) Dinamiği: Web arayüzünde varsayılan güven eşiği (%25) seçildiğinde, oda aydınlatmasındaki gölgeler sebebiyle düşük skor alan komponentler ekranda filtrelenmiştir. Güven eşiği %10-%15 seviyesine çekildiğinde dirençler ve diğer bileşenler kutu içine alınabilmiştir.\n"
        "• Morfolojik Benzerlik ve Karışıklıklar: LED fotoğraflarında model %71 ile LED tespit etmiş; ancak yanındaki bazı silindirik LED gövdelerini %59-%61 güvenle 'Capacitor' (elektrolitik kondansatör) olarak etiketlemiştir. Bu durum iki komponentin dikey silindirik gövde ve altından çıkan bacak yapısının yüksek geometrik benzerliğinden kaynaklanmaktadır.\n"
        "• Ölçek ve Çoklu Komponent Yoğunluğu: Arduino Uno fotoğrafında kart bir bütün olarak çekildiğinde, model kartın üzerindeki yüzey montaj (SMD) bloklarını kondansatör kümesi (%41) olarak algılamıştır. Model tekil ayrık devre elemanları üzerinde eğitildiği için kartın tamamını tek bir varlık olarak değil, yerel bileşen blokları olarak sınıflandırma eğilimi göstermiştir.",
        space_before=2, space_after=6, line_spacing=1.15
    )

    # ==================== SAYFA 5 ====================
    doc.add_page_break()

    # 9. Bolum - Tablo Tek Basina Nizami Oturur
    add_clean_heading(doc, "9. Proje Raporu Şablonu")

    table_data = [
        ("Project Title", "Electronic Components Recognition using YOLOv8 & FastAPI"),
        ("Problem / Task", "Nesne Tespiti (Object Detection - 8 Sınıf)"),
        ("Dataset", "Roboflow Universe - Electronic Components Dataset"),
        ("Dataset URL", "https://universe.roboflow.com/samu-drioq/electronic-components-d6uul/dataset/2"),
        ("Model Architecture", "YOLOv8 Nano (yolov8n.pt)"),
        ("Input Size", "640 x 640"),
        ("Hyperparameters", "Epoch: 25, Batch: 16, lr0: 0.001, lrf: 0.01, Patience: 10"),
        ("Optimizer", "AdamW"),
        ("Activation / Output Function", "Gizli katmanlar: SiLU | Çıktı: Sigmoid & Softmax (DFL)"),
        ("Loss Function", "Bbox: CIoU + DFL | Sınıflandırma: BCE"),
        ("Evaluation Metrics", "mAP@50: %91.48 | mAP@50-95: %78.21 | Precision: %86.37 | Recall: %87.99"),
        ("Training Environment", "NVIDIA GeForce RTX 4050 Laptop GPU (6GB), PyTorch 2.6 CUDA 12.4, Windows 11"),
        ("Best Performance", "mAP@50: 0.9148 (%91.48)"),
        ("Inference Time", "3.90 ms / görsel (~256 FPS)"),
        ("Deployment Technology", "FastAPI"),
        ("Repository", "https://github.com/samet/electronic-components-recognition")
    ]

    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Alan"
    hdr_cells[1].text = "Açıklama / Öğrenci Yanıtı"
    format_run(hdr_cells[0].paragraphs[0].runs[0], font_name="Arial", size_pt=10, bold=True, color_rgb=(255, 255, 255))
    format_run(hdr_cells[1].paragraphs[0].runs[0], font_name="Arial", size_pt=10, bold=True, color_rgb=(255, 255, 255))
    set_cell_background(hdr_cells[0], "262626")
    set_cell_background(hdr_cells[1], "262626")
    hdr_cells[0].width = Inches(2.3)
    hdr_cells[1].width = Inches(4.7)

    for i, (k, v) in enumerate(table_data):
        row_cells = table.add_row().cells
        row_cells[0].text = k
        row_cells[1].text = v
        format_run(row_cells[0].paragraphs[0].runs[0], font_name="Arial", size_pt=9.5, bold=True, color_rgb=(0, 0, 0))
        format_run(row_cells[1].paragraphs[0].runs[0], font_name="Arial", size_pt=9.5, bold=False, color_rgb=(30, 30, 30))
        row_cells[0].width = Inches(2.3)
        row_cells[1].width = Inches(4.7)
        bg = "F4F4F5" if i % 2 == 0 else "FFFFFF"
        set_cell_background(row_cells[0], bg)
        set_cell_background(row_cells[1], bg)

    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    doc_path = os.path.abspath("PROJE_RAPORU.docx")
    pdf_path = os.path.abspath("PROJE_RAPORU.pdf")

    doc.save(doc_path)
    print("PROJE_RAPORU.docx basariyla olusturuldu.")

    print("PDF donusumu baslatiliyor...")
    convert(doc_path, pdf_path)
    print("PROJE_RAPORU.pdf basariyla olusturuldu! Boyut:", os.path.getsize(pdf_path), "bytes")

if __name__ == "__main__":
    create_report()
