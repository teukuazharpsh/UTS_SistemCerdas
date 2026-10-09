# UTS Sistem Cerdas (MKP501) - Logika Fuzzy Mamdani
## Sistem Cerdas untuk Pengendalian Penyiraman Tanaman (NIM GENAP)

Repositori ini berisi implementasi program Python, visualisasi grafik, dan laporan analisis untuk Ujian Tengah Semester (UTS) Praktik Sistem Cerdas, Program Studi Teknologi Rekayasa Mekatronika, Politeknik Enjinering Indorama (PEI).

---

## 📋 Deskripsi Kasus
Sebuah sistem penyiraman tanaman otomatis dirancang agar durasi penyiraman menyesuaikan kondisi suhu lingkungan dan kelembapan tanah. Tanaman memerlukan penyiraman lebih lama ketika suhu tinggi dan tanah kering, sedangkan penyiraman perlu dikurangi ketika tanah masih lembap.

* **Metode**: Fuzzy Mamdani (Triangular Membership Function)
* **Operator Implikasi**: MIN
* **Operator Agregasi**: MAX
* **Metode Defuzzifikasi**: Centroid (Center of Gravity)

---

## ⚙️ Spesifikasi Variabel

| Variabel | Peran | Semesta Pembicaraan | Himpunan Fuzzy |
|---|---|---|---|
| **Suhu** | Input 1 | 0 – 40 °C | Dingin, Normal, Panas |
| **Kelembapan Tanah** | Input 2 | 0 – 100 % | Kering, Normal, Lembap |
| **Durasi Penyiraman** | Output | 0 – 30 menit | Singkat, Sedang, Lama |

---

## 🗂️ Struktur Repositori

```text
UTS - 09102026/
├── gui_app.py               # [NEW] Aplikasi Desktop GUI Interaktif Modern (Two-Way Binding & Live Plot)
├── fuzzy_system.py          # Modul perhitungan Fuzzy Mamdani (Fuzzifikasi, Rules, Implikasi, Agregasi, Centroid)
├── visualizer.py            # Modul plotting grafik fungsi keanggotaan dan agregasi-centroid
├── main.py                  # Entrypoint CLI interaktif dan batch testing 10 data
├── LAPORAN_ANALISIS.md      # Laporan analisis lengkap menjawab 4 pertanyaan soal UTS
├── output_grafik/           # Hasil visualisasi grafik beresolusi tinggi (.png)
│   ├── mf_suhu.png
│   ├── mf_kelembapan.png
│   ├── mf_durasi.png
│   ├── grafik_mf_gabungan.png
│   ├── defuzzifikasi_skenario_1.png
│   └── defuzzifikasi_skenario_5.png
├── .gitignore               # Filter file sementara
└── README.md                # Dokumentasi proyek
```

---

## 🚀 Cara Menjalankan Program

### 1. Prasyarat Lingkungan
Pastikan Python 3 telah terpasang dengan pustaka:
```bash
pip install numpy matplotlib
```

### 2. Menjalankan Aplikasi Desktop GUI (Rekomendasi Utama)
Jalankan file `gui_app.py`:
```bash
python gui_app.py
```
Fitur Utama GUI:
* **Identitas Lengkap**: Tersemat nama **Teuku Azhar Pasha (NIM: 202406036)**, Dosen **Dr. E. Agung Nugroho, ST., MT**, dan Prodi TRM PEI.
* **Dual Input & Sinkronisasi 2 Arah**: Slider dan Text Box saling terhubung otomatis secara instan.
* **Proteksi Batas (*Safety Clamping*)**: Jika nilai diinput melebihi rentang (misal Suhu > 40 °C), sistem otomatis melakukan saturasi ke batas aman dengan indikator badge peringatan.
* **Live Matplotlib Display**: Grafik implikasi, agregasi MAX, dan garis centroid langsung bergerak mengikuti perubahan input.
* **4 Tab Terpadu**: Simulasi Real-Time, Kurva MF, Tabel 10 Pengujian Interaktif (bisa ekspor ke CSV), dan Matriks 9 Rule Base beserta jawaban analisis UTS.

### 3. Menjalankan Menu CLI Terminal
Jika ingin menjalankan versi terminal:
```bash
python main.py
```
Menu yang tersedia:
1. **Hitung Durasi Penyiraman (Input Interaktif)**: Masukkan suhu dan kelembapan secara langsung.
2. **Tampilkan Tabel Pengujian 10 Data & Generate Grafik Skenario**: Menjalankan 10 skenario pengujian dan membuat grafik centroid.
3. **Generate Seluruh Grafik Membership Function**: Membuat file grafik fungsi keanggotaan ke folder `output_grafik/`.
4. **Jalankan Semua**: Eksekusi batch seluruh pengujian dan pembuatan grafik.

---

## 📊 Hasil Pengujian 10 Kombinasi Data

| No | Suhu (°C) | Kelembapan (%) | Durasi (menit) | Skenario Pengujian |
|:---:|:---:|:---:|:---:|:---|
| 1 | 15.0 | 20.0 | **15.00** | Soal 1: Suhu Dingin, Tanah Kering |
| 2 | 20.0 | 30.0 | **25.11** | Soal 2: Suhu Dingin-Normal, Tanah Kering-Normal |
| 3 | 25.0 | 50.0 | **15.00** | Soal 3: Suhu Normal, Tanah Normal |
| 4 | 30.0 | 25.0 | **25.35** | Soal 4: Suhu Normal-Panas, Tanah Kering |
| 5 | 35.0 | 15.0 | **25.68** | Soal 5: Suhu Panas, Tanah Kering |
| 6 | 10.0 | 85.0 | **4.65** | Variasi 1: Suhu Dingin, Tanah Sangat Lembap |
| 7 | 38.0 | 10.0 | **25.88** | Variasi 2: Suhu Sangat Panas, Tanah Kering Kritis |
| 8 | 25.0 | 15.0 | **25.74** | Variasi 3: Suhu Normal, Tanah Sangat Kering |
| 9 | 32.0 | 75.0 | **11.33** | Variasi 4: Suhu Panas, Tanah Cukup Lembap |
| 10 | 18.0 | 55.0 | **12.94** | Variasi 5: Suhu Dingin-Normal, Tanah Normal |

Laporan analisis detail dan jawaban lengkap atas 4 pertanyaan evaluasi tersedia di file [LAPORAN_ANALISIS.md](LAPORAN_ANALISIS.md).
