"""
Aplikasi GUI: Sistem Cerdas Pengendalian Penyiraman Tanaman (Fuzzy Mamdani)
Mata Kuliah: MKP501 Sistem Cerdas
Mahasiswa  : Teuku Azhar Pasha (NIM: 202406036)
Dosen      : Dr. E. Agung Nugroho, ST., MT
Program Studi: Sarjana Terapan Teknologi Rekayasa Mekatronika (TRM)
Politeknik Enjinering Indorama (PEI)
"""

import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from fuzzy_system import FuzzySprinklerSystem, trimf


# --- PALET WARNA PROFESSIONAL ERGONOMIC SLATE ---
BG_DARK = "#1E222B"          # Background utama jendela
BG_CARD = "#282C37"          # Kontainer / Card background
BG_HEADER = "#161920"        # Header Bar
BG_INPUT = "#1A1D24"         # Background kotak teks isian
TEXT_MAIN = "#F1F5F9"        # Teks utama (putih lembut)
TEXT_MUTED = "#94A3B8"       # Teks keterangan (abu-abu sejuk)
ACCENT_BLUE = "#3B82F6"      # Biru rekayasa
ACCENT_CYAN = "#38BDF8"      # Cyan cerah untuk angka
ACCENT_GREEN = "#10B981"     # Hijau segar untuk output durasi
ACCENT_AMBER = "#F59E0B"     # Amber / oranye untuk centroid & peringatan
BORDER_COLOR = "#334155"     # Border halus
PLOT_BG = "#222630"          # Kanvas plot matplotlib


class FuzzySprinklerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Cerdas Pengendalian Penyiraman Tanaman - Fuzzy Mamdani [PEI TRM]")
        self.geometry("1280 to 820".replace(" to ", "x"))
        self.minsize(1100, 720)
        self.configure(bg=BG_DARK)

        # Inisialisasi Engine Fuzzy
        self.fuzzy_engine = FuzzySprinklerSystem()

        # Variabel Data Input
        self.var_suhu = tk.DoubleVar(value=25.0)
        self.var_kelembapan = tk.DoubleVar(value=50.0)
        self.var_suhu_text = tk.StringVar(value="25.0")
        self.var_kelembapan_text = tk.StringVar(value="50.0")

        # Flag pencegah recursive callback pada sync 2 arah
        self._updating_from_slider = False
        self._updating_from_entry = False

        # Status peringatan clamping
        self.status_suhu_warning = tk.StringVar(value="Dalam Rentang Normal [0 - 40 °C]")
        self.status_kelembapan_warning = tk.StringVar(value="Dalam Rentang Normal [0 - 100 %]")

        # Setup Styling TTK
        self.setup_styles()

        # Buat Komponen Tampilan
        self.create_header()
        self.create_tab_interface()
        self.create_status_bar()

        # Plot awal
        self.update_simulation_live()

    def setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Tab Notebook
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BG_CARD, foreground=TEXT_MUTED,
                             padding=[18, 9], font=("Segoe UI", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", ACCENT_BLUE)],
                       foreground=[("selected", "#FFFFFF")])

        # Treeview (Tabel Pengujian)
        self.style.configure("Treeview",
                             background=BG_CARD,
                             foreground=TEXT_MAIN,
                             fieldbackground=BG_CARD,
                             rowheight=28,
                             font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading",
                             background=BG_HEADER,
                             foreground=TEXT_MAIN,
                             font=("Segoe UI", 9, "bold"),
                             relief="flat")
        self.style.map("Treeview",
                       background=[("selected", ACCENT_BLUE)],
                       foreground=[("selected", "#FFFFFF")])

        # Scrollbar
        self.style.configure("Vertical.TScrollbar", background=BG_CARD, troughcolor=BG_DARK)

    # =========================================================================
    # HEADER BAR (IDENTITAS AKADEMIK MAHASISWA & DOSEN)
    # =========================================================================
    def create_header(self):
        header_frame = tk.Frame(self, bg=BG_HEADER, height=85, relief="flat")
        header_frame.pack(side="top", fill="x")

        # Kontainer Kiri: Judul Mata Kuliah & Kasus
        left_box = tk.Frame(header_frame, bg=BG_HEADER)
        left_box.pack(side="left", padx=20, pady=12)

        lbl_badge = tk.Label(left_box, text="UTS PRAKTEK MKP501 SISTEM CERDAS - SEMESTER 5",
                             bg="#1E293B", fg="#60A5FA", font=("Segoe UI", 8, "bold"),
                             padx=8, pady=2)
        lbl_badge.pack(anchor="w", pady=(0, 3))

        lbl_title = tk.Label(left_box, text="Sistem Cerdas Pengendalian Penyiraman Tanaman (Fuzzy Mamdani)",
                             bg=BG_HEADER, fg=TEXT_MAIN, font=("Segoe UI", 14, "bold"))
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(left_box, text="Dosen Pengampu: Dr. E. Agung Nugroho, ST., MT  |  Metode: Triangular MF & Centroid",
                           bg=BG_HEADER, fg=TEXT_MUTED, font=("Segoe UI", 9))
        lbl_sub.pack(anchor="w")

        # Kontainer Kanan: Profil Mahasiswa
        right_box = tk.Frame(header_frame, bg="#1F2430", highlightbackground=BORDER_COLOR, highlightthickness=1)
        right_box.pack(side="right", padx=20, pady=12)

        inner_box = tk.Frame(right_box, bg="#1F2430", padx=14, pady=6)
        inner_box.pack()

        lbl_mhs_title = tk.Label(inner_box, text="MAHASISWA (NIM GENAP)", bg="#1F2430", fg="#38BDF8", font=("Segoe UI", 8, "bold"))
        lbl_mhs_title.pack(anchor="e")

        lbl_nama = tk.Label(inner_box, text="Teuku Azhar Pasha", bg="#1F2430", fg=TEXT_MAIN, font=("Segoe UI", 11, "bold"))
        lbl_nama.pack(anchor="e")

        lbl_nim = tk.Label(inner_box, text="NIM: 202406036  •  TRM - PEI", bg="#1F2430", fg=TEXT_MUTED, font=("Segoe UI", 9))
        lbl_nim.pack(anchor="e")

    # =========================================================================
    # TAB INTERFACE (NOTEBOOK)
    # =========================================================================
    def create_tab_interface(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        # Tab 1: Simulasi Interaktif & Visualisasi Centroid
        self.tab_simulasi = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_simulasi, text="  ⚡ 1. Simulasi Real-Time & Defuzzifikasi  ")

        # Tab 2: Kurva Membership Function
        self.tab_mf = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_mf, text="  📈 2. Desain Kurva Membership Function  ")

        # Tab 3: Tabel 10 Pengujian
        self.tab_tabel = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_tabel, text="  📋 3. Tabel Pengujian 10 Skenario  ")

        # Tab 4: Rule Base & Analisis Soal UTS
        self.tab_analisis = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_analisis, text="  🧠 4. Rule Base & Analisis Hasil UTS  ")

        # Bangun konten masing-masing tab
        self.build_tab_simulasi()
        self.build_tab_mf()
        self.build_tab_tabel()
        self.build_tab_analisis()

    # =========================================================================
    # TAB 1: SIMULASI REAL-TIME & DEFUZZIFIKASI
    # =========================================================================
    def build_tab_simulasi(self):
        # Layout 2 Kolom (Kiri: Kontrol & Hasil, Kanan: Live Matplotlib Plot)
        container = tk.Frame(self.tab_simulasi, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        left_panel = tk.Frame(container, bg=BG_DARK, width=440)
        left_panel.pack(side="left", fill="y", padx=(0, 8))
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(container, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        right_panel.pack(side="right", fill="both", expand=True)

        # ----------------- PANEL KIRI -----------------
        # 1. Card Input Parameter (Dual Input: Slider + TextBox)
        card_input = tk.Frame(left_panel, bg=BG_CARD, padx=14, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card_input.pack(fill="x", pady=(0, 10))

        lbl_c_title = tk.Label(card_input, text="KONTROL PARAMETER INPUT", bg=BG_CARD, fg="#60A5FA", font=("Segoe UI", 10, "bold"))
        lbl_c_title.pack(anchor="w", pady=(0, 8))

        # --- A. Input Suhu Udara ---
        lbl_s_hdr = tk.Label(card_input, text="🌡️ Suhu Udara Lingkungan (0 - 40 °C):", bg=BG_CARD, fg=TEXT_MAIN, font=("Segoe UI", 9, "bold"))
        lbl_s_hdr.pack(anchor="w")

        row_suhu = tk.Frame(card_input, bg=BG_CARD)
        row_suhu.pack(fill="x", pady=(3, 2))

        self.scale_suhu = tk.Scale(row_suhu, from_=0.0, to=40.0, resolution=0.5, orient="horizontal",
                                   variable=self.var_suhu, bg=BG_CARD, fg=TEXT_MUTED, troughcolor=BG_INPUT,
                                   activebackground=ACCENT_BLUE, highlightthickness=0, showvalue=False,
                                   command=self.on_slider_suhu_change)
        self.scale_suhu.pack(side="left", fill="x", expand=True, padx=(0, 8))

        entry_box_suhu = tk.Frame(row_suhu, bg=BG_INPUT, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=4, pady=2)
        entry_box_suhu.pack(side="right")
        self.entry_suhu = tk.Entry(entry_box_suhu, textvariable=self.var_suhu_text, width=6, bg=BG_INPUT, fg=ACCENT_CYAN,
                                   font=("Segoe UI", 10, "bold"), bd=0, justify="center", insertbackground=TEXT_MAIN)
        self.entry_suhu.pack(side="left")
        lbl_unit_s = tk.Label(entry_box_suhu, text="°C", bg=BG_INPUT, fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_unit_s.pack(side="right", padx=(2, 0))
        self.entry_suhu.bind("<Return>", self.on_entry_suhu_confirm)
        self.entry_suhu.bind("<FocusOut>", self.on_entry_suhu_confirm)

        # Derajat Suhu & Status Clamping
        self.lbl_mu_suhu = tk.Label(card_input, text="Dingin: 0.00 | Normal: 1.00 | Panas: 0.00", bg=BG_CARD, fg=TEXT_MUTED, font=("Consolas", 8))
        self.lbl_mu_suhu.pack(anchor="w", pady=(1, 2))

        self.lbl_warn_suhu = tk.Label(card_input, textvariable=self.status_suhu_warning, bg=BG_CARD, fg="#10B981", font=("Segoe UI", 7))
        self.lbl_warn_suhu.pack(anchor="w", pady=(0, 8))

        # --- B. Input Kelembapan Tanah ---
        lbl_k_hdr = tk.Label(card_input, text="💧 Kelembapan Tanah (0 - 100 %):", bg=BG_CARD, fg=TEXT_MAIN, font=("Segoe UI", 9, "bold"))
        lbl_k_hdr.pack(anchor="w")

        row_kel = tk.Frame(card_input, bg=BG_CARD)
        row_kel.pack(fill="x", pady=(3, 2))

        self.scale_kel = tk.Scale(row_kel, from_=0.0, to=100.0, resolution=1.0, orient="horizontal",
                                  variable=self.var_kelembapan, bg=BG_CARD, fg=TEXT_MUTED, troughcolor=BG_INPUT,
                                  activebackground=ACCENT_BLUE, highlightthickness=0, showvalue=False,
                                  command=self.on_slider_kel_change)
        self.scale_kel.pack(side="left", fill="x", expand=True, padx=(0, 8))

        entry_box_kel = tk.Frame(row_kel, bg=BG_INPUT, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=4, pady=2)
        entry_box_kel.pack(side="right")
        self.entry_kel = tk.Entry(entry_box_kel, textvariable=self.var_kelembapan_text, width=6, bg=BG_INPUT, fg=ACCENT_CYAN,
                                  font=("Segoe UI", 10, "bold"), bd=0, justify="center", insertbackground=TEXT_MAIN)
        self.entry_kel.pack(side="left")
        lbl_unit_k = tk.Label(entry_box_kel, text="%", bg=BG_INPUT, fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_unit_k.pack(side="right", padx=(2, 0))
        self.entry_kel.bind("<Return>", self.on_entry_kel_confirm)
        self.entry_kel.bind("<FocusOut>", self.on_entry_kel_confirm)

        # Derajat Kelembapan & Status Clamping
        self.lbl_mu_kel = tk.Label(card_input, text="Kering: 0.00 | Normal: 1.00 | Lembap: 0.00", bg=BG_CARD, fg=TEXT_MUTED, font=("Consolas", 8))
        self.lbl_mu_kel.pack(anchor="w", pady=(1, 2))

        self.lbl_warn_kel = tk.Label(card_input, textvariable=self.status_kelembapan_warning, bg=BG_CARD, fg="#10B981", font=("Segoe UI", 7))
        self.lbl_warn_kel.pack(anchor="w", pady=(0, 8))

        # Tombol Aksi Input
        btn_row = tk.Frame(card_input, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(2, 0))

        btn_reset = tk.Button(btn_row, text="🔄 Reset Nilai", bg="#334155", fg=TEXT_MAIN, font=("Segoe UI", 8, "bold"),
                              relief="flat", activebackground="#475569", activeforeground="#FFFFFF", cursor="hand2",
                              command=self.reset_default_values, padx=10, pady=4)
        btn_reset.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_save_plot = tk.Button(btn_row, text="💾 Simpan Grafik PNG", bg="#1E3A8A", fg="#93C5FD", font=("Segoe UI", 8, "bold"),
                                  relief="flat", activebackground="#1D4ED8", activeforeground="#FFFFFF", cursor="hand2",
                                  command=self.save_current_plot, padx=10, pady=4)
        btn_save_plot.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # 2. Card Hasil Output Rekomendasi
        card_output = tk.Frame(left_panel, bg=BG_CARD, padx=14, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card_output.pack(fill="x", pady=(0, 10))

        lbl_o_title = tk.Label(card_output, text="HASIL REKOMENDASI SISTEM", bg=BG_CARD, fg="#34D399", font=("Segoe UI", 10, "bold"))
        lbl_o_title.pack(anchor="w", pady=(0, 6))

        # Kotak Durasi Besar
        box_durasi = tk.Frame(card_output, bg="#132E27", highlightbackground="#059669", highlightthickness=1, pady=8)
        box_durasi.pack(fill="x", pady=(0, 6))

        lbl_d_tag = tk.Label(box_durasi, text="DURASI PENYIRAMAN REKOMENDASI", bg="#132E27", fg="#6EE7B7", font=("Segoe UI", 8, "bold"))
        lbl_d_tag.pack()

        self.lbl_durasi_val = tk.Label(box_durasi, text="15.00 MENIT", bg="#132E27", fg="#A7F3D0", font=("Segoe UI", 22, "bold"))
        self.lbl_durasi_val.pack()

        self.lbl_kategori_out = tk.Label(box_durasi, text="Kategori: SEDANG (8 - 22 Menit)", bg="#132E27", fg="#34D399", font=("Segoe UI", 9))
        self.lbl_kategori_out.pack()

        # 3. Card Log Rule Aktif
        card_log = tk.Frame(left_panel, bg=BG_CARD, padx=14, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card_log.pack(fill="both", expand=True)

        lbl_l_title = tk.Label(card_log, text="ATURAN AKTIF (FIRING STRENGTH α > 0)", bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"))
        lbl_l_title.pack(anchor="w", pady=(0, 4))

        self.txt_rules = tk.Text(card_log, bg=BG_INPUT, fg=TEXT_MAIN, font=("Consolas", 8), bd=0, height=8,
                                 highlightbackground=BORDER_COLOR, highlightthickness=1, wrap="word")
        self.txt_rules.pack(fill="both", expand=True)

        # ----------------- PANEL KANAN (CANVAS MATPLOTLIB) -----------------
        self.fig_simulasi = Figure(figsize=(7, 5.2), dpi=100, facecolor=BG_CARD)
        self.ax_simulasi = self.fig_simulasi.add_subplot(111)
        self.ax_simulasi.set_facecolor(PLOT_BG)

        self.canvas_simulasi = FigureCanvasTkAgg(self.fig_simulasi, master=right_panel)
        self.canvas_simulasi.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    # =========================================================================
    # EVENT HANDLERS SINKRONISASI DUA ARAH (TWO-WAY BINDING)
    # =========================================================================
    def on_slider_suhu_change(self, val):
        if self._updating_from_entry:
            return
        self._updating_from_slider = True
        try:
            val_f = float(val)
            self.var_suhu_text.set(f"{val_f:.1f}")
            self.status_suhu_warning.set("Dalam Rentang Normal [0 - 40 °C]")
            self.lbl_warn_suhu.configure(fg="#10B981")
            self.update_simulation_live()
        finally:
            self._updating_from_slider = False

    def on_slider_kel_change(self, val):
        if self._updating_from_entry:
            return
        self._updating_from_slider = True
        try:
            val_f = float(val)
            self.var_kelembapan_text.set(f"{val_f:.1f}")
            self.status_kelembapan_warning.set("Dalam Rentang Normal [0 - 100 %]")
            self.lbl_warn_kel.configure(fg="#10B981")
            self.update_simulation_live()
        finally:
            self._updating_from_slider = False

    def on_entry_suhu_confirm(self, event=None):
        if self._updating_from_slider:
            return
        self._updating_from_entry = True
        raw_str = self.var_suhu_text.get().strip()
        try:
            val = float(raw_str)
            # Analisis saturasi / clamping
            if val < 0.0:
                self.status_suhu_warning.set(f"⚠️ Nilai {val}°C < 0, disaturasi ke 0.0 °C (Safety Clamp)")
                self.lbl_warn_suhu.configure(fg=ACCENT_AMBER)
                val = 0.0
            elif val > 40.0:
                self.status_suhu_warning.set(f"⚠️ Nilai {val}°C > 40, disaturasi ke 40.0 °C (Safety Clamp)")
                self.lbl_warn_suhu.configure(fg=ACCENT_AMBER)
                val = 40.0
            else:
                self.status_suhu_warning.set("Dalam Rentang Normal [0 - 40 °C]")
                self.lbl_warn_suhu.configure(fg="#10B981")

            self.var_suhu.set(val)
            self.var_suhu_text.set(f"{val:.1f}")
            self.update_simulation_live()
        except ValueError:
            messagebox.showwarning("Input Tidak Valid", "Harap masukkan nilai angka numerik untuk Suhu Udara!")
            self.var_suhu_text.set(f"{self.var_suhu.get():.1f}")
        finally:
            self._updating_from_entry = False

    def on_entry_kel_confirm(self, event=None):
        if self._updating_from_slider:
            return
        self._updating_from_entry = True
        raw_str = self.var_kelembapan_text.get().strip()
        try:
            val = float(raw_str)
            # Analisis saturasi / clamping
            if val < 0.0:
                self.status_kelembapan_warning.set(f"⚠️ Nilai {val}% < 0, disaturasi ke 0.0 % (Safety Clamp)")
                self.lbl_warn_kel.configure(fg=ACCENT_AMBER)
                val = 0.0
            elif val > 100.0:
                self.status_kelembapan_warning.set(f"⚠️ Nilai {val}% > 100, disaturasi ke 100.0 % (Safety Clamp)")
                self.lbl_warn_kel.configure(fg=ACCENT_AMBER)
                val = 100.0
            else:
                self.status_kelembapan_warning.set("Dalam Rentang Normal [0 - 100 %]")
                self.lbl_warn_kel.configure(fg="#10B981")

            self.var_kelembapan.set(val)
            self.var_kelembapan_text.set(f"{val:.1f}")
            self.update_simulation_live()
        except ValueError:
            messagebox.showwarning("Input Tidak Valid", "Harap masukkan nilai angka numerik untuk Kelembapan Tanah!")
            self.var_kelembapan_text.set(f"{self.var_kelembapan.get():.1f}")
        finally:
            self._updating_from_entry = False

    def reset_default_values(self):
        self.var_suhu.set(25.0)
        self.var_kelembapan.set(50.0)
        self.var_suhu_text.set("25.0")
        self.var_kelembapan_text.set("50.0")
        self.status_suhu_warning.set("Dalam Rentang Normal [0 - 40 °C]")
        self.status_kelembapan_warning.set("Dalam Rentang Normal [0 - 100 %]")
        self.lbl_warn_suhu.configure(fg="#10B981")
        self.lbl_warn_kel.configure(fg="#10B981")
        self.update_simulation_live()

    # =========================================================================
    # LOGIKA UPDATE SIMULASI & EMBEDDED PLOT
    # =========================================================================
    def update_simulation_live(self):
        suhu = self.var_suhu.get()
        kelembapan = self.var_kelembapan.get()

        res = self.fuzzy_engine.compute(suhu, kelembapan)
        durasi = res['hasil_defuzzifikasi']

        # Update Teks Fuzzifikasi
        mu_s = res['fuzzifikasi']['suhu']
        self.lbl_mu_suhu.configure(text=f"Dingin: {mu_s['dingin']:.2f} | Normal: {mu_s['normal']:.2f} | Panas: {mu_s['panas']:.2f}")

        mu_k = res['fuzzifikasi']['kelembapan']
        self.lbl_mu_kel.configure(text=f"Kering: {mu_k['kering']:.2f} | Normal: {mu_k['normal']:.2f} | Lembap: {mu_k['lembap']:.2f}")

        # Update Durasi & Kategori
        self.lbl_durasi_val.configure(text=f"{durasi:.2f} MENIT")
        if durasi <= 10.0:
            kat = "Kategori: SINGKAT (0 - 12 Menit)"
        elif durasi <= 20.0:
            kat = "Kategori: SEDANG (8 - 22 Menit)"
        else:
            kat = "Kategori: LAMA (18 - 30 Menit)"
        self.lbl_kategori_out.configure(text=kat)

        # Update Text Rules
        self.txt_rules.delete("1.0", tk.END)
        active_found = False
        for r in res['rule_evaluations']:
            if r['alpha'] > 0:
                active_found = True
                rule_tag = r['description'].split(':')[0]
                self.txt_rules.insert(tk.END, f"• {rule_tag}: α={r['alpha']:.3f} -> {r['output_label'].upper()}\n")
                self.txt_rules.insert(tk.END, f"  {r['description'].split(': ')[1]}\n")
        if not active_found:
            self.txt_rules.insert(tk.END, "• Tidak ada aturan yang aktif (Fallback)\n")

        # Render Ulang Matplotlib Plot
        self.render_simulasi_plot(res, suhu, kelembapan)

    def render_simulasi_plot(self, res, suhu, kelembapan):
        self.ax_simulasi.clear()

        x = res['durasi_range']
        agg = res['aggregated']
        centroid = res['hasil_defuzzifikasi']

        # Plot garis referensi tipis
        self.ax_simulasi.plot(x, res['mf_durasi_curves']['singkat'], color='#38BDF8', linestyle=':', linewidth=1.2, alpha=0.45, label='Singkat [0, 0, 12]')
        self.ax_simulasi.plot(x, res['mf_durasi_curves']['sedang'], color='#FBBF24', linestyle=':', linewidth=1.2, alpha=0.45, label='Sedang [8, 15, 22]')
        self.ax_simulasi.plot(x, res['mf_durasi_curves']['lama'], color='#F87171', linestyle=':', linewidth=1.2, alpha=0.45, label='Lama [18, 30, 30]')

        # Arsiran Area Agregasi MAX (Warna oranye hangat lembut)
        self.ax_simulasi.fill_between(x, 0, agg, facecolor='#F59E0B', alpha=0.45, label='Area Agregasi (MAX)')
        self.ax_simulasi.plot(x, agg, color='#D97706', linewidth=2.0)

        # Garis Centroid Merah Tegas
        self.ax_simulasi.axvline(x=centroid, color='#EF4444', linestyle='-', linewidth=2.5,
                                 label=f'Centroid: {centroid:.2f} menit')

        # Titik Centroid Marker
        idx_c = np.abs(x - centroid).argmin()
        c_height = agg[idx_c]
        self.ax_simulasi.scatter([centroid], [c_height], color='#B91C1C', s=75, zorder=6)

        # Styling Axis & Grid untuk Tema Slate
        self.ax_simulasi.set_title(f"Implikasi, Agregasi (MAX) & Defuzzifikasi Centroid  |  Suhu={suhu:.1f}°C, Kelembapan={kelembapan:.1f}%",
                                   color=TEXT_MAIN, fontsize=10, fontweight='bold', pad=10)
        self.ax_simulasi.set_xlabel("Durasi Penyiraman (Menit)", color=TEXT_MUTED, fontsize=9)
        self.ax_simulasi.set_ylabel("Derajat Keanggotaan (μ)", color=TEXT_MUTED, fontsize=9)
        self.ax_simulasi.set_xlim(0, 30)
        self.ax_simulasi.set_ylim(-0.05, 1.05)

        self.ax_simulasi.tick_params(colors=TEXT_MUTED, labelsize=8)
        for spine in self.ax_simulasi.spines.values():
            spine.set_color(BORDER_COLOR)

        self.ax_simulasi.grid(True, linestyle='--', color='#334155', alpha=0.55)
        self.ax_simulasi.legend(loc='upper right', facecolor=BG_CARD, edgecolor=BORDER_COLOR,
                                labelcolor=TEXT_MAIN, fontsize=8, framealpha=0.9)

        self.fig_simulasi.tight_layout()
        self.canvas_simulasi.draw()

    def save_current_plot(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
                                             initialfile=f"defuzzifikasi_suhu_{int(self.var_suhu.get())}_kel_{int(self.var_kelembapan.get())}.png")
        if fpath:
            self.fig_simulasi.savefig(fpath, dpi=300, facecolor=BG_CARD)
            messagebox.showinfo("Berhasil Disimpan", f"Grafik defuzzifikasi berhasil disimpan ke:\n{fpath}")

    # =========================================================================
    # TAB 2: DESAIN KURVA MEMBERSHIP FUNCTION
    # =========================================================================
    def build_tab_mf(self):
        frame = tk.Frame(self.tab_mf, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Canvas Matplotlib 3 Subplot
        fig_mf = Figure(figsize=(10, 6), dpi=100, facecolor=BG_CARD)
        axes = fig_mf.subplots(3, 1)

        sys = self.fuzzy_engine

        # Subplot 1: Suhu
        ax1 = axes[0]
        ax1.set_facecolor(PLOT_BG)
        ax1.plot(sys.suhu_range, trimf(sys.suhu_range, sys.mf_suhu['dingin']), color='#60A5FA', linewidth=2, label='Dingin [0, 0, 20]')
        ax1.plot(sys.suhu_range, trimf(sys.suhu_range, sys.mf_suhu['normal']), color='#34D399', linewidth=2, label='Normal [15, 25, 35]')
        ax1.plot(sys.suhu_range, trimf(sys.suhu_range, sys.mf_suhu['panas']), color='#F87171', linewidth=2, label='Panas [25, 40, 40]')
        ax1.set_title("(a) Variabel Input: Suhu Udara Lingkungan (°C)", color=TEXT_MAIN, fontsize=9, fontweight='bold', pad=4)
        ax1.set_xlim(0, 40)
        ax1.set_ylim(-0.05, 1.05)
        ax1.tick_params(colors=TEXT_MUTED, labelsize=8)
        ax1.grid(True, linestyle='--', color='#334155', alpha=0.5)
        ax1.legend(loc='upper right', facecolor=BG_CARD, edgecolor=BORDER_COLOR, labelcolor=TEXT_MAIN, fontsize=7)
        for sp in ax1.spines.values(): sp.set_color(BORDER_COLOR)

        # Subplot 2: Kelembapan
        ax2 = axes[1]
        ax2.set_facecolor(PLOT_BG)
        ax2.plot(sys.kelembapan_range, trimf(sys.kelembapan_range, sys.mf_kelembapan['kering']), color='#F59E0B', linewidth=2, label='Kering [0, 0, 50]')
        ax2.plot(sys.kelembapan_range, trimf(sys.kelembapan_range, sys.mf_kelembapan['normal']), color='#10B981', linewidth=2, label='Normal [30, 50, 70]')
        ax2.plot(sys.kelembapan_range, trimf(sys.kelembapan_range, sys.mf_kelembapan['lembap']), color='#38BDF8', linewidth=2, label='Lembap [50, 100, 100]')
        ax2.set_title("(b) Variabel Input: Kelembapan Tanah (%)", color=TEXT_MAIN, fontsize=9, fontweight='bold', pad=4)
        ax2.set_xlim(0, 100)
        ax2.set_ylim(-0.05, 1.05)
        ax2.tick_params(colors=TEXT_MUTED, labelsize=8)
        ax2.grid(True, linestyle='--', color='#334155', alpha=0.5)
        ax2.legend(loc='upper right', facecolor=BG_CARD, edgecolor=BORDER_COLOR, labelcolor=TEXT_MAIN, fontsize=7)
        for sp in ax2.spines.values(): sp.set_color(BORDER_COLOR)

        # Subplot 3: Durasi
        ax3 = axes[2]
        ax3.set_facecolor(PLOT_BG)
        ax3.plot(sys.durasi_range, trimf(sys.durasi_range, sys.mf_durasi['singkat']), color='#2DD4BF', linewidth=2, label='Singkat [0, 0, 12]')
        ax3.plot(sys.durasi_range, trimf(sys.durasi_range, sys.mf_durasi['sedang']), color='#FBBF24', linewidth=2, label='Sedang [8, 15, 22]')
        ax3.plot(sys.durasi_range, trimf(sys.durasi_range, sys.mf_durasi['lama']), color='#FB7185', linewidth=2, label='Lama [18, 30, 30]')
        ax3.set_title("(c) Variabel Output: Durasi Penyiraman (Menit)", color=TEXT_MAIN, fontsize=9, fontweight='bold', pad=4)
        ax3.set_xlim(0, 30)
        ax3.set_ylim(-0.05, 1.05)
        ax3.tick_params(colors=TEXT_MUTED, labelsize=8)
        ax3.grid(True, linestyle='--', color='#334155', alpha=0.5)
        ax3.legend(loc='upper right', facecolor=BG_CARD, edgecolor=BORDER_COLOR, labelcolor=TEXT_MAIN, fontsize=7)
        for sp in ax3.spines.values(): sp.set_color(BORDER_COLOR)

        fig_mf.tight_layout()

        canvas_mf = FigureCanvasTkAgg(fig_mf, master=frame)
        canvas_mf.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    # =========================================================================
    # TAB 3: TABEL PENGUJIAN 10 SKENARIO
    # =========================================================================
    def build_tab_tabel(self):
        container = tk.Frame(self.tab_tabel, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Bar Kontrol Tabel
        top_bar = tk.Frame(container, bg=BG_CARD, padx=14, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_bar.pack(fill="x", pady=(0, 10))

        lbl_desc = tk.Label(top_bar, text="Tabel Pengujian 10 Data (5 Data Soal UTS + 5 Data Variasi Mahasiswa)",
                            bg=BG_CARD, fg=TEXT_MAIN, font=("Segoe UI", 10, "bold"))
        lbl_desc.pack(side="left")

        btn_run_all = tk.Button(top_bar, text="▶️ Jalankan Evaluasi Ulang", bg=ACCENT_BLUE, fg="#FFFFFF",
                                font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#2563EB",
                                cursor="hand2", padx=12, pady=4, command=self.populate_test_table)
        btn_run_all.pack(side="right", padx=(6, 0))

        btn_load_selected = tk.Button(top_bar, text="🔍 Tampilkan di Simulasi", bg="#334155", fg=TEXT_MAIN,
                                      font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#475569",
                                      cursor="hand2", padx=12, pady=4, command=self.load_selected_to_simulation)
        btn_load_selected.pack(side="right", padx=(6, 0))

        btn_export = tk.Button(top_bar, text="📥 Ekspor ke CSV", bg="#065F46", fg="#A7F3D0",
                               font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#047857",
                               cursor="hand2", padx=12, pady=4, command=self.export_table_to_csv)
        btn_export.pack(side="right")

        # Treeview Kontainer
        tree_frame = tk.Frame(container, bg=BG_CARD, highlightbackground=BORDER_COLOR, highlightthickness=1)
        tree_frame.pack(fill="both", expand=True)

        columns = ("no", "suhu", "kelembapan", "durasi", "kategori", "keterangan")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("no", text="No")
        self.tree.heading("suhu", text="Suhu (°C)")
        self.tree.heading("kelembapan", text="Kelembapan (%)")
        self.tree.heading("durasi", text="Durasi (Menit)")
        self.tree.heading("kategori", text="Kategori Output")
        self.tree.heading("keterangan", text="Skenario Pengujian")

        self.tree.column("no", width=45, anchor="center")
        self.tree.column("suhu", width=100, anchor="center")
        self.tree.column("kelembapan", width=120, anchor="center")
        self.tree.column("durasi", width=130, anchor="center")
        self.tree.column("kategori", width=130, anchor="center")
        self.tree.column("keterangan", width=380, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.load_selected_to_simulation())

        self.populate_test_table()

    def populate_test_table(self):
        # Bersihkan tabel
        for item in self.tree.get_children():
            self.tree.delete(item)

        from main import DATA_PENGUJIAN
        for d in DATA_PENGUJIAN:
            res = self.fuzzy_engine.compute(d['suhu'], d['kelembapan'])
            durasi = res['hasil_defuzzifikasi']
            if durasi <= 10.0: kat = "Singkat"
            elif durasi <= 20.0: kat = "Sedang"
            else: kat = "Lama"

            self.tree.insert("", "end", values=(
                d['no'],
                f"{d['suhu']:.1f}",
                f"{d['kelembapan']:.1f}",
                f"{durasi:.2f}",
                kat,
                d['keterangan']
            ))

    def load_selected_to_simulation(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Pilih Data", "Silakan klik salah satu baris pengujian pada tabel terlebih dahulu!")
            return
        vals = self.tree.item(sel[0], "values")
        suhu = float(vals[1])
        kelembapan = float(vals[2])

        # Sinkronkan ke tab simulasi
        self.var_suhu.set(suhu)
        self.var_kelembapan.set(kelembapan)
        self.var_suhu_text.set(f"{suhu:.1f}")
        self.var_kelembapan_text.set(f"{kelembapan:.1f}")
        self.update_simulation_live()

        # Buka tab 1
        self.notebook.select(self.tab_simulasi)

    def export_table_to_csv(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")],
                                             initialfile="hasil_pengujian_10_data_uts.csv")
        if not fpath:
            return
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["No", "Suhu (C)", "Kelembapan (%)", "Durasi (Menit)", "Kategori", "Skenario"])
            for child in self.tree.get_children():
                writer.writerow(self.tree.item(child, "values"))
        messagebox.showinfo("Ekspor Berhasil", f"Tabel pengujian berhasil diekspor ke:\n{fpath}")

    # =========================================================================
    # TAB 4: RULE BASE & ANALISIS SOAL UTS
    # =========================================================================
    def build_tab_analisis(self):
        container = tk.Frame(self.tab_analisis, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Split 2 Kolom (Kiri: Matriks 9 Aturan, Kanan: Jawaban 4 Soal UTS)
        left_box = tk.Frame(container, bg=BG_CARD, padx=12, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 6))

        right_box = tk.Frame(container, bg=BG_CARD, padx=12, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        right_box.pack(side="right", fill="both", expand=True, padx=(6, 0))

        # --- Kiri: 9 Rule Base ---
        lbl_r_title = tk.Label(left_box, text="MATRIKS 9 RULE BASE (MAMDANI IF-THEN)", bg=BG_CARD, fg="#60A5FA", font=("Segoe UI", 10, "bold"))
        lbl_r_title.pack(anchor="w", pady=(0, 8))

        txt_r = tk.Text(left_box, bg=BG_INPUT, fg=TEXT_MAIN, font=("Consolas", 9), bd=0, wrap="word",
                        highlightbackground=BORDER_COLOR, highlightthickness=1)
        txt_r.pack(fill="both", expand=True)

        rules_content = """DAFTAR 9 ATURAN FUZZY MAMDANI:
==================================================
R1: IF Suhu DINGIN AND Kelembapan KERING
    THEN Durasi SEDANG
R2: IF Suhu DINGIN AND Kelembapan NORMAL
    THEN Durasi SINGKAT
R3: IF Suhu DINGIN AND Kelembapan LEMBAP
    THEN Durasi SINGKAT
--------------------------------------------------
R4: IF Suhu NORMAL AND Kelembapan KERING
    THEN Durasi LAMA
R5: IF Suhu NORMAL AND Kelembapan NORMAL
    THEN Durasi SEDANG
R6: IF Suhu NORMAL AND Kelembapan LEMBAP
    THEN Durasi SINGKAT
--------------------------------------------------
R7: IF Suhu PANAS  AND Kelembapan KERING
    THEN Durasi LAMA
R8: IF Suhu PANAS  AND Kelembapan NORMAL
    THEN Durasi LAMA
R9: IF Suhu PANAS  AND Kelembapan LEMBAP
    THEN Durasi SEDANG
==================================================
Karakteristik Mekatronika:
• Kelembapan tanah memegang prioritas kendali kritis.
• Ketika tanah LEMBAP, durasi penyiraman selalu
  dibatasi pada level SINGKAT atau SEDANG demi
  mencegah kejenuhan air dan pembusukan akar.
"""
        txt_r.insert(tk.END, rules_content)
        txt_r.configure(state="disabled")

        # --- Kanan: Jawaban Pertanyaan Analisis UTS ---
        lbl_a_title = tk.Label(right_box, text="JAWABAN 4 PERTANYAAN ANALISIS SOAL UTS", bg=BG_CARD, fg="#34D399", font=("Segoe UI", 10, "bold"))
        lbl_a_title.pack(anchor="w", pady=(0, 8))

        txt_a = tk.Text(right_box, bg=BG_INPUT, fg=TEXT_MAIN, font=("Segoe UI", 9), bd=0, wrap="word",
                        highlightbackground=BORDER_COLOR, highlightthickness=1)
        txt_a.pack(fill="both", expand=True)

        analisis_content = """1. Mengapa tanah kering durasi lebih lama daripada tanah lembap?
Jawab:
Pada kondisi kering (kelembapan < 30%), kadar air berada di bawah kapasitas lapang. Air perlu waktu lebih lama agar meresap hingga zona perakaran aktif (root zone) dan tidak sekadar membasahi permukaan tanah yang cepat menguap. Sebaliknya, tanah lembap telah jenuh; penyiraman berlebih memicu genangan air (waterlogging) dan pembusukan akar (root rot).

2. Bagaimana perubahan membership function memengaruhi defuzzifikasi?
Jawab:
• Menggeser titik puncak atau memperlebar basis segitiga mengubah derajat keaktifan firing strength (α).
• Luas area konsekuen yang terpotong ikut berubah. Karena centroid menghitung titik berat bidang z* = ∫(y·μ)dy / ∫μ dy, semakin besar luas area himpunan 'Lama', maka nilai defuzzifikasi akan semakin terdorong ke durasi yang lebih lama.

3. Apa yang terjadi jika suatu kombinasi input tidak memicu rule apapun?
Jawab:
Seluruh α = 0, sehingga kurva agregasi datar pada nol (μ_agg = 0). Terjadi pembagian dengan nol (0/0 = indeterminate/NaN) pada centroid. Pada sistem fisik nyata, ini menyebabkan aktuator mengalami crash/undefined state. Di program ini dicegah dengan:
(1) Overlap MF minimal 25% (tanpa blind spot).
(2) Proteksi fallback default nilai aman.

4. Apakah hasil sistem selalu meningkat ketika suhu naik?
Jawab:
TIDAK SELALU. Durasi penyiraman adalah fungsi multivariabel antara suhu dan kelembapan.
Contoh bukti pengujian:
• Suhu 35°C & Kelembapan 15% -> Durasi: 25.68 Menit (Lama)
• Suhu 32°C & Kelembapan 75% -> Durasi: 11.33 Menit (Sedang)
Meskipun suhu tinggi, jika tanah lembap, sistem memprioritaskan efisiensi air (Rule 9).
"""
        txt_a.insert(tk.END, analisis_content)
        txt_a.configure(state="disabled")

    # =========================================================================
    # STATUS BAR
    # =========================================================================
    def create_status_bar(self):
        status_bar = tk.Frame(self, bg=BG_HEADER, height=28)
        status_bar.pack(side="bottom", fill="x")

        lbl_s_left = tk.Label(status_bar, text="● Sistem Aktif  |  Metode: Mamdani (Triangular MF - MIN - MAX - Centroid COG)",
                              bg=BG_HEADER, fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_s_left.pack(side="left", padx=16, pady=3)

        lbl_s_right = tk.Label(status_bar, text="Politeknik Enjinering Indorama (PEI) - TRM 2026/2027",
                               bg=BG_HEADER, fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_s_right.pack(side="right", padx=16, pady=3)


if __name__ == "__main__":
    app = FuzzySprinklerGUI()
    app.mainloop()
