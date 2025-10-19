import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
from datetime import datetime
import json

class YabaniOtTespitSistemi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Yabani Ot Tespit Sistemi - Çiftçi Asistanı")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2E8B57')
        
        # Tespit edilen otlar için veritabanı
        self.yabani_otlar_db = {
            'sirken': {'renk_araligi': ([35, 50, 50], [85, 255, 255]), 'risk': 'yüksek'},
            'koyungözü': {'renk_araligi': ([20, 100, 100], [30, 255, 255]), 'risk': 'orta'},
            'gelincik': {'renk_araligi': ([0, 120, 70], [10, 255, 255]), 'risk': 'düşük'},
            'yabani_hardal': {'renk_araligi': ([25, 150, 150], [35, 255, 255]), 'risk': 'yüksek'}
        }
        
        self.tespit_sonuclari = []
        self.video_sonuclari = []
        self.video_analiz_durumu = False
        self.setup_ui()
        
    def setup_ui(self):
        # Ana başlık
        baslik = tk.Label(self.root, text="Yabani Ot Tespit Sistemi", 
                         font=('Arial', 24, 'bold'), 
                         bg='#2E8B57', fg='white')
        baslik.pack(pady=20)
        
        # Ana çerçeve
        ana_frame = tk.Frame(self.root, bg='#2E8B57')
        ana_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Sol panel - kontroller
        kontrol_frame = tk.Frame(ana_frame, bg='#90EE90', relief='raised', bd=2)
        kontrol_frame.pack(side='left', fill='y', padx=(0, 10))
        
        tk.Label(kontrol_frame, text="Kontrol Paneli", 
                font=('Arial', 16, 'bold'), bg='#90EE90').pack(pady=10)
        
        # Dosya seçme butonu
        tk.Button(kontrol_frame, text="📷 Resim Seç", 
                 command=self.resim_sec, font=('Arial', 12),
                 bg='#32CD32', fg='white', width=20, height=2).pack(pady=10)
        
        # Kamera butonu
        tk.Button(kontrol_frame, text="📹 Kamera Aç", 
                 command=self.kamera_ac, font=('Arial', 12),
                 bg='#228B22', fg='white', width=20, height=2).pack(pady=10)
        
        # Video analizi butonu
        tk.Button(kontrol_frame, text="🎬 Video Analiz Et", 
                 command=self.video_analiz, font=('Arial', 12),
                 bg='#8A2BE2', fg='white', width=20, height=2).pack(pady=10)
        
        # Analiz butonu
        self.analiz_btn = tk.Button(kontrol_frame, text="🔍 Analiz Et", 
                                   command=self.analiz_et, font=('Arial', 12),
                                   bg='#FF6347', fg='white', width=20, height=2,
                                   state='disabled')
        self.analiz_btn.pack(pady=10)
        
        # Rapor butonu
        tk.Button(kontrol_frame, text="📊 Rapor Oluştur", 
                 command=self.rapor_olustur, font=('Arial', 12),
                 bg='#4169E1', fg='white', width=20, height=2).pack(pady=10)
        
        # Video raporu butonu
        tk.Button(kontrol_frame, text="🎬 Video Raporu", 
                 command=self.video_rapor_olustur, font=('Arial', 12),
                 bg='#800080', fg='white', width=20, height=2).pack(pady=10)
        
        # Hassasiyet ayarı
        tk.Label(kontrol_frame, text="Tespit Hassasiyeti:", 
                font=('Arial', 11), bg='#90EE90').pack(pady=(20, 5))
        
        self.hassasiyet = tk.Scale(kontrol_frame, from_=1, to=10, 
                                  orient='horizontal', bg='#90EE90', 
                                  length=180)
        self.hassasiyet.set(5)
        self.hassasiyet.pack(pady=5)
        
        # Sağ panel - görüntü ve sonuçlar
        sag_frame = tk.Frame(ana_frame, bg='#2E8B57')
        sag_frame.pack(side='right', fill='both', expand=True)
        
        # Görüntü alanı
        self.goruntu_frame = tk.Frame(sag_frame, bg='white', relief='sunken', bd=2)
        self.goruntu_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.goruntu_label = tk.Label(self.goruntu_frame, 
                                     text="Lütfen bir resim seçin veya kamera açın",
                                     font=('Arial', 14), bg='white')
        self.goruntu_label.pack(expand=True)
        
        # Sonuçlar alanı
        sonuc_frame = tk.Frame(sag_frame, bg='#F0F8FF', relief='raised', bd=2)
        sonuc_frame.pack(fill='x', pady=10)
        
        tk.Label(sonuc_frame, text="Tespit Sonuçları", 
                font=('Arial', 14, 'bold'), bg='#F0F8FF').pack(pady=5)
        
        # Sonuçlar için text widget
        self.sonuc_text = tk.Text(sonuc_frame, height=8, font=('Arial', 10),
                                 wrap='word', bg='white')
        scrollbar = tk.Scrollbar(sonuc_frame, orient='vertical', 
                                command=self.sonuc_text.yview)
        self.sonuc_text.configure(yscrollcommand=scrollbar.set)
        
        self.sonuc_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        # Durum çubuğu
        self.durum_var = tk.StringVar()
        self.durum_var.set("Hazır")
        durum_bar = tk.Label(self.root, textvariable=self.durum_var, 
                            font=('Arial', 10), bg='#696969', fg='white',
                            anchor='w', padx=10)
        durum_bar.pack(side='bottom', fill='x')
        
        self.mevcut_goruntu = None
        
    def resim_sec(self):
        dosya_tipleri = [('Resim dosyaları', '*.jpg *.jpeg *.png *.bmp *.tiff')]
        dosya_yolu = filedialog.askopenfilename(filetypes=dosya_tipleri)
        
        if dosya_yolu:
            self.goruntu_yukle(dosya_yolu)
            
    def goruntu_yukle(self, dosya_yolu):
        try:
            # OpenCV ile görüntü yükle
            self.mevcut_goruntu = cv2.imread(dosya_yolu)
            if self.mevcut_goruntu is None:
                raise ValueError("Görüntü yüklenemedi")
            
            # Görüntüyü boyutlandır
            h, w = self.mevcut_goruntu.shape[:2]
            max_size = 600
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                self.mevcut_goruntu = cv2.resize(self.mevcut_goruntu, (new_w, new_h))
            
            # Tkinter için görüntüyü dönüştür
            goruntu_rgb = cv2.cvtColor(self.mevcut_goruntu, cv2.COLOR_BGR2RGB)
            goruntu_pil = Image.fromarray(goruntu_rgb)
            goruntu_tk = ImageTk.PhotoImage(goruntu_pil)
            
            # Görüntüyü göster
            self.goruntu_label.configure(image=goruntu_tk, text="")
            self.goruntu_label.image = goruntu_tk
            
            self.analiz_btn.configure(state='normal')
            self.durum_var.set("Görüntü yüklendi - Analiz için hazır")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü yüklenirken hata: {str(e)}")
            
    def kamera_ac(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Hata", "Kamera açılamadı")
                return
            
            # Kamera penceresi
            kamera_pencere = tk.Toplevel(self.root)
            kamera_pencere.title("Kamera Görüntüsü")
            kamera_pencere.geometry("800x600")
            
            kamera_label = tk.Label(kamera_pencere)
            kamera_label.pack(expand=True)
            
            def kamera_guncelle():
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_pil = Image.fromarray(frame_rgb)
                    frame_tk = ImageTk.PhotoImage(frame_pil)
                    kamera_label.configure(image=frame_tk)
                    kamera_label.image = frame_tk
                kamera_pencere.after(30, kamera_guncelle)
            
            def foto_cek():
                ret, frame = cap.read()
                if ret:
                    self.mevcut_goruntu = frame.copy()
                    self.goruntu_yukle_direkt(frame)
                    cap.release()
                    kamera_pencere.destroy()
                    
            tk.Button(kamera_pencere, text="📷 Fotoğraf Çek", 
                     command=foto_cek, font=('Arial', 12),
                     bg='#FF6347', fg='white').pack(pady=10)
                     
            kamera_guncelle()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kamera hatası: {str(e)}")
            
    def goruntu_yukle_direkt(self, goruntu):
        try:
            # Görüntüyü boyutlandır
            h, w = goruntu.shape[:2]
            max_size = 600
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                goruntu = cv2.resize(goruntu, (new_w, new_h))
            
            # Tkinter için görüntüyü dönüştür
            goruntu_rgb = cv2.cvtColor(goruntu, cv2.COLOR_BGR2RGB)
            goruntu_pil = Image.fromarray(goruntu_rgb)
            goruntu_tk = ImageTk.PhotoImage(goruntu_pil)
            
            # Görüntüyü göster
            self.goruntu_label.configure(image=goruntu_tk, text="")
            self.goruntu_label.image = goruntu_tk
            
            self.analiz_btn.configure(state='normal')
            self.durum_var.set("Görüntü hazır - Analiz edebilirsiniz")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü işlenirken hata: {str(e)}")
            
    def analiz_et(self):
        if self.mevcut_goruntu is None:
            messagebox.showwarning("Uyarı", "Lütfen önce bir görüntü seçin")
            return
            
        self.durum_var.set("Analiz ediliyor...")
        self.root.update()
        
        try:
            # Görüntü ön işleme
            hsv = cv2.cvtColor(self.mevcut_goruntu, cv2.COLOR_BGR2HSV)
            
            # Gaussian blur ile gürültü azaltma
            hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
            
            tespit_sonuclari = []
            toplam_yabani_ot_alani = 0
            goruntu_alani = self.mevcut_goruntu.shape[0] * self.mevcut_goruntu.shape[1]
            
            # Her yabani ot türü için tespit
            for ot_adi, ot_bilgi in self.yabani_otlar_db.items():
                alt_sinir, ust_sinir = ot_bilgi['renk_araligi']
                
                # Hassasiyet ayarına göre renk aralığını ayarla
                hassasiyet_faktor = self.hassasiyet.get() / 5.0
                
                # Renk maskeleme
                mask = cv2.inRange(hsv, np.array(alt_sinir), np.array(ust_sinir))
                
                # Morfolojik işlemler
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Konturları bul
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                ot_alani = 0
                ot_sayisi = 0
                
                for contour in contours:
                    alan = cv2.contourArea(contour)
                    # Minimum alan eşiği (gürültüyü filtrele)
                    if alan > 100 * hassasiyet_faktor:
                        ot_alani += alan
                        ot_sayisi += 1
                        
                        # Görüntü üzerine tespit çiz
                        cv2.drawContours(self.mevcut_goruntu, [contour], -1, (0, 255, 0), 2)
                        
                        # Merkez noktasını işaretle
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            cv2.circle(self.mevcut_goruntu, (cx, cy), 5, (255, 0, 0), -1)
                            cv2.putText(self.mevcut_goruntu, ot_adi, (cx-20, cy-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                if ot_sayisi > 0:
                    yuzde = (ot_alani / goruntu_alani) * 100
                    tespit_sonuclari.append({
                        'ot_adi': ot_adi,
                        'sayisi': ot_sayisi,
                        'alan_yuzdesi': yuzde,
                        'risk_seviyesi': ot_bilgi['risk']
                    })
                    toplam_yabani_ot_alani += ot_alani
            
            # Sonuçları güncelle
            self.tespit_sonuclari = tespit_sonuclari
            self.sonuclari_goster(tespit_sonuclari, toplam_yabani_ot_alani, goruntu_alani)
            
            # İşlenmiş görüntüyü göster
            self.goruntu_yukle_direkt(self.mevcut_goruntu)
            
            self.durum_var.set(f"Analiz tamamlandı - {len(tespit_sonuclari)} tür yabani ot tespit edildi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Analiz sırasında hata: {str(e)}")
            self.durum_var.set("Analiz hatası")
            
    def sonuclari_goster(self, sonuclar, toplam_ot_alani, toplam_alan):
        self.sonuc_text.delete(1.0, tk.END)
        
        if not sonuclar:
            self.sonuc_text.insert(tk.END, "✅ Tebrikler! Yabani ot tespit edilmedi.\n")
            self.sonuc_text.insert(tk.END, "Tarlanız temiz görünüyor.\n")
            return
        
        toplam_yuzde = (toplam_ot_alani / toplam_alan) * 100
        
        self.sonuc_text.insert(tk.END, f"🌾 YABANI OT TESPİT RAPORU\n")
        self.sonuc_text.insert(tk.END, f"{'='*40}\n\n")
        
        self.sonuc_text.insert(tk.END, f"📊 Genel Durum:\n")
        self.sonuc_text.insert(tk.END, f"• Toplam yabani ot kaplamı: %{toplam_yuzde:.1f}\n")
        
        if toplam_yuzde < 5:
            self.sonuc_text.insert(tk.END, f"• Durum: ✅ İyi - Düşük seviye\n\n")
        elif toplam_yuzde < 15:
            self.sonuc_text.insert(tk.END, f"• Durum: ⚠️ Orta - Dikkat gerekli\n\n")
        else:
            self.sonuc_text.insert(tk.END, f"• Durum: 🚨 Yüksek - Acil müdahale\n\n")
        
        self.sonuc_text.insert(tk.END, f"🔍 Tespit Edilen Yabani Otlar:\n\n")
        
        for sonuc in sonuclar:
            risk_emoji = {'düşük': '🟢', 'orta': '🟡', 'yüksek': '🔴'}
            self.sonuc_text.insert(tk.END, f"{risk_emoji[sonuc['risk_seviyesi']]} {sonuc['ot_adi'].upper()}\n")
            self.sonuc_text.insert(tk.END, f"   • Adet: {sonuc['sayisi']}\n")
            self.sonuc_text.insert(tk.END, f"   • Kaplama: %{sonuc['alan_yuzdesi']:.1f}\n")
            self.sonuc_text.insert(tk.END, f"   • Risk: {sonuc['risk_seviyesi']}\n\n")
        
        # Öneriler
        self.sonuc_text.insert(tk.END, f"💡 ÖNERİLER:\n")
        if toplam_yuzde > 10:
            self.sonuc_text.insert(tk.END, f"• Herbisit uygulaması önerilir\n")
            self.sonuc_text.insert(tk.END, f"• Mekanik mücadele düşünülebilir\n")
        else:
            self.sonuc_text.insert(tk.END, f"• Düzenli takip yapın\n")
            self.sonuc_text.insert(tk.END, f"• Erken müdahale için hazır olun\n")
            
    def rapor_olustur(self):
        if not self.tespit_sonuclari:
            messagebox.showwarning("Uyarı", "Rapor oluşturmak için önce analiz yapın")
            return
            
        try:
            # Dosya adı
            tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"yabani_ot_raporu_{tarih}.txt"
            
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.write("YABANI OT TESPİT RAPORU\n")
                f.write("="*50 + "\n\n")
                f.write(f"Tarih: {datetime.now().strftime('%d/%m/%Y - %H:%M')}\n")
                f.write(f"Uygulama: Yabani Ot Tespit Sistemi v1.0\n\n")
                
                if self.tespit_sonuclari:
                    f.write("TESPİT EDİLEN YABANI OTLAR:\n")
                    f.write("-" * 30 + "\n")
                    
                    for sonuc in self.tespit_sonuclari:
                        f.write(f"\nOt Türü: {sonuc['ot_adi']}\n")
                        f.write(f"Adet: {sonuc['sayisi']}\n")
                        f.write(f"Kaplama Alanı: %{sonuc['alan_yuzdesi']:.2f}\n")
                        f.write(f"Risk Seviyesi: {sonuc['risk_seviyesi']}\n")
                        
                    # Genel değerlendirme
                    toplam_yuzde = sum(s['alan_yuzdesi'] for s in self.tespit_sonuclari)
                    f.write(f"\nGENEL DEĞERLENDİRME:\n")
                    f.write(f"Toplam Yabani Ot Kaplamı: %{toplam_yuzde:.2f}\n")
                    
                    if toplam_yuzde < 5:
                        f.write("Durum: Düşük risk - Takip önerilir\n")
                    elif toplam_yuzde < 15:
                        f.write("Durum: Orta risk - Müdahale planlanmalı\n")
                    else:
                        f.write("Durum: Yüksek risk - Acil müdahale gerekli\n")
                        
                else:
                    f.write("Yabani ot tespit edilmedi.\n")
                    f.write("Tarla durumu: Temiz\n")
            
            messagebox.showinfo("Başarılı", f"Rapor oluşturuldu: {dosya_adi}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulurken hata: {str(e)}")
            
    def video_analiz(self):
        """Video dosyasını seçip analiz eder"""
        dosya_tipleri = [('Video dosyaları', '*.mp4 *.avi *.mov *.mkv *.wmv *.flv')]
        video_yolu = filedialog.askopenfilename(filetypes=dosya_tipleri)
        
        if not video_yolu:
            return
            
        # Video analiz penceresi oluştur
        self.video_analiz_penceresi(video_yolu)
        
    def video_analiz_penceresi(self, video_yolu):
        """Video analiz penceresi"""
        video_pencere = tk.Toplevel(self.root)
        video_pencere.title("Video Analizi - Yabani Ot Tespiti")
        video_pencere.geometry("1000x700")
        video_pencere.configure(bg='#2E8B57')
        
        # Başlık
        tk.Label(video_pencere, text="Video Yabani Ot Analizi", 
                font=('Arial', 18, 'bold'), bg='#2E8B57', fg='white').pack(pady=10)
        
        # Video görüntü alanı
        video_frame = tk.Frame(video_pencere, bg='black', relief='sunken', bd=2)
        video_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        video_label = tk.Label(video_frame, bg='black', text="Video yükleniyor...", 
                              fg='white', font=('Arial', 14))
        video_label.pack(expand=True)
        
        # Kontrol çubuğu
        kontrol_frame = tk.Frame(video_pencere, bg='#90EE90', height=100)
        kontrol_frame.pack(fill='x', padx=20, pady=10)
        kontrol_frame.pack_propagate(False)
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(kontrol_frame, variable=progress_var, 
                                     maximum=100, length=300)
        progress_bar.pack(pady=10)
        
        # Durum etiketi
        durum_label = tk.Label(kontrol_frame, text="", bg='#90EE90', 
                              font=('Arial', 10))
        durum_label.pack()
        
        # Kontrol butonları
        buton_frame = tk.Frame(kontrol_frame, bg='#90EE90')
        buton_frame.pack(pady=10)
        
        baslat_btn = tk.Button(buton_frame, text="▶️ Analizi Başlat", 
                              font=('Arial', 11), bg='#32CD32', fg='white',
                              command=lambda: self.video_analizi_baslat(
                                  video_yolu, video_label, progress_var, 
                                  durum_label, baslat_btn, durdur_btn))
        baslat_btn.pack(side='left', padx=5)
        
        durdur_btn = tk.Button(buton_frame, text="⏹️ Durdur", 
                              font=('Arial', 11), bg='#FF6347', fg='white',
                              command=self.video_analizi_durdur, state='disabled')
        durdur_btn.pack(side='left', padx=5)
        
        # Sonuç alanı
        sonuc_frame = tk.Frame(video_pencere, bg='#F0F8FF', relief='raised', bd=2)
        sonuc_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(sonuc_frame, text="Video Analiz Sonuçları", 
                font=('Arial', 12, 'bold'), bg='#F0F8FF').pack(pady=5)
        
        self.video_sonuc_text = tk.Text(sonuc_frame, height=6, font=('Arial', 9),
                                       wrap='word', bg='white')
        video_scrollbar = tk.Scrollbar(sonuc_frame, orient='vertical', 
                                      command=self.video_sonuc_text.yview)
        self.video_sonuc_text.configure(yscrollcommand=video_scrollbar.set)
        
        self.video_sonuc_text.pack(side='left', fill='both', expand=True, 
                                  padx=5, pady=5)
        video_scrollbar.pack(side='right', fill='y', pady=5)
        
    def video_analizi_baslat(self, video_yolu, video_label, progress_var, 
                           durum_label, baslat_btn, durdur_btn):
        """Video analizini başlatır"""
        self.video_analiz_durumu = True
        baslat_btn.configure(state='disabled')
        durdur_btn.configure(state='normal')
        
        # Video yakalama nesnesi oluştur
        cap = cv2.VideoCapture(video_yolu)
        
        if not cap.isOpened():
            messagebox.showerror("Hata", "Video dosyası açılamadı!")
            return
            
        # Video bilgileri
        toplam_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        sure = toplam_frame / fps if fps > 0 else 0
        
        durum_label.configure(text=f"Video: {sure:.1f}s, {toplam_frame} frame")
        
        # Analiz değişkenleri
        self.video_sonuclari = []
        frame_sayaci = 0
        analiz_araliği = max(1, fps // 2)  # Saniyede 2 frame analiz et
        
        try:
            while cap.isOpened() and self.video_analiz_durumu:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame_sayaci += 1
                
                # Progress güncelle
                progress = (frame_sayaci / toplam_frame) * 100
                progress_var.set(progress)
                
                # Video görüntüsünü göster (her 5. frame)
                if frame_sayaci % 5 == 0:
                    self.video_frame_goster(frame, video_label)
                
                # Belirli aralıklarla analiz yap
                if frame_sayaci % analiz_araliği == 0:
                    frame_sonucu = self.frame_analiz_et(frame, frame_sayaci, fps)
                    if frame_sonucu:
                        self.video_sonuclari.append(frame_sonucu)
                        
                # Durum güncelle
                if frame_sayaci % (fps * 2) == 0:  # 2 saniyede bir güncelle
                    zaman = frame_sayaci / fps
                    durum_label.configure(text=f"Analiz ediliyor... {zaman:.1f}s / {sure:.1f}s")
                    
                # UI güncelle
                video_label.master.update()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Video analizi sırasında hata: {str(e)}")
        finally:
            cap.release()
            
        # Analiz tamamlandı
        self.video_analiz_durumu = False
        baslat_btn.configure(state='normal')
        durdur_btn.configure(state='disabled')
        progress_var.set(100)
        durum_label.configure(text="Analiz tamamlandı!")
        
        # Sonuçları göster
        self.video_sonuclarini_goster()
        
    def video_analizi_durdur(self):
        """Video analizini durdurur"""
        self.video_analiz_durumu = False
        
    def video_frame_goster(self, frame, video_label):
        """Video frame'ini label'da gösterir"""
        try:
            # Frame'i boyutlandır
            h, w = frame.shape[:2]
            max_size = 400
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h))
            
            # BGR'den RGB'ye çevir
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Label'ı güncelle
            video_label.configure(image=frame_tk, text="")
            video_label.image = frame_tk
            
        except Exception as e:
            print(f"Frame gösterme hatası: {e}")
            
    def frame_analiz_et(self, frame, frame_no, fps):
        """Tek bir frame'i analiz eder"""
        try:
            # Görüntü ön işleme
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
            
            frame_sonucu = {
                'frame_no': frame_no,
                'zaman': frame_no / fps,
                'tespit_edilen_otlar': [],
                'toplam_ot_alani': 0
            }
            
            goruntu_alani = frame.shape[0] * frame.shape[1]
            hassasiyet_faktor = self.hassasiyet.get() / 5.0
            
            # Her yabani ot türü için tespit
            for ot_adi, ot_bilgi in self.yabani_otlar_db.items():
                alt_sinir, ust_sinir = ot_bilgi['renk_araligi']
                
                # Renk maskeleme
                mask = cv2.inRange(hsv, np.array(alt_sinir), np.array(ust_sinir))
                
                # Morfolojik işlemler
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Konturları bul
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                ot_alani = 0
                ot_sayisi = 0
                
                for contour in contours:
                    alan = cv2.contourArea(contour)
                    if alan > 50 * hassasiyet_faktor:  # Video için daha düşük eşik
                        ot_alani += alan
                        ot_sayisi += 1
                
                if ot_sayisi > 0:
                    yuzde = (ot_alani / goruntu_alani) * 100
                    frame_sonucu['tespit_edilen_otlar'].append({
                        'ot_adi': ot_adi,
                        'sayisi': ot_sayisi,
                        'alan_yuzdesi': yuzde,
                        'risk_seviyesi': ot_bilgi['risk']
                    })
                    frame_sonucu['toplam_ot_alani'] += ot_alani
            
            # Eğer yabani ot tespit edildiyse sonucu döndür
            if frame_sonucu['tespit_edilen_otlar']:
                return frame_sonucu
            
        except Exception as e:
            print(f"Frame analiz hatası: {e}")
            
        return None
        
    def video_sonuclarini_goster(self):
        """Video analiz sonuçlarını gösterir"""
        self.video_sonuc_text.delete(1.0, tk.END)
        
        if not self.video_sonuclari:
            self.video_sonuc_text.insert(tk.END, "✅ Video analizi tamamlandı!\n")
            self.video_sonuc_text.insert(tk.END, "Videoda yabani ot tespit edilmedi.\n")
            return
            
        # Genel istatistikler
        toplam_frame = len(self.video_sonuclari)
        
        # Ot türlerini topla
        ot_istatistik = {}
        risk_dagilimlari = {'düşük': 0, 'orta': 0, 'yüksek': 0}
        
        for frame_sonucu in self.video_sonuclari:
            for ot in frame_sonucu['tespit_edilen_otlar']:
                ot_adi = ot['ot_adi']
                if ot_adi not in ot_istatistik:
                    ot_istatistik[ot_adi] = {'toplam_sayisi': 0, 'ortalama_kaplama': 0, 
                                           'gorunme_sayisi': 0, 'risk': ot['risk_seviyesi']}
                
                ot_istatistik[ot_adi]['toplam_sayisi'] += ot['sayisi']
                ot_istatistik[ot_adi]['ortalama_kaplama'] += ot['alan_yuzdesi']
                ot_istatistik[ot_adi]['gorunme_sayisi'] += 1
                risk_dagilimlari[ot['risk_seviyesi']] += 1
        
        # Ortalama kaplama hesapla
        for ot_adi in ot_istatistik:
            ot_istatistik[ot_adi]['ortalama_kaplama'] /= ot_istatistik[ot_adi]['gorunme_sayisi']
        
        # Sonuçları yazdır
        self.video_sonuc_text.insert(tk.END, f"🎬 VİDEO ANALİZ RAPORU\n")
        self.video_sonuc_text.insert(tk.END, f"{'='*50}\n\n")
        
        self.video_sonuc_text.insert(tk.END, f"📊 Genel Durum:\n")
        self.video_sonuc_text.insert(tk.END, f"• Yabani ot tespit edilen frame sayısı: {toplam_frame}\n")
        self.video_sonuc_text.insert(tk.END, f"• Tespit edilen ot türü sayısı: {len(ot_istatistik)}\n\n")
        
        self.video_sonuc_text.insert(tk.END, f"🔍 Tespit Edilen Yabani Otlar:\n\n")
        
        for ot_adi, istatistik in ot_istatistik.items():
            risk_emoji = {'düşük': '🟢', 'orta': '🟡', 'yüksek': '🔴'}
            self.video_sonuc_text.insert(tk.END, f"{risk_emoji[istatistik['risk']]} {ot_adi.upper()}\n")
            self.video_sonuc_text.insert(tk.END, f"   • Toplam görünme: {istatistik['gorunme_sayisi']} frame\n")
            self.video_sonuc_text.insert(tk.END, f"   • Ortalama kaplama: %{istatistik['ortalama_kaplama']:.1f}\n")
            self.video_sonuc_text.insert(tk.END, f"   • Risk seviyesi: {istatistik['risk']}\n\n")
        
        # Risk dağılımı
        self.video_sonuc_text.insert(tk.END, f"⚠️ Risk Dağılımı:\n")
        self.video_sonuc_text.insert(tk.END, f"• 🟢 Düşük risk: {risk_dagilimlari['düşük']} tespit\n")
        self.video_sonuc_text.insert(tk.END, f"• 🟡 Orta risk: {risk_dagilimlari['orta']} tespit\n")
        self.video_sonuc_text.insert(tk.END, f"• 🔴 Yüksek risk: {risk_dagilimlari['yüksek']} tespit\n\n")
        
        # Öneriler
        toplam_yuksek_risk = risk_dagilimlari['yüksek'] + risk_dagilimlari['orta']
        self.video_sonuc_text.insert(tk.END, f"💡 ÖNERİLER:\n")
        if toplam_yuksek_risk > toplam_frame * 0.3:
            self.video_sonuc_text.insert(tk.END, f"• 🚨 Acil müdahale gerekli!\n")
            self.video_sonuc_text.insert(tk.END, f"• Herbisit uygulaması önerilir\n")
        elif toplam_yuksek_risk > 0:
            self.video_sonuc_text.insert(tk.END, f"• ⚠️ Düzenli takip yapın\n")
            self.video_sonuc_text.insert(tk.END, f"• Mekanik mücadele düşünülebilir\n")
        else:
            self.video_sonuc_text.insert(tk.END, f"• ✅ Mevcut durum kontrol altında\n")  
            self.video_sonuc_text.insert(tk.END, f"• Preventif önlemler alın\n")
            
    def video_rapor_olustur(self):
        """Video analiz raporu oluşturur"""
        if not self.video_sonuclari:
            messagebox.showwarning("Uyarı", "Video raporu oluşturmak için önce video analizi yapın")
            return
            
        try:
            # Dosya adı
            tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
            dosya_adi = f"video_yabani_ot_raporu_{tarih}.txt"
            
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.write("VIDEO YABANI OT TESPİT RAPORU\n")
                f.write("="*60 + "\n\n")
                f.write(f"Tarih: {datetime.now().strftime('%d/%m/%Y - %H:%M')}\n")
                f.write(f"Uygulama: Yabani Ot Tespit Sistemi v1.0\n")
                f.write(f"Analiz Türü: Video Analizi\n\n")
                
                # Genel istatistikler
                toplam_frame = len(self.video_sonuclari)
                f.write(f"GENEL İSTATİSTİKLER:\n")
                f.write(f"-" * 30 + "\n")
                f.write(f"Yabani ot tespit edilen frame sayısı: {toplam_frame}\n")
                
                # Ot türlerini topla
                ot_istatistik = {}
                risk_dagilimlari = {'düşük': 0, 'orta': 0, 'yüksek': 0}
                
                for frame_sonucu in self.video_sonuclari:
                    for ot in frame_sonucu['tespit_edilen_otlar']:
                        ot_adi = ot['ot_adi']
                        if ot_adi not in ot_istatistik:
                            ot_istatistik[ot_adi] = {'toplam_sayisi': 0, 'ortalama_kaplama': 0, 
                                                   'gorunme_sayisi': 0, 'risk': ot['risk_seviyesi']}
                        
                        ot_istatistik[ot_adi]['toplam_sayisi'] += ot['sayisi']
                        ot_istatistik[ot_adi]['ortalama_kaplama'] += ot['alan_yuzdesi']
                        ot_istatistik[ot_adi]['gorunme_sayisi'] += 1
                        risk_dagilimlari[ot['risk_seviyesi']] += 1
                
                # Ortalama kaplama hesapla
                for ot_adi in ot_istatistik:
                    ot_istatistik[ot_adi]['ortalama_kaplama'] /= ot_istatistik[ot_adi]['gorunme_sayisi']
                
                f.write(f"Tespit edilen ot türü sayısı: {len(ot_istatistik)}\n\n")
                
                # Detaylı ot analizi
                f.write("TESPİT EDİLEN YABANI OTLAR:\n")
                f.write("-" * 40 + "\n\n")
                
                for ot_adi, istatistik in ot_istatistik.items():
                    f.write(f"Ot Türü: {ot_adi.upper()}\n")
                    f.write(f"Görünme Sıklığı: {istatistik['gorunme_sayisi']} frame\n")
                    f.write(f"Ortalama Kaplama: %{istatistik['ortalama_kaplama']:.2f}\n")
                    f.write(f"Risk Seviyesi: {istatistik['risk']}\n")
                    f.write("-" * 20 + "\n")
                
                # Risk değerlendirmesi
                f.write(f"\nRİSK DEĞERLENDİRMESİ:\n")
                f.write(f"Düşük Risk Tespitleri: {risk_dagilimlari['düşük']}\n")
                f.write(f"Orta Risk Tespitleri: {risk_dagilimlari['orta']}\n")
                f.write(f"Yüksek Risk Tespitleri: {risk_dagilimlari['yüksek']}\n\n")
                
                # Zaman bazlı analiz
                f.write("ZAMAN BAZLI ANALİZ:\n")
                f.write("-" * 25 + "\n")
                for i, frame_sonucu in enumerate(self.video_sonuclari[:10]):  # İlk 10 tespit
                    f.write(f"Zaman: {frame_sonucu['zaman']:.1f}s - ")
                    f.write(f"Frame: {frame_sonucu['frame_no']} - ")
                    f.write(f"Tespit: {len(frame_sonucu['tespit_edilen_otlar'])} tür\n")
                
                if len(self.video_sonuclari) > 10:
                    f.write(f"... ve {len(self.video_sonuclari) - 10} tespit daha\n")
                
                # Öneriler
                toplam_yuksek_risk = risk_dagilimlari['yüksek'] + risk_dagilimlari['orta']
                f.write(f"\nÖNERİLER:\n")
                f.write("-" * 15 + "\n")
                if toplam_yuksek_risk > toplam_frame * 0.3:
                    f.write("- Acil müdahale gerekli!\n")
                    f.write("- Herbisit uygulaması önerilir\n")
                    f.write("- Uzman danışmanlığı alın\n")
                elif toplam_yuksek_risk > 0:
                    f.write("- Düzenli takip yapın\n")
                    f.write("- Mekanik mücadele düşünülebilir\n")
                    f.write("- Preventif ilaçlama planı yapın\n")
                else:
                    f.write("- Mevcut durum kontrol altında\n")
                    f.write("- Preventif önlemler almaya devam edin\n")
                    f.write("- Düzenli kontrol yapın\n")
            
            messagebox.showinfo("Başarılı", f"Video raporu oluşturuldu: {dosya_adi}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Video raporu oluşturulurken hata: {str(e)}")
    
    def calistir(self):
        self.root.mainloop()

# Ana program
if __name__ == "__main__":
    print("Yabani Ot Tespit Sistemi başlatılıyor...")
    print("Gerekli kütüphaneler kontrol ediliyor...")
    
    try:
        uygulama = YabaniOtTespitSistemi()
        print("Sistem hazır!")
        uygulama.calistir()
    except Exception as e:
        print(f"Sistem başlatılırken hata: {e}")
        print("Lütfen gerekli kütüphanelerin yüklü olduğundan emin olun:")
        print("pip install opencv-python pillow numpy")