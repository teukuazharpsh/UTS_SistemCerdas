# LAPORAN UJIAN TENGAH SEMESTER (UTS)
## SISTEM CERDAS (MKP501) - KELOMPOK NIM GENAP
**Sistem Cerdas untuk Pengendalian Penyiraman Tanaman Menggunakan Logika Fuzzy Mamdani**

* **Mata Kuliah** : MKP501 Sistem Cerdas
* **Program Studi**: Sarjana Terapan Teknologi Rekayasa Mekatronika (TRM)
* **Semester / Kelas** : 5 / 1
* **Institusi**    : Politeknik Enjinering Indorama (PEI)
* **Dosen Pengampu**: Dr. E. Agung Nugroho, ST., MT

---

## 1. Perancangan Sistem Fuzzy

### 1.1 Variabel dan Semesta Pembicaraan (Universe of Discourse)
Sistem cerdas pengendalian penyiraman tanaman ini menggunakan 2 variabel input dan 1 variabel output:
1. **Suhu Udara (Input)**: Rentang $0 - 40\ ^\circ\text{C}$
2. **Kelembapan Tanah (Input)**: Rentang $0 - 100\%$
3. **Durasi Penyiraman (Output)**: Rentang $0 - 30\text{ menit}$

### 1.2 Parameter Fungsi Keanggotaan (*Triangular Membership Function*)
Fungsi keanggotaan segitiga dinyatakan dengan format $[a, b, c]$, di mana:
* $a$ = titik batas kiri ($\mu = 0$)
* $b$ = titik puncak ($\mu = 1$)
* $c$ = titik batas kanan ($\mu = 0$)

| Variabel | Himpunan Fuzzy | Tipe Kurva | Parameter $[a, b, c]$ | Keterangan Fisik |
|---|---|---|---|---|
| **Suhu** ($0 - 40\ ^\circ\text{C}$) | **Dingin** | Segitiga (Bahu Kiri) | $[0, 0, 20]$ | Suhu sejuk/rendah di bawah $20^\circ\text{C}$ |
| | **Normal** | Segitiga | $[15, 25, 35]$ | Suhu optimal tanaman ($15^\circ\text{C} - 35^\circ\text{C}$) |
| | **Panas** | Segitiga (Bahu Kanan) | $[25, 40, 40]$ | Suhu tinggi terik di atas $25^\circ\text{C}$ |
| **Kelembapan Tanah** ($0 - 100\%$) | **Kering** | Segitiga (Bahu Kiri) | $[0, 0, 50]$ | Tanah gersang membutuhkan pasokan air |
| | **Normal** | Segitiga | $[30, 50, 70]$ | Kapasitas lapang/kelembapan ideal tanah |
| | **Lembap** | Segitiga (Bahu Kanan) | $[50, 100, 100]$ | Tanah basah/kandungan air tinggi |
| **Durasi Penyiraman** ($0 - 30\text{ menit}$) | **Singkat** | Segitiga (Bahu Kiri) | $[0, 0, 12]$ | Penyiraman minimal ($0 - 12$ menit) |
| | **Sedang** | Segitiga | $[8, 15, 22]$ | Penyiraman moderat ($8 - 22$ menit) |
| | **Lama** | Segitiga (Bahu Kanan) | $[18, 30, 30]$ | Penyiraman intensif ($18 - 30$ menit) |

### 1.3 Alasan Pemilihan Parameter
1. **Overlap yang Cukup (Tumpang Tindih)**:
   Setiap fungsi keanggotaan yang bertetangga memiliki area *overlap* sebesar $5 - 10$ satuan (misal Suhu: Dingin-Normal tumpang tindih pada rentang $15 - 20^\circ\text{C}$, Normal-Panas pada $25 - 35^\circ\text{C}$). Hal ini menjamin:
   * **Kelancaran transisi (smoothness)** output aktuator katup penyiram tanpa lonjakan drastis.
   * **Tidak ada *blind spot*** (seluruh nilai input di dalam semesta pembicaraan selalu tercover oleh minimal 1 aturan fuzzy).
