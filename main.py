"""
Aplikasi Utama: Sistem Cerdas Pengendalian Penyiraman Tanaman (Fuzzy Mamdani)
Mata Kuliah: MKP501 Sistem Cerdas
NIM GENAP - Semester 5 TRM - Politeknik Enjinering Indorama
"""

import sys
import os
from fuzzy_system import FuzzySprinklerSystem
from visualizer import plot_membership_functions, plot_defuzzifikasi_centroid


# 10 Data Pengujian (5 Data Soal + 5 Variasi Mahasiswa)
DATA_PENGUJIAN = [
    # Data dari lembar soal
    {"no": 1, "suhu": 15.0, "kelembapan": 20.0, "keterangan": "Soal 1: Suhu Dingin, Tanah Kering"},
    {"no": 2, "suhu": 20.0, "kelembapan": 30.0, "keterangan": "Soal 2: Suhu Dingin-Normal, Tanah Kering-Normal"},
    {"no": 3, "suhu": 25.0, "kelembapan": 50.0, "keterangan": "Soal 3: Suhu Normal, Tanah Normal"},
    {"no": 4, "suhu": 30.0, "kelembapan": 25.0, "keterangan": "Soal 4: Suhu Normal-Panas, Tanah Kering"},
    {"no": 5, "suhu": 35.0, "kelembapan": 15.0, "keterangan": "Soal 5: Suhu Panas, Tanah Kering"},
    # 5 Variasi Mahasiswa
    {"no": 6, "suhu": 10.0, "kelembapan": 85.0, "keterangan": "Variasi 1: Suhu Dingin, Tanah Lembap"},
    {"no": 7, "suhu": 38.0, "kelembapan": 10.0, "keterangan": "Variasi 2: Suhu Sangat Panas, Tanah Sangat Kering"},
    {"no": 8, "suhu": 25.0, "kelembapan": 15.0, "keterangan": "Variasi 3: Suhu Normal, Tanah Kering"},
    {"no": 9, "suhu": 32.0, "kelembapan": 75.0, "keterangan": "Variasi 4: Suhu Panas, Tanah Lembap"},
    {"no": 10, "suhu": 18.0, "kelembapan": 55.0, "keterangan": "Variasi 5: Suhu Dingin-Normal, Tanah Normal"}
]


def print_header():
    print("=" * 70)
    print("  SISTEM CERDAS PENGENDALIAN PENYIRAMAN TANAMAN (FUZZY MAMDANI)")
    print("  Mata Kuliah: MKP501 Sistem Cerdas | NIM GENAP")
    print("=" * 70)


def hitung_interaktif(system: FuzzySprinklerSystem):
    print("\n--- 1. Perhitungan Interaktif ---")
    try:
        suhu_str = input("Masukkan Suhu Udara (0 - 40 °C): ").strip()
        kelembapan_str = input("Masukkan Kelembapan Tanah (0 - 100 %): ").strip()

        suhu = float(suhu_str)
        kelembapan = float(kelembapan_str)
    except ValueError:
        print("[Error] Harap masukkan nilai numerik yang valid!")
        return

    res = system.compute(suhu, kelembapan)

    print("\n" + "-" * 50)
    print("HASIL TAHAPAN INFERENSI FUZZY MAMDANI")
    print("-" * 50)
    print(f"Input Suhu       : {res['input']['suhu']} °C")
    print(f"Input Kelembapan : {res['input']['kelembapan']} %")

    print("\n1. Derajat Keanggotaan (Fuzzifikasi):")
    print(f"   • Suhu Dingin  : {res['fuzzifikasi']['suhu']['dingin']:.4f}")
    print(f"   • Suhu Normal  : {res['fuzzifikasi']['suhu']['normal']:.4f}")
    print(f"   • Suhu Panas   : {res['fuzzifikasi']['suhu']['panas']:.4f}")
    print(f"   • Kelembapan Kering  : {res['fuzzifikasi']['kelembapan']['kering']:.4f}")
    print(f"   • Kelembapan Normal  : {res['fuzzifikasi']['kelembapan']['normal']:.4f}")
    print(f"   • Kelembapan Lembap  : {res['fuzzifikasi']['kelembapan']['lembap']:.4f}")

    print("\n2. Evaluasi Aturan (Firing Strength α):")
    aktif = False
    for r in res['rule_evaluations']:
        if r['alpha'] > 0:
            aktif = True
            print(f"   • {r['description']} => alpha = {r['alpha']:.4f}")
    if not aktif:
        print("   • Tidak ada aturan yang aktif (alpha = 0).")

    print("\n3. Hasil Defuzzifikasi (Centroid):")
    print(f"   >>> Durasi Penyiraman Rekomendasi: {res['hasil_defuzzifikasi']:.2f} menit <<<")
    print("-" * 50)

    # Simpan grafik untuk pengujian ini
    simpan = input("Apakah Anda ingin menyimpan grafik centroid untuk kasus ini? (y/n): ").strip().lower()
    if simpan == 'y':
        fname = f"defuzzifikasi_suhu_{int(suhu)}_kel_{int(kelembapan)}.png"
        path = plot_defuzzifikasi_centroid(system, suhu, kelembapan, filename=fname)
        print(f"Grafik disimpan di: {path}")


