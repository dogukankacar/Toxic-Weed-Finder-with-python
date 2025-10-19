TR:
Yabani Ot Tespit Sistemi (Python, OpenCV, Tkinter)
Bu proje, tarla fotoğrafları, videolar veya canlı kamera görüntülerinden renk tabanlı görüntü işleme yöntemleriyle zararlı otları tespit etmek üzere tasarlanmış bir masaüstü uygulamasıdır. Kullanıcı dostu bir Tkinter GUI’si üzerinden resim yükleme, kamera ile anlık çekim ve video analizi yapılabilir.
Öne çıkan özellikler:

HSV renk uzayında maskeleme; Gaussian blur ve morfolojik işlemlerle gürültü azaltma.

Kontur tabanlı tespit ile adet, alan ve kaplama yüzdesi hesaplama; tespit edilen nesneler görüntü üzerinde çizilerek gösterilir.

Video modu: belirlenen aralıklarla kare analizi, zaman bazlı tespit raporları ve toplu istatistik çıkarımı.

Raporlama: Analiz sonuçlarını .txt dosyası olarak kaydetme; risk seviyelerine göre öneriler üreten özet metin.

Konfigürasyon: Kullanıcı tarafından ayarlanabilen hassasiyet/skor eşiği.
Teknolojiler: Python, OpenCV, NumPy, Pillow (PIL), Tkinter.
(GitHub: repo-link-ekle — README'de örnek görüntüler, kullanım talimatı ve istenirse model/algoritma geliştirme notları bulunur.)

Bu bir prototiptir şu anlık !!

EN:
Weed Detection System (Python, OpenCV, Tkinter)

This project is a desktop application designed to detect harmful weeds from field photos, videos, or live camera feeds using color-based image processing techniques. Through a user-friendly Tkinter GUI, users can perform image uploads, real-time camera capture, and video analysis.

Key Features:

HSV color space masking; noise reduction using Gaussian blur and morphological operations.

Contour-based detection: calculates count, area, and coverage percentage; detected objects are highlighted on the image.

Video mode: analyzes frames at set intervals, generates time-based detection reports, and extracts aggregated statistics.

Reporting: saves analysis results as .txt files; produces summary text with recommendations based on risk levels.

Configuration: user-adjustable sensitivity/score thresholds.

Technologies: Python, OpenCV, NumPy, Pillow (PIL), Tkinter.

GitHub: [repo-link-here] — the README includes sample images, usage instructions, and optional notes for improving the model/algorithm.

⚠️ Note: This is currently a prototype!