2. **Kesesuaian dengan Karakter Fisik Tanaman**:
   * Suhu di atas $25^\circ\text{C}$ meningkatkan laju evapotranspirasi tanah dan daun secara eksponensial.
   * Kelembapan di bawah $30\%$ menandakan tanaman mendekati *wilting point* (titik layu sementara) sehingga durasi penyiraman harus dinaikkan secara proporsional.

---

## 2. Penyusunan Rule Base (Aturan IF–THEN)

Rule base disusun dengan memetakan seluruh kombinasi himpunan fuzzy ($3 \times 3 = 9$ Aturan):

| No. Aturan | Kondisi Suhu | Operator | Kondisi Kelembapan | Konsekuen Durasi Penyiraman | Logika Rekayasa Mekatronika |
|---|---|---|---|---|---|
| **R1** | DINGIN | AND | KERING | **SEDANG** | Tanah kering butuh air, namun suhu dingin mengurangi evaporasi. |
| **R2** | DINGIN | AND | NORMAL | **SINGKAT** | Air cukup & suhu rendah; cukup penyiraman minimal menjaga kelembapan. |
| **R3** | DINGIN | AND | LEMBAP | **SINGKAT** | Tanah sudah basah dan suhu dingin; penyiraman dihemat agar tidak busuk akar. |
| **R4** | NORMAL | AND | KERING | **LAMA** | Suhu sedang namun tanah kering membutuhkan pemulihan kadar air optimal. |
| **R5** | NORMAL | AND | NORMAL | **SEDANG** | Kondisi standar operasional penyiraman rutin. |
| **R6** | NORMAL | AND | LEMBAP | **SINGKAT** | Tanah sudah lembap; penyiraman dikurangi untuk efisiensi air. |
| **R7** | PANAS | AND | KERING | **LAMA** | Kondisi paling kritis; penguapan tinggi dan tanah gersang menuntut penyiraman maksimum. |
| **R8** | PANAS | AND | NORMAL | **LAMA** | Meskipun tanah normal, suhu panas cepat mengeringkan tanah dalam waktu singkat. |
| **R9** | PANAS | AND | LEMBAP | **SEDANG** | Suhu panas memerlukan penyiraman sedang agar tanah tidak lekas kering. |

---

## 3. Implementasi Proses Fuzzy Mamdani

Tahapan komputasi yang diimplementasikan pada file program Python `fuzzy_system.py`:
1. **Input**: Menerima nilai kontinu suhu udara ($x_1$) dan kelembapan tanah ($x_2$).
2. **Fuzzifikasi**: Menghitung nilai $\mu(x)$ untuk tiap himpunan menggunakan fungsi segitiga `trimf`.
3. **Evaluasi Rule Base & Firing Strength**:
   $$\alpha_i = \min(\mu_{\text{Suhu}, i}(x_1), \mu_{\text{Kelembapan}, i}(x_2))$$
4. **Implikasi (Metode MIN / Clipping)**:
   Memotong kurva fungsi keanggotaan output pada ketinggian $\alpha_i$:
   $$\mu_{\text{implikasi}, i}(y) = \min(\alpha_i, \mu_{\text{Durasi}, i}(y))$$
5. **Agregasi (Metode MAX / Union)**:
   Menggabungkan seluruh kurva terpotong dari setiap aturan yang aktif:
   $$\mu_{\text{agregasi}}(y) = \max_{i=1..9}(\mu_{\text{implikasi}, i}(y))$$
6. **Defuzzifikasi Centroid (Center of Gravity)**:
   Menghitung titik berat dari kurva area agregasi:
   $$z^* = \frac{\int y \cdot \mu_{\text{agregasi}}(y) \, dy}{\int \mu_{\text{agregasi}}(y) \, dy} \approx \frac{\sum y_j \cdot \mu_{\text{agregasi}}(y_j)}{\sum \mu_{\text{agregasi}}(y_j)}$$
7. **Output**: Nilai skalar durasi penyiraman dalam satuan menit.

---

## 4. Pengujian dan Visualisasi

### 4.1 Tabel Hasil Pengujian 10 Kombinasi Data Input