def jalankan_tabel_pengujian(system: FuzzySprinklerSystem):
    print("\n" + "=" * 80)
    print("TABEL PENGUJIAN 10 KOMBINASI DATA INPUT")
    print("=" * 80)
    header = f"| {'No':<3} | {'Suhu (°C)':<10} | {'Kelembapan (%)':<15} | {'Durasi (menit)':<16} | {'Keterangan Kasus':<30} |"
    sep = "+" + "-" * 5 + "+" + "-" * 12 + "+" + "-" * 17 + "+" + "-" * 18 + "+" + "-" * 32 + "+"

    print(sep)
    print(header)
    print(sep)

    hasil_tabel = []
    for item in DATA_PENGUJIAN:
        res = system.compute(item['suhu'], item['kelembapan'])
        durasi = res['hasil_defuzzifikasi']
        hasil_tabel.append({
            'no': item['no'],
            'suhu': item['suhu'],
            'kelembapan': item['kelembapan'],
            'durasi': durasi,
            'keterangan': item['keterangan']
        })
        row = f"| {item['no']:<3} | {item['suhu']:<10.1f} | {item['kelembapan']:<15.1f} | {durasi:<16.2f} | {item['keterangan']:<30} |"
        print(row)

    print(sep)

    # Buat grafik agregasi dan centroid untuk skenario 1 (Sesuai ketentuan soal nomor 4)
    print("\nMenghasilkan grafik agregasi & posisi centroid untuk Skenario 1 (Suhu 15°C, Kelembapan 20%)...")
    plot_defuzzifikasi_centroid(system, 15.0, 20.0, filename="defuzzifikasi_skenario_1.png")
    # Juga skenario 5 (kondisi panas & kering) untuk perbandingan
    plot_defuzzifikasi_centroid(system, 35.0, 15.0, filename="defuzzifikasi_skenario_5.png")

    return hasil_tabel


def menu():
    system = FuzzySprinklerSystem()

    while True:
        print_header()
        print("PILIHAN MENU:")
        print("1. Hitung Durasi Penyiraman (Input Interaktif)")
        print("2. Tampilkan Tabel Pengujian 10 Data & Generate Grafik Skenario")
        print("3. Generate Seluruh Grafik Membership Function")
        print("4. Jalankan Semua (Grafik, Pengujian 10 Data, dan Verifikasi)")
        print("5. Buka Aplikasi Desktop GUI (Graphical User Interface)")
        print("0. Keluar")
        print("=" * 70)

        pilihan = input("Pilih menu (0-5): ").strip()
        if pilihan == '1':
            hitung_interaktif(system)
        elif pilihan == '2':
            jalankan_tabel_pengujian(system)
        elif pilihan == '3':
            plot_membership_functions(system)
        elif pilihan == '4':
            print("\n[PROSES] Membuat semua grafik Membership Function...")
            plot_membership_functions(system)
            print("\n[PROSES] Menjalankan pengujian 10 data...")
            jalankan_tabel_pengujian(system)
            print("\n[SELESAI] Semua proses telah dieksekusi dengan sukses!")
        elif pilihan == '5':
            print("\n[PROSES] Membuka Aplikasi Desktop GUI...")
            from gui_app import ModernFuzzySprinklerApp
            app = ModernFuzzySprinklerApp()
            app.mainloop()
        elif pilihan == '0':
            print("Terima kasih. Program selesai.")
            break
        else:
            print("[Perhatian] Pilihan menu tidak valid. Silakan coba lagi.")

        input("\nTekan Enter untuk melanjutkan...")


if __name__ == '__main__':
    menu()
