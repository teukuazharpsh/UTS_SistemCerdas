"""
Modul Visualisasi Grafik Fuzzy Mamdani
- Membership Function (Suhu, Kelembapan, Durasi)
- Grafik Implikasi, Agregasi, dan Centroid
Mata Kuliah: MKP501 Sistem Cerdas
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from fuzzy_system import FuzzySprinklerSystem, trimf

# Konfigurasi style matplotlib
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10


def plot_membership_functions(system: FuzzySprinklerSystem, output_dir="output_grafik"):
    """Menghasilkan grafik Membership Function untuk setiap variabel dan versi gabungan"""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Grafik Suhu
    plt.figure(figsize=(8, 4.5), dpi=300)
    plt.plot(system.suhu_range, trimf(system.suhu_range, system.mf_suhu['dingin']), 'b-', linewidth=2, label='Dingin [0, 0, 20]')
    plt.plot(system.suhu_range, trimf(system.suhu_range, system.mf_suhu['normal']), 'g-', linewidth=2, label='Normal [15, 25, 35]')
    plt.plot(system.suhu_range, trimf(system.suhu_range, system.mf_suhu['panas']), 'r-', linewidth=2, label='Panas [25, 40, 40]')
    plt.title('Fungsi Keanggotaan Variabel Suhu (Input)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Suhu (°C)', fontsize=10)
    plt.ylabel('Derajat Keanggotaan (μ)', fontsize=10)
    plt.ylim(-0.05, 1.05)
    plt.xlim(0, 40)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='center right', frameon=True)
    plt.tight_layout()
    suhu_path = os.path.join(output_dir, 'mf_suhu.png')
    plt.savefig(suhu_path)
    plt.close()

    # 2. Grafik Kelembapan
    plt.figure(figsize=(8, 4.5), dpi=300)
    plt.plot(system.kelembapan_range, trimf(system.kelembapan_range, system.mf_kelembapan['kering']), 'chocolate', linewidth=2, label='Kering [0, 0, 50]')
    plt.plot(system.kelembapan_range, trimf(system.kelembapan_range, system.mf_kelembapan['normal']), 'seagreen', linewidth=2, label='Normal [30, 50, 70]')
    plt.plot(system.kelembapan_range, trimf(system.kelembapan_range, system.mf_kelembapan['lembap']), 'royalblue', linewidth=2, label='Lembap [50, 100, 100]')
    plt.title('Fungsi Keanggotaan Variabel Kelembapan Tanah (Input)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Kelembapan Tanah (%)', fontsize=10)
    plt.ylabel('Derajat Keanggotaan (μ)', fontsize=10)
    plt.ylim(-0.05, 1.05)
    plt.xlim(0, 100)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='center right', frameon=True)
    plt.tight_layout()
    kelembapan_path = os.path.join(output_dir, 'mf_kelembapan.png')
    plt.savefig(kelembapan_path)
    plt.close()

    # 3. Grafik Durasi Penyiraman
    plt.figure(figsize=(8, 4.5), dpi=300)
    plt.plot(system.durasi_range, trimf(system.durasi_range, system.mf_durasi['singkat']), 'teal', linewidth=2, label='Singkat [0, 0, 12]')
    plt.plot(system.durasi_range, trimf(system.durasi_range, system.mf_durasi['sedang']), 'orange', linewidth=2, label='Sedang [8, 15, 22]')
    plt.plot(system.durasi_range, trimf(system.durasi_range, system.mf_durasi['lama']), 'crimson', linewidth=2, label='Lama [18, 30, 30]')
    plt.title('Fungsi Keanggotaan Variabel Durasi Penyiraman (Output)', fontsize=12, fontweight='bold', pad=12)
    plt.xlabel('Durasi Penyiraman (menit)', fontsize=10)
    plt.ylabel('Derajat Keanggotaan (μ)', fontsize=10)
    plt.ylim(-0.05, 1.05)
    plt.xlim(0, 30)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='center right', frameon=True)
    plt.tight_layout()
    durasi_path = os.path.join(output_dir, 'mf_durasi.png')
    plt.savefig(durasi_path)
    plt.close()

    # 4. Grafik Gabungan (3 Subplot untuk Laporan)
    fig, axes = plt.subplots(3, 1, figsize=(9, 10), dpi=300)

    # Subplot Suhu
    axes[0].plot(system.suhu_range, trimf(system.suhu_range, system.mf_suhu['dingin']), 'b-', label='Dingin [0, 0, 20]')
    axes[0].plot(system.suhu_range, trimf(system.suhu_range, system.mf_suhu['normal']), 'g-', label='Normal [15, 25, 35]')
    axes[0].plot(system.suhu_range, trimf(system.suhu_range, system.mf_suhu['panas']), 'r-', label='Panas [25, 40, 40]')
    axes[0].set_title('(a) Variabel Input: Suhu Lingkungan (°C)', fontweight='bold')
    axes[0].set_xlabel('Suhu (°C)')
    axes[0].set_ylabel('μ')
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].legend(loc='upper right')

    # Subplot Kelembapan
    axes[1].plot(system.kelembapan_range, trimf(system.kelembapan_range, system.mf_kelembapan['kering']), 'chocolate', label='Kering [0, 0, 50]')
    axes[1].plot(system.kelembapan_range, trimf(system.kelembapan_range, system.mf_kelembapan['normal']), 'seagreen', label='Normal [30, 50, 70]')
    axes[1].plot(system.kelembapan_range, trimf(system.kelembapan_range, system.mf_kelembapan['lembap']), 'royalblue', label='Lembap [50, 100, 100]')
    axes[1].set_title('(b) Variabel Input: Kelembapan Tanah (%)', fontweight='bold')
    axes[1].set_xlabel('Kelembapan (%)')
    axes[1].set_ylabel('μ')
    axes[1].set_ylim(-0.05, 1.05)
    axes[1].legend(loc='upper right')

    # Subplot Durasi
    axes[2].plot(system.durasi_range, trimf(system.durasi_range, system.mf_durasi['singkat']), 'teal', label='Singkat [0, 0, 12]')
    axes[2].plot(system.durasi_range, trimf(system.durasi_range, system.mf_durasi['sedang']), 'orange', label='Sedang [8, 15, 22]')
    axes[2].plot(system.durasi_range, trimf(system.durasi_range, system.mf_durasi['lama']), 'crimson', label='Lama [18, 30, 30]')
    axes[2].set_title('(c) Variabel Output: Durasi Penyiraman (menit)', fontweight='bold')
    axes[2].set_xlabel('Durasi (menit)')
    axes[2].set_ylabel('μ')
    axes[2].set_ylim(-0.05, 1.05)
    axes[2].legend(loc='upper right')

    plt.suptitle('Desain Fungsi Keanggotaan Segitiga Sistem Cerdas Penyiraman', fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()
    gabungan_path = os.path.join(output_dir, 'grafik_mf_gabungan.png')
    plt.savefig(gabungan_path)
    plt.close()

    print(f"[OK] Grafik MF tersimpan di folder: {output_dir}/")
    return {
        'suhu': suhu_path,
        'kelembapan': kelembapan_path,
        'durasi': durasi_path,
        'gabungan': gabungan_path
    }


def plot_defuzzifikasi_centroid(system: FuzzySprinklerSystem, suhu_val, kelembapan_val, output_dir="output_grafik", filename="defuzzifikasi_centroid.png"):
    """
    Menampilkan dan menyimpan grafik visualisasi proses Fuzzy Mamdani:
    - Kurva potongan masing-masing aturan aktif (implikasi MIN)
    - Area agregasi (operator MAX)
    - Garis posisi defuzzifikasi centroid
    """
    os.makedirs(output_dir, exist_ok=True)
    res = system.compute(suhu_val, kelembapan_val)

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    # Plot kurva MF referensi dengan garis putus-putus
    ax.plot(res['durasi_range'], res['mf_durasi_curves']['singkat'], 'k--', linewidth=1, alpha=0.35, label='MF Singkat')
    ax.plot(res['durasi_range'], res['mf_durasi_curves']['sedang'], 'm--', linewidth=1, alpha=0.35, label='MF Sedang')
    ax.plot(res['durasi_range'], res['mf_durasi_curves']['lama'], 'b--', linewidth=1, alpha=0.35, label='MF Lama')

    # Arsiran kurva hasil agregasi MAX
    ax.fill_between(res['durasi_range'], 0, res['aggregated'], facecolor='orange', alpha=0.55, label='Area Agregasi (MAX)')
    ax.plot(res['durasi_range'], res['aggregated'], color='darkorange', linewidth=2)

    # Garis Centroid
    centroid_val = res['hasil_defuzzifikasi']
    centroid_idx = np.abs(res['durasi_range'] - centroid_val).argmin()
    centroid_height = res['aggregated'][centroid_idx]

    ax.axvline(x=centroid_val, color='red', linestyle='-', linewidth=2.5,
               label=f'Defuzzifikasi Centroid: {centroid_val:.2f} menit')
    ax.scatter([centroid_val], [centroid_height], color='darkred', s=70, zorder=5)

    # Keterangan Firing Strength aturan yang aktif
    active_rules_text = "Aturan Aktif (α > 0):\n"
    active_count = 0
    for r in res['rule_evaluations']:
        if r['alpha'] > 0:
            active_count += 1
            rule_id = r['description'].split(':')[0]
            active_rules_text += f"• {rule_id}: α = {r['alpha']:.2f} ({r['output_label']})\n"
    if active_count == 0:
        active_rules_text += "• Tidak ada aturan aktif"

    ax.text(0.02, 0.95, active_rules_text.strip(),
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='white', edgecolor='gray', alpha=0.9),
            fontsize=9)

    ax.set_title(f'Hasil Agregasi & Defuzzifikasi Centroid (Suhu = {suhu_val}°C, Kelembapan = {kelembapan_val}%)',
                 fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Durasi Penyiraman (menit)', fontsize=10)
    ax.set_ylabel('Derajat Keanggotaan (μ)', fontsize=10)
    ax.set_xlim(0, 30)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    out_file = os.path.join(output_dir, filename)
    plt.savefig(out_file)
    plt.close()

    print(f"[OK] Grafik Agregasi & Centroid tersimpan di: {out_file}")
    return out_file