| No | Suhu (°C) | Kelembapan Tanah (%) | Durasi Penyiraman (Menit) | Kategori & Skenario Pengujian |
|:---:|:---:|:---:|:---:|:---|
| **1** | 15.0 | 20.0 | **15.00** | *Soal UTS 1*: Suhu Dingin, Tanah Kering |
| **2** | 20.0 | 30.0 | **25.11** | *Soal UTS 2*: Suhu Dingin-Normal, Tanah Kering-Normal |
| **3** | 25.0 | 50.0 | **15.00** | *Soal UTS 3*: Suhu Normal, Tanah Normal |
| **4** | 30.0 | 25.0 | **25.35** | *Soal UTS 4*: Suhu Normal-Panas, Tanah Kering |
| **5** | 35.0 | 15.0 | **25.68** | *Soal UTS 5*: Suhu Panas, Tanah Kering |
| **6** | 10.0 | 85.0 | **4.65** | *Variasi Mahasiswa 1*: Suhu Dingin, Tanah Sangat Lembap |
| **7** | 38.0 | 10.0 | **25.88** | *Variasi Mahasiswa 2*: Suhu Sangat Panas, Tanah Kering Kritis |
| **8** | 25.0 | 15.0 | **25.74** | *Variasi Mahasiswa 3*: Suhu Normal, Tanah Sangat Kering |
| **9** | 32.0 | 75.0 | **11.33** | *Variasi Mahasiswa 4*: Suhu Panas, Tanah Cukup Lembap |
| **10** | 18.0 | 55.0 | **12.94** | *Variasi Mahasiswa 5*: Suhu Dingin-Normal, Tanah Normal |

### 4.2 File Visualisasi Grafik yang Dihasilkan
Seluruh grafik telah digenerate otomatis ke folder `output_grafik/`:
1. `output_grafik/mf_suhu.png`: Grafik fungsi keanggotaan variabel Suhu.
2. `output_grafik/mf_kelembapan.png`: Grafik fungsi keanggotaan variabel Kelembapan Tanah.
3. `output_grafik/mf_durasi.png`: Grafik fungsi keanggotaan variabel Durasi Penyiraman.
4. `output_grafik/grafik_mf_gabungan.png`: Kompilasi seluruh fungsi keanggotaan (3 subplot).
5. `output_grafik/defuzzifikasi_skenario_1.png`: Grafik implikasi, agregasi MAX, dan posisi Centroid untuk Skenario 1 ($15^\circ\text{C}, 20\%$).
6. `output_grafik/defuzzifikasi_skenario_5.png`: Grafik implikasi, agregasi MAX, dan posisi Centroid untuk Skenario 5 ($35^\circ\text{C}, 15\%$).

---

## 5. Analisis Hasil

### Pertanyaan 1: Mengapa durasi penyiraman pada kondisi tanah kering seharusnya lebih lama daripada pada kondisi tanah lembap?
**Jawaban**:
Secara biologis dan hidrologis, air di dalam tanah diserap oleh akar tanaman untuk proses fotosintesis dan transpirasi. Pada saat kondisi tanah **kering** (kelembapan $< 30\%$), ketersediaan air bebas (*capillary water*) di dalam pori-pori tanah berada di bawah kapasitas lapang (*field capacity*). Jika penyiraman hanya dilakukan singkat, air hanya akan membasahi lapisan paling atas (*topsoil*) dan cepat menguap sebelum mencapai zona perakaran aktif (*root zone*). Oleh sebab itu, durasi penyiraman harus lebih lama agar debit air kumulatif mencukupi untuk membasahi tanah hingga kedalaman perakaran. Sebaliknya, pada kondisi tanah **lembap** (kelembapan $> 70\%$), pori-pori tanah telah jenuh air. Pemberian air berlebih justru menyebabkan genangan (*waterlogging*), menghambat aerasi oksigen ke akar yang memicu pembusukan akar (*root rot*), dan membuang air secara sia-sia.

### Pertanyaan 2: Bagaimana perubahan membership function dapat memengaruhi hasil defuzzifikasi?
**Jawaban**:
Bentuk dan parameter *membership function* (MF) menentukan:
1. **Derajat keaktifan aturan ($\alpha$-predicate)**: Menggeser titik puncak $b$ atau memperlebar basis $[a, c]$ akan mengubah rentang sensitivitas input terhadap himpunan tertentu. Input yang sama dapat menghasilkan nilai keanggotaan $\mu$ yang lebih besar atau lebih kecil.
2. **Bentuk dan Luas Area Konsekuen yang Terpotong (Implikasi)**: Defuzzifikasi metode Centroid menghitung titik berat bidang agregasi $\frac{\int y \cdot \mu(y) dy}{\int \mu(y) dy}$. Apabila parameter kurva output diubah (misal memperlebar himpunan `Lama`), maka momen inersia/luas area himpunan `Lama` bertambah besar, sehingga titik berat centroid akan ditarik ke arah nilai yang lebih tinggi. Sebaliknya, jika rentang dibuat lebih sempit, perubahan respons output terhadap input akan menjadi lebih agresif atau kaku.

### Pertanyaan 3: Apa yang terjadi apabila suatu kombinasi input tidak mengaktifkan satu pun rule?
**Jawaban**:
Apabila input berada pada area kosong di luar cakupan aturan (*dead zone* atau *blind spot*), maka seluruh $\alpha$-predicate bernilai 0 ($\alpha_i = 0$ untuk seluruh $i$). Akibatnya:
* Fungsi agregasi menghasilkan kurva datar bernilai nol di seluruh semesta pembicaraan: $\mu_{\text{agregasi}}(y) = 0, \forall y$.
* Pada proses defuzzifikasi Centroid, terjadi pembagian dengan nol (*division by zero*):
  $$z^* = \frac{\int y \cdot 0 \, dy}{\int 0 \, dy} = \frac{0}{0} \quad (\text{Indeterminate / NaN})$$
* **Dampak pada sistem fisik**: Aktuator mikrokontroler/PLC akan mengalami kegagalan sistem (*crash/undefined state*) atau katup mati mendadak.
* **Solusi rekayasa yang diterapkan pada program**:
  1. Merancang basis himpunan fuzzy selalu bertumpang tindih (*overlap* $\ge 25\%$).
  2. Menyediakan proteksi *fail-safe* di dalam kode program: jika $\sum \mu = 0$, sistem otomatis mengambil nilai aman rata-rata (*midpoint default*) atau mempertahankan status aman sebelumnya.

### Pertanyaan 4: Apakah hasil sistem selalu meningkat ketika suhu naik? Jelaskan dengan mempertimbangkan kelembapan tanah dan rule base.
**Jawaban**:
**Tidak selalu**. Output durasi penyiraman tidak berbanding lurus hanya terhadap suhu, melainkan ditentukan oleh interaksi multivariabel antara suhu **dan** kelembapan tanah.
* **Contoh Pembuktian dari Tabel Pengujian**:
  * Pada Data No. 5: Suhu $35^\circ\text{C}$ (Panas) dan Kelembapan $15\%$ (Kering) menghasilkan durasi penyiraman **$25.68$ menit**.
  * Namun pada Data No. 9: Suhu $32^\circ\text{C}$ (Panas) tetapi Kelembapan $75\%$ (Lembap) menghasilkan durasi penyiraman hanya **$11.33$ menit**.
  * Bahkan Data No. 8 (Suhu $25^\circ\text{C}$, Kelembapan $15\%$) menghasilkan durasi **$25.74$ menit**, yang **lebih tinggi** daripada Suhu $32^\circ\text{C}$ dengan tanah lembap.
* **Penjelasan Logika Fuzzy**:
  Aturan sistem menetapkan bahwa faktor kelembapan tanah memegang prioritas kendali kritis untuk mencegah kejenuhan air. Sesuai Rule 9 (`IF Suhu PANAS AND Kelembapan LEMBAP THEN Durasi SEDANG`), meskipun suhu sangat panas, jika sensor mendeteksi tanah masih basah, sistem membatasi durasi penyiraman pada kategori Sedang atau Singkat agar tidak terjadi pemborosan air dan kerusakan tanaman. Dengan demikian, peningkatan suhu **hanya akan menaikkan durasi penyiraman jika kondisi tanah juga berada pada status kering atau normal**.
