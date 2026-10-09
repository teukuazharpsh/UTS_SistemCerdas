"""
Aplikasi Desktop Modern: Sistem Cerdas Pengendalian Penyiraman Tanaman (Fuzzy Mamdani)
Desain: Ultra-Modern Dark Dashboard (Matte Obsidian & Electric Lime Accent)
Mata Kuliah : MKP501 Sistem Cerdas
Mahasiswa   : Teuku Azhar Pasha (NIM: 202406036)
Dosen       : Dr. E. Agung Nugroho, ST., MT
Prodi       : Sarjana Terapan Teknologi Rekayasa Mekatronika (TRM)
Institusi   : Politeknik Enjinering Indorama (PEI)
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


# =============================================================================
# PALET WARNA SESUAI GAMBAR REFERENSI (MODLY / ULTRA-MODERN DARK MINIMALIST)
# =============================================================================
COLOR_BG_APP     = "#18191D"      # Matte Obsidian Black (Latar Utama)
COLOR_CARD       = "#22242A"      # Soft Charcoal Graphite (Permukaan Kartu)
COLOR_CARD_HOVER = "#2A2C34"      # Hover state kartu/tombol
COLOR_SIDEBAR    = "#141518"      # Sidebar Kiri Lebih Gelap
COLOR_INPUT_BOX  = "#1A1B20"      # Kotak isian Text Box
COLOR_BORDER     = "#2E313A"      # Garis batas ultra-halus (subtle border)

# ACCENT COLORS (DISIPLIN & MINIMALIS)
ACCENT_LIME      = "#D2F83A"      # Electric Lime / Neon Chartreuse (Signature Accent)
ACCENT_LIME_DARK = "#9EBE1D"      # Versi lebih redup untuk border/teks halus
ACCENT_PURPLE    = "#A78BFA"      # Soft Lavender untuk kurva implikasi
ACCENT_ROSE      = "#F472B6"      # Soft Rose untuk kurva pelengkap
ACCENT_AMBER     = "#FBBF24"      # Soft Amber untuk warning/agregasi

# TYPOGRAPHY COLORS
TEXT_WHITE       = "#FFFFFF"      # Putih bersih untuk nilai data utama / judul
TEXT_MUTED       = "#8E92A0"      # Abu-abu sejuk untuk label & deskripsi
TEXT_DARK        = "#141518"      # Teks gelap di atas tombol lime


class ModernFuzzySprinklerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AgroFuzzy - Smart Irrigation Control System [PEI TRM]")
        self.geometry("1300x820")
        self.minsize(1150, 720)
        self.configure(bg=COLOR_BG_APP)

        # Inisialisasi Engine Fuzzy
        self.fuzzy_engine = FuzzySprinklerSystem()

        # Variabel Parameter Input
        self.var_suhu = tk.DoubleVar(value=25.0)
        self.var_kelembapan = tk.DoubleVar(value=50.0)
        self.var_suhu_text = tk.StringVar(value="25.0")
        self.var_kelembapan_text = tk.StringVar(value="50.0")

        # Flags Sinkronisasi 2 Arah
        self._sync_lock = False

        # Status Peringatan Batas Input (Safety Clamp)
        self.status_suhu_clamp = tk.StringVar(value="Rentang Normal (0 – 40 °C)")
        self.status_kel_clamp = tk.StringVar(value="Rentang Normal (0 – 100 %)")

        # Konfigurasi Styling TTK
        self.setup_ttk_styles()

        # Layout Utama: Sidebar Kiri & Konten Kanan
        self.create_sidebar()
        self.create_main_content()

        # Buka Halaman Utama (Simulasi)
        self.nav_buttons = {}
        self.register_nav_buttons()
        self.switch_view("simulasi")

        # Eksekusi Render Awal
        self.update_simulation_live()

    def setup_ttk_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Treeview (Tabel Pengujian)
        self.style.configure("Treeview",
                             background=COLOR_CARD,
                             foreground=TEXT_WHITE,
                             fieldbackground=COLOR_CARD,
                             rowheight=32,
                             font=("Segoe UI", 9),
                             borderwidth=0)
        self.style.configure("Treeview.Heading",
                             background="#1A1B20",
                             foreground=TEXT_MUTED,
                             font=("Segoe UI", 9, "bold"),
                             relief="flat")
        self.style.map("Treeview",
                       background=[("selected", "#2F323C")],
                       foreground=[("selected", ACCENT_LIME)])

        # Scrollbar
        self.style.configure("Vertical.TScrollbar", background=COLOR_CARD, troughcolor=COLOR_BG_APP, borderwidth=0)

    # =========================================================================
    # SIDEBAR KIRI (SEPERTI GAMBAR: LOGO, INFO DOSEN, PROFIL MAHASISWA, MENU)
    # =========================================================================
    def create_sidebar(self):
        self.sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 1. Logo / Branding Aplikasi (Gaya "Modly")
        logo_box = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR, padx=22, pady=18)
        logo_box.pack(fill="x")

        lbl_logo = tk.Label(logo_box, text="🌱 AgroFuzzy", bg=COLOR_SIDEBAR, fg=ACCENT_LIME,
                            font=("Segoe UI", 16, "bold"))
        lbl_logo.pack(anchor="w")

        lbl_sublogo = tk.Label(logo_box, text="Intelligent Sprinkler Control", bg=COLOR_SIDEBAR,
                              fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_sublogo.pack(anchor="w", pady=(2, 0))

        # 2. Kotak Dosen Pengampu & Mata Kuliah (BERADA DI ATAS KOTAK NAMA)
        dosen_card = tk.Frame(self.sidebar, bg=COLOR_CARD, padx=14, pady=12,
                              highlightbackground=COLOR_BORDER, highlightthickness=1)
        dosen_card.pack(fill="x", padx=16, pady=(0, 10))

        lbl_dosen_tag = tk.Label(dosen_card, text="DOSEN PENGAMPU & MATA KULIAH", bg=COLOR_CARD, fg="#94A3B8",
                                 font=("Segoe UI", 8, "bold"))
        lbl_dosen_tag.pack(anchor="w")

        lbl_dosen_name = tk.Label(dosen_card, text="Dr. E. Agung Nugroho, ST., MT", bg=COLOR_CARD,
                                  fg=TEXT_WHITE, font=("Segoe UI", 11, "bold"))
        lbl_dosen_name.pack(anchor="w", pady=(2, 2))

        lbl_mk = tk.Label(dosen_card, text="MKP501 Sistem Cerdas • Sem 5", bg=COLOR_CARD,
                          fg=ACCENT_LIME, font=("Segoe UI", 9.5, "bold"))
        lbl_mk.pack(anchor="w")

        # 3. User Profile Card (Teuku Azhar Pasha - BERADA DI BAWAH KOTAK DOSEN)
        user_card = tk.Frame(self.sidebar, bg=COLOR_CARD, padx=14, pady=12,
                             highlightbackground=COLOR_BORDER, highlightthickness=1)
        user_card.pack(fill="x", padx=16, pady=(0, 16))

        # Avatar Box (Inisial Elegan)
        avatar_box = tk.Frame(user_card, bg="#1A1B20", width=42, height=42,
                              highlightbackground=ACCENT_LIME, highlightthickness=1)
        avatar_box.pack(side="left", padx=(0, 10))
        avatar_box.pack_propagate(False)
        lbl_avatar = tk.Label(avatar_box, text="TAP", bg="#1A1B20", fg=ACCENT_LIME,
                              font=("Segoe UI", 10, "bold"))
        lbl_avatar.pack(expand=True)

        user_info = tk.Frame(user_card, bg=COLOR_CARD)
        user_info.pack(side="left", fill="x", expand=True)

        lbl_nama = tk.Label(user_info, text="Teuku Azhar Pasha", bg=COLOR_CARD, fg=TEXT_WHITE,
                            font=("Segoe UI", 11, "bold"))
        lbl_nama.pack(anchor="w")

        lbl_nim = tk.Label(user_info, text="NIM: 202406036 (Genap)", bg=COLOR_CARD, fg="#F1F5F9",
                           font=("Segoe UI", 10, "bold"))
        lbl_nim.pack(anchor="w", pady=(1, 1))

        lbl_prodi = tk.Label(user_info, text="TRM • PEI Purwakarta", bg=COLOR_CARD,
                             fg=ACCENT_LIME, font=("Segoe UI", 8.5, "bold"))
        lbl_prodi.pack(anchor="w")

        # 4. Navigasi Vertikal (Pill Menu)
        self.nav_container = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR, padx=12)
        self.nav_container.pack(fill="x")

        # Footer Sederhana di Bawah Sidebar
        footer_box = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR, padx=16, pady=12)
        footer_box.pack(side="bottom", fill="x")
        lbl_foot = tk.Label(footer_box, text="PEI Mechatronics 2026/2027", bg=COLOR_SIDEBAR,
                            fg="#474B57", font=("Segoe UI", 8))
        lbl_foot.pack(anchor="center")

    def register_nav_buttons(self):
        menu_items = [
            ("simulasi",  "⚡  Simulasi Real-Time"),
            ("kurva_mf",  "📈  Kurva Membership"),
            ("tabel_uji", "📋  Tabel Pengujian"),
            ("analisis",  "🧠  Rule Base & Analisis")
        ]

        for view_key, title in menu_items:
            btn = tk.Button(self.nav_container, text=title, anchor="w", padx=16, pady=10,
                            bg=COLOR_SIDEBAR, fg=TEXT_MUTED, font=("Segoe UI", 9, "bold"),
                            relief="flat", activebackground=COLOR_CARD, activeforeground=TEXT_WHITE,
                            cursor="hand2", bd=0, command=lambda k=view_key: self.switch_view(k))
            btn.pack(fill="x", pady=3)
            self.nav_buttons[view_key] = btn

    def switch_view(self, target_key):
        # Update styling tombol nav (Active state pill lime)
        for k, btn in self.nav_buttons.items():
            if k == target_key:
                btn.configure(bg=COLOR_CARD, fg=ACCENT_LIME)
            else:
                btn.configure(bg=COLOR_SIDEBAR, fg=TEXT_MUTED)

        # Ganti tampilan di content area
        for frame in [self.view_simulasi, self.view_mf, self.view_tabel, self.view_analisis]:
            frame.pack_forget()

        if target_key == "simulasi":
            self.lbl_page_title.configure(text="Simulasi & Monitoring Kendali")
            self.lbl_page_subtitle.configure(text="Pengaturan parameter input suhu dan kelembapan secara interaktif")
            self.view_simulasi.pack(fill="both", expand=True)
            self.update_simulation_live()
        elif target_key == "kurva_mf":
            self.lbl_page_title.configure(text="Desain Fungsi Keanggotaan (Membership Functions)")
            self.lbl_page_subtitle.configure(text="Visualisasi kurva segitiga untuk Suhu, Kelembapan Tanah, dan Durasi Penyiraman")
            self.view_mf.pack(fill="both", expand=True)
        elif target_key == "tabel_uji":
            self.lbl_page_title.configure(text="Evaluasi Tabel Pengujian")
            self.lbl_page_subtitle.configure(text="Daftar skenario pengujian UTS dan data interaktif yang ditambahkan")
            self.view_tabel.pack(fill="both", expand=True)
        elif target_key == "analisis":
            self.lbl_page_title.configure(text="Matriks 9 Rule Base & Jawaban Analisis UTS")
            self.lbl_page_subtitle.configure(text="Logika inferensi mekatronika dan jawaban atas 4 pertanyaan evaluasi")
            self.view_analisis.pack(fill="both", expand=True)

    # =========================================================================
    # MAIN CONTENT AREA (HEADER TOP BAR & CONTAINER)
    # =========================================================================
    def create_main_content(self):
        self.main_area = tk.Frame(self, bg=COLOR_BG_APP)
        self.main_area.pack(side="right", fill="both", expand=True, padx=24, pady=20)

        # Top Header Bar (Judul Halaman + Tombol Aksi Kanan seperti 'Upgrade' di gambar)
        top_bar = tk.Frame(self.main_area, bg=COLOR_BG_APP)
        top_bar.pack(fill="x", pady=(0, 16))

        title_box = tk.Frame(top_bar, bg=COLOR_BG_APP)
        title_box.pack(side="left")

        self.lbl_page_title = tk.Label(title_box, text="Simulasi & Monitoring Kendali", bg=COLOR_BG_APP,
                                       fg=TEXT_WHITE, font=("Segoe UI", 16, "bold"))
        self.lbl_page_title.pack(anchor="w")

        self.lbl_page_subtitle = tk.Label(title_box, text="Pengaturan parameter input suhu dan kelembapan secara interaktif",
                                          bg=COLOR_BG_APP, fg=TEXT_MUTED, font=("Segoe UI", 9))
        self.lbl_page_subtitle.pack(anchor="w", pady=(2, 0))

        # Tombol Aksi Kanan (Pill Button Aksen Electric Lime)
        action_box = tk.Frame(top_bar, bg=COLOR_BG_APP)
        action_box.pack(side="right")

        btn_save_plot = tk.Button(action_box, text="💾  Simpan Grafik", bg=ACCENT_LIME, fg=TEXT_DARK,
                                  font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#BCE62C",
                                  cursor="hand2", padx=16, pady=6, bd=0, command=self.save_current_plot)
        btn_save_plot.pack(side="right", padx=(8, 0))

        btn_reset = tk.Button(action_box, text="🔄  Reset Default", bg=COLOR_CARD, fg=TEXT_WHITE,
                              font=("Segoe UI", 9, "bold"), relief="flat", activebackground=COLOR_CARD_HOVER,
                              cursor="hand2", padx=14, pady=6, bd=0, highlightbackground=COLOR_BORDER,
                              highlightthickness=1, command=self.reset_default_values)
        btn_reset.pack(side="right")

        # Kontainer Halaman Dinamis
        self.content_container = tk.Frame(self.main_area, bg=COLOR_BG_APP)
        self.content_container.pack(fill="both", expand=True)

        self.view_simulasi = tk.Frame(self.content_container, bg=COLOR_BG_APP)
        self.view_mf = tk.Frame(self.content_container, bg=COLOR_BG_APP)
        self.view_tabel = tk.Frame(self.content_container, bg=COLOR_BG_APP)
        self.view_analisis = tk.Frame(self.content_container, bg=COLOR_BG_APP)

        self.build_view_simulasi()
        self.build_view_mf()
        self.build_view_tabel()
        self.build_view_analisis()

    # =========================================================================
    # VIEW 1: SIMULASI REAL-TIME (CARD GRID LAYOUT SEPERTI GAMBAR REFERENSI)
    # =========================================================================
    def build_view_simulasi(self):
        # Grid 2 Kolom: Kiri (Kontrol Input & Status Angka Besar), Kanan (Live Plot & Log Rules)
        col_left = tk.Frame(self.view_simulasi, bg=COLOR_BG_APP, width=380)
        col_left.pack(side="left", fill="y", padx=(0, 14))
        col_left.pack_propagate(False)

        col_right = tk.Frame(self.view_simulasi, bg=COLOR_BG_APP)
        col_right.pack(side="right", fill="both", expand=True)

        # ----------------- KOLOM KIRI -----------------
        # CARD 1: KONTROL PARAMETER INPUT (DUAL INPUT SLIDER + ENTRY)
        card_input = tk.Frame(col_left, bg=COLOR_CARD, padx=18, pady=18,
                              highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_input.pack(fill="x", pady=(0, 14))

        lbl_ci_head = tk.Label(card_input, text="Kontrol Parameter Input", bg=COLOR_CARD, fg=TEXT_WHITE,
                               font=("Segoe UI", 11, "bold"))
        lbl_ci_head.pack(anchor="w", pady=(0, 14))

        # --- A. Suhu Udara ---
        lbl_s_tag = tk.Label(card_input, text="Suhu Lingkungan (°C)", bg=COLOR_CARD, fg=TEXT_MUTED,
                             font=("Segoe UI", 9, "bold"))
        lbl_s_tag.pack(anchor="w")

        row_s = tk.Frame(card_input, bg=COLOR_CARD)
        row_s.pack(fill="x", pady=(6, 2))

        self.scale_suhu = tk.Scale(row_s, from_=0.0, to=40.0, resolution=0.5, orient="horizontal",
                                   variable=self.var_suhu, bg=COLOR_CARD, fg=TEXT_MUTED, troughcolor=COLOR_INPUT_BOX,
                                   activebackground=ACCENT_LIME, highlightthickness=0, bd=0, showvalue=False,
                                   command=self.on_slider_suhu_change)
        self.scale_suhu.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Text Box Entry Suhu
        box_entry_s = tk.Frame(row_s, bg=COLOR_INPUT_BOX, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=6, pady=3)
        box_entry_s.pack(side="right")
        self.entry_suhu = tk.Entry(box_entry_s, textvariable=self.var_suhu_text, width=5, bg=COLOR_INPUT_BOX,
                                   fg=ACCENT_LIME, font=("Segoe UI", 10, "bold"), bd=0, justify="center",
                                   insertbackground=TEXT_WHITE)
        self.entry_suhu.pack(side="left")
        lbl_unit_s = tk.Label(box_entry_s, text="°C", bg=COLOR_INPUT_BOX, fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_unit_s.pack(side="right", padx=(2, 0))
        self.entry_suhu.bind("<Return>", self.on_entry_suhu_confirm)
        self.entry_suhu.bind("<FocusOut>", self.on_entry_suhu_confirm)

        # Status & Derajat Suhu (Font Diperbesar & Kontras Tinggi)
        self.lbl_mu_suhu = tk.Label(card_input, text="Dingin: 0.00 | Normal: 1.00 | Panas: 0.00", bg=COLOR_CARD,
                                    fg="#CBD5E1", font=("Segoe UI", 9))
        self.lbl_mu_suhu.pack(anchor="w", pady=(3, 1))

        self.lbl_warn_suhu = tk.Label(card_input, textvariable=self.status_suhu_clamp, bg=COLOR_CARD,
                                      fg="#A3E635", font=("Segoe UI", 9, "bold"))
        self.lbl_warn_suhu.pack(anchor="w", pady=(0, 12))

        # --- B. Kelembapan Tanah ---
        lbl_k_tag = tk.Label(card_input, text="Kelembapan Tanah (%)", bg=COLOR_CARD, fg=TEXT_MUTED,
                             font=("Segoe UI", 9, "bold"))
        lbl_k_tag.pack(anchor="w")

        row_k = tk.Frame(card_input, bg=COLOR_CARD)
        row_k.pack(fill="x", pady=(6, 2))

        self.scale_kel = tk.Scale(row_k, from_=0.0, to=100.0, resolution=1.0, orient="horizontal",
                                  variable=self.var_kelembapan, bg=COLOR_CARD, fg=TEXT_MUTED, troughcolor=COLOR_INPUT_BOX,
                                  activebackground=ACCENT_LIME, highlightthickness=0, bd=0, showvalue=False,
                                  command=self.on_slider_kel_change)
        self.scale_kel.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Text Box Entry Kelembapan
        box_entry_k = tk.Frame(row_k, bg=COLOR_INPUT_BOX, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=6, pady=3)
        box_entry_k.pack(side="right")
        self.entry_kel = tk.Entry(box_entry_k, textvariable=self.var_kelembapan_text, width=5, bg=COLOR_INPUT_BOX,
                                  fg=ACCENT_LIME, font=("Segoe UI", 10, "bold"), bd=0, justify="center",
                                  insertbackground=TEXT_WHITE)
        self.entry_kel.pack(side="left")
        lbl_unit_k = tk.Label(box_entry_k, text="%", bg=COLOR_INPUT_BOX, fg=TEXT_MUTED, font=("Segoe UI", 8))
        lbl_unit_k.pack(side="right", padx=(2, 0))
        self.entry_kel.bind("<Return>", self.on_entry_kel_confirm)
        self.entry_kel.bind("<FocusOut>", self.on_entry_kel_confirm)

        # Status & Derajat Kelembapan (Font Diperbesar & Kontras Tinggi)
        self.lbl_mu_kel = tk.Label(card_input, text="Kering: 0.00 | Normal: 1.00 | Lembap: 0.00", bg=COLOR_CARD,
                                   fg="#CBD5E1", font=("Segoe UI", 9))
        self.lbl_mu_kel.pack(anchor="w", pady=(3, 1))

        self.lbl_warn_kel = tk.Label(card_input, textvariable=self.status_kel_clamp, bg=COLOR_CARD,
                                     fg="#A3E635", font=("Segoe UI", 9, "bold"))
        self.lbl_warn_kel.pack(anchor="w", pady=(0, 6))

        # Tombol Masukkan ke Tabel Pengujian
        btn_add_table = tk.Button(card_input, text="➕  Masukkan ke Tabel Pengujian", bg="#2B303C", fg=ACCENT_LIME,
                                  font=("Segoe UI", 9, "bold"), relief="flat", activebackground="#3A4150",
                                  activeforeground=TEXT_WHITE, cursor="hand2", padx=12, pady=7, bd=0,
                                  highlightbackground=COLOR_BORDER, highlightthickness=1,
                                  command=self.tambah_ke_tabel_pengujian)
        btn_add_table.pack(fill="x", pady=(8, 0))

        # CARD 2: HASIL REKOMENDASI DURASI (SEPERTI CARD SKOR BESAR PADA GAMBAR REFERENSI)
        card_output = tk.Frame(col_left, bg=COLOR_CARD, padx=20, pady=20,
                               highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_output.pack(fill="x", pady=(0, 14))

        lbl_out_head = tk.Label(card_output, text="Rekomendasi Durasi", bg=COLOR_CARD, fg=TEXT_MUTED,
                                font=("Segoe UI", 9, "bold"))
        lbl_out_head.pack(anchor="w")

        # Angka Raksasa (Modly Big Score Style)
        out_row = tk.Frame(card_output, bg=COLOR_CARD)
        out_row.pack(anchor="w", pady=(6, 4))

        self.lbl_durasi_num = tk.Label(out_row, text="15.00", bg=COLOR_CARD, fg=ACCENT_LIME,
                                       font=("Segoe UI", 32, "bold"))
        self.lbl_durasi_num.pack(side="left")

        lbl_unit_dur = tk.Label(out_row, text="menit", bg=COLOR_CARD, fg=TEXT_MUTED,
                                font=("Segoe UI", 12))
        lbl_unit_dur.pack(side="left", padx=(6, 0), pady=(12, 0))

        # Pill Status Kategori
        self.lbl_kategori_pill = tk.Label(card_output, text="SEDANG (8 – 22 Menit)", bg="#2B3024",
                                          fg=ACCENT_LIME, font=("Segoe UI", 9.5, "bold"), padx=12, pady=5)
        self.lbl_kategori_pill.pack(anchor="w", pady=(4, 6))

        lbl_aktuator_status = tk.Label(card_output, text="● Status Pompa: Katup Otomatis Terbuka", bg=COLOR_CARD,
                                       fg="#A3E635", font=("Segoe UI", 9.5, "bold"))
        lbl_aktuator_status.pack(anchor="w")

        # ----------------- KOLOM KANAN -----------------
        # CARD 3: EMBEDDED MATPLOTLIB CANVAS (LIVE DEFUZZIFIKASI PLOT)
        card_plot = tk.Frame(col_right, bg=COLOR_CARD, padx=14, pady=14,
                             highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_plot.pack(fill="both", expand=True, pady=(0, 14))

        lbl_cp_head = tk.Label(card_plot, text="Visualisasi Inferensi Mamdani & Posisi Centroid",
                               bg=COLOR_CARD, fg=TEXT_WHITE, font=("Segoe UI", 11, "bold"))
        lbl_cp_head.pack(anchor="w", pady=(0, 8))

        # Figure Matplotlib Stylized Matte
        self.fig_sim = Figure(figsize=(6.8, 3.8), dpi=100, facecolor=COLOR_CARD)
        self.ax_sim = self.fig_sim.add_subplot(111)
        self.ax_sim.set_facecolor("#1A1B20")

        self.canvas_sim = FigureCanvasTkAgg(self.fig_sim, master=card_plot)
        self.canvas_sim.get_tk_widget().pack(fill="both", expand=True)

        # CARD 4: LOG ATURAN YANG AKTIF
        card_log = tk.Frame(col_right, bg=COLOR_CARD, padx=16, pady=12,
                            highlightbackground=COLOR_BORDER, highlightthickness=1)
        card_log.pack(fill="x")

        lbl_log_head = tk.Label(card_log, text="Aturan Aktif Saat Ini (Firing Strength α > 0)",
                                bg=COLOR_CARD, fg=TEXT_WHITE, font=("Segoe UI", 10.5, "bold"))
        lbl_log_head.pack(anchor="w", pady=(0, 6))

        self.txt_rules = tk.Text(card_log, bg=COLOR_INPUT_BOX, fg="#FFFFFF", font=("Segoe UI", 9.5),
                                 bd=0, height=4, highlightbackground=COLOR_BORDER, highlightthickness=1, wrap="word",
                                 spacing1=3, spacing3=3)
        self.txt_rules.pack(fill="x")

    # =========================================================================
    # TWO-WAY BINDING & REACTION HANDLERS
    # =========================================================================
    def on_slider_suhu_change(self, val):
        if self._sync_lock: return
        self._sync_lock = True
        try:
            val_f = float(val)
            self.var_suhu_text.set(f"{val_f:.1f}")
            self.status_suhu_clamp.set("Rentang Normal (0 – 40 °C)")
            self.lbl_warn_suhu.configure(fg=ACCENT_LIME)
            self.update_simulation_live()
        finally:
            self._sync_lock = False

    def on_slider_kel_change(self, val):
        if self._sync_lock: return
        self._sync_lock = True
        try:
            val_f = float(val)
            self.var_kelembapan_text.set(f"{val_f:.1f}")
            self.status_kel_clamp.set("Rentang Normal (0 – 100 %)")
            self.lbl_warn_kel.configure(fg=ACCENT_LIME)
            self.update_simulation_live()
        finally:
            self._sync_lock = False

    def on_entry_suhu_confirm(self, event=None):
        if self._sync_lock: return
        self._sync_lock = True
        try:
            val = float(self.var_suhu_text.get().strip())
            # Safety clamping check
            if val < 0.0:
                self.status_suhu_clamp.set(f"⚠️ {val}°C < 0, disaturasi ke 0.0 °C")
                self.lbl_warn_suhu.configure(fg=ACCENT_AMBER)
                val = 0.0
            elif val > 40.0:
                self.status_suhu_clamp.set(f"⚠️ {val}°C > 40, disaturasi ke 40.0 °C")
                self.lbl_warn_suhu.configure(fg=ACCENT_AMBER)
                val = 40.0
            else:
                self.status_suhu_clamp.set("Rentang Normal (0 – 40 °C)")
                self.lbl_warn_suhu.configure(fg=ACCENT_LIME)

            self.var_suhu.set(val)
            self.var_suhu_text.set(f"{val:.1f}")
            self.update_simulation_live()
        except ValueError:
            messagebox.showwarning("Input Error", "Harap masukkan angka numerik yang valid untuk Suhu!")
            self.var_suhu_text.set(f"{self.var_suhu.get():.1f}")
        finally:
            self._sync_lock = False

    def on_entry_kel_confirm(self, event=None):
        if self._sync_lock: return
        self._sync_lock = True
        try:
            val = float(self.var_kelembapan_text.get().strip())
            # Safety clamping check
            if val < 0.0:
                self.status_kel_clamp.set(f"⚠️ {val}% < 0, disaturasi ke 0.0 %")
                self.lbl_warn_kel.configure(fg=ACCENT_AMBER)
                val = 0.0
            elif val > 100.0:
                self.status_kel_clamp.set(f"⚠️ {val}% > 100, disaturasi ke 100.0 %")
                self.lbl_warn_kel.configure(fg=ACCENT_AMBER)
                val = 100.0
            else:
                self.status_kel_clamp.set("Rentang Normal (0 – 100 %)")
                self.lbl_warn_kel.configure(fg=ACCENT_LIME)

            self.var_kelembapan.set(val)
            self.var_kelembapan_text.set(f"{val:.1f}")
            self.update_simulation_live()
        except ValueError:
            messagebox.showwarning("Input Error", "Harap masukkan angka numerik yang valid untuk Kelembapan!")
            self.var_kelembapan_text.set(f"{self.var_kelembapan.get():.1f}")
        finally:
            self._sync_lock = False

    def reset_default_values(self):
        self.var_suhu.set(25.0)
        self.var_kelembapan.set(50.0)
        self.var_suhu_text.set("25.0")
        self.var_kelembapan_text.set("50.0")
        self.status_suhu_clamp.set("Rentang Normal (0 – 40 °C)")
        self.status_kel_clamp.set("Rentang Normal (0 – 100 %)")
        self.lbl_warn_suhu.configure(fg="#A3E635")
        self.lbl_warn_kel.configure(fg="#A3E635")
        self.update_simulation_live()

    def tambah_ke_tabel_pengujian(self):
        suhu = self.var_suhu.get()
        kelembapan = self.var_kelembapan.get()
        res = self.fuzzy_engine.compute(suhu, kelembapan)
        durasi = res['hasil_defuzzifikasi']
        if durasi <= 10.0:
            kat = "Singkat"
        elif durasi <= 20.0:
            kat = "Sedang"
        else:
            kat = "Lama"

        no_baru = len(self.tree.get_children()) + 1
        ket = f"Uji Real-time: Suhu {suhu:.1f}°C, Kel {kelembapan:.1f}%"

        self.tree.insert("", "end", values=(
            no_baru, f"{suhu:.1f}", f"{kelembapan:.1f}", f"{durasi:.2f}", kat, ket
        ))

        messagebox.showinfo("Berhasil Ditambahkan",
                            f"Skenario berhasil dimasukkan ke Tabel Pengujian!\n\n"
                            f"• No          : {no_baru}\n"
                            f"• Suhu        : {suhu:.1f} °C\n"
                            f"• Kelembapan  : {kelembapan:.1f} %\n"
                            f"• Rekomendasi : {durasi:.2f} Menit ({kat})\n\n"
                            f"Buka tab '📋 Tabel Pengujian' untuk melihat daftar lengkap.")

    # =========================================================================
    # RENDER LIVE SIMULASI MATPLOTLIB PLOT
    # =========================================================================
    def update_simulation_live(self):
        suhu = self.var_suhu.get()
        kelembapan = self.var_kelembapan.get()

        res = self.fuzzy_engine.compute(suhu, kelembapan)
        durasi = res['hasil_defuzzifikasi']

        # Update Derajat Fuzzifikasi
        mu_s = res['fuzzifikasi']['suhu']
        self.lbl_mu_suhu.configure(text=f"Dingin: {mu_s['dingin']:.2f} | Normal: {mu_s['normal']:.2f} | Panas: {mu_s['panas']:.2f}")

        mu_k = res['fuzzifikasi']['kelembapan']
        self.lbl_mu_kel.configure(text=f"Kering: {mu_k['kering']:.2f} | Normal: {mu_k['normal']:.2f} | Lembap: {mu_k['lembap']:.2f}")

        # Update Angka Skor Besar
        self.lbl_durasi_num.configure(text=f"{durasi:.2f}")
        if durasi <= 10.0:
            self.lbl_kategori_pill.configure(text="SINGKAT (0 – 12 Menit)")
        elif durasi <= 20.0:
            self.lbl_kategori_pill.configure(text="SEDANG (8 – 22 Menit)")
        else:
            self.lbl_kategori_pill.configure(text="LAMA (18 – 30 Menit)")

        # Update List Aturan (Format Sangat Jelas & Mudah Dibaca)
        self.txt_rules.delete("1.0", tk.END)
        found = False
        for r in res['rule_evaluations']:
            if r['alpha'] > 0:
                found = True
                rule_tag = r['description'].split(':')[0]
                rule_detail = r['description'].split(': ')[1]
                self.txt_rules.insert(tk.END, f"• [{rule_tag}]  α = {r['alpha']:.3f}  →  Output: {r['output_label'].upper()}\n")
                self.txt_rules.insert(tk.END, f"   Kondisi: {rule_detail}\n\n")
        if not found:
            self.txt_rules.insert(tk.END, "• Tidak ada aturan aktif (Fallback batas aman)\n")

        # Render Canvas Plot
        self.ax_sim.clear()
        x = res['durasi_range']
        agg = res['aggregated']

        # Garis referensi tegas & kontras
        self.ax_sim.plot(x, res['mf_durasi_curves']['singkat'], color='#94A3B8', linestyle='--', linewidth=1.5, alpha=0.8, label='Singkat')
        self.ax_sim.plot(x, res['mf_durasi_curves']['sedang'], color=ACCENT_PURPLE, linestyle='--', linewidth=1.5, alpha=0.9, label='Sedang')
        self.ax_sim.plot(x, res['mf_durasi_curves']['lama'], color=ACCENT_ROSE, linestyle='--', linewidth=1.5, alpha=0.9, label='Lama')

        # Area Agregasi (Arsiran Abu-abu Gelap / Dark Charcoal)
        self.ax_sim.fill_between(x, 0, agg, facecolor="#353945", alpha=0.8, label='Agregasi Area (MAX)')
        self.ax_sim.plot(x, agg, color="#A1A1AA", linewidth=2.0)

        # Garis Centroid Berpendar (Electric Lime Accent)
        self.ax_sim.axvline(x=durasi, color=ACCENT_LIME, linestyle='-', linewidth=2.8,
                            label=f'Centroid: {durasi:.2f} m')

        idx_c = np.abs(x - durasi).argmin()
        self.ax_sim.scatter([durasi], [agg[idx_c]], color=ACCENT_LIME, s=90, zorder=6, edgecolors='#18191D', linewidth=2.0)

        # Styling Plot Sesuai Palet (Font Jelas & Kontras Tinggi)
        self.ax_sim.set_title(f"Durasi Centroid = {durasi:.2f} menit  (Suhu: {suhu:.1f}°C, Kelembapan: {kelembapan:.1f}%)",
                              color=TEXT_WHITE, fontsize=10.5, fontweight='bold', pad=10)
        self.ax_sim.set_xlabel("Durasi Penyiraman (Menit)", color="#CBD5E1", fontsize=9, fontweight='bold')
        self.ax_sim.set_ylabel("Derajat Keanggotaan (μ)", color="#CBD5E1", fontsize=9, fontweight='bold')
        self.ax_sim.set_xlim(0, 30)
        self.ax_sim.set_ylim(-0.05, 1.05)

        self.ax_sim.tick_params(colors="#CBD5E1", labelsize=8.5)
        for spine in self.ax_sim.spines.values():
            spine.set_color(COLOR_BORDER)

        self.ax_sim.grid(True, linestyle=':', color="#2E313A", alpha=0.7)
        # Legend Font Besar, Jelas, & Kontras Tinggi
        self.ax_sim.legend(loc='upper right', facecolor='#18191E', edgecolor='#474C5A',
                           labelcolor='#FFFFFF', fontsize=9.5, framealpha=0.96)

        self.fig_sim.tight_layout()
        self.canvas_sim.draw()

    def save_current_plot(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
                                             initialfile=f"centroid_suhu_{int(self.var_suhu.get())}_kel_{int(self.var_kelembapan.get())}.png")
        if fpath:
            self.fig_sim.savefig(fpath, dpi=300, facecolor=COLOR_CARD)
            messagebox.showinfo("Tersimpan", f"Grafik defuzzifikasi berhasil disimpan ke:\n{fpath}")

    # =========================================================================
    # VIEW 2: KURVA MEMBERSHIP FUNCTION
    # =========================================================================
    def build_view_mf(self):
        card = tk.Frame(self.view_mf, bg=COLOR_CARD, padx=16, pady=16,
                        highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        fig_mf = Figure(figsize=(9, 5.5), dpi=100, facecolor=COLOR_CARD)
        axes = fig_mf.subplots(3, 1)
        sys = self.fuzzy_engine

        # Subplot 1: Suhu
        ax1 = axes[0]
        ax1.set_facecolor("#1A1B20")
        ax1.plot(sys.suhu_range, trimf(sys.suhu_range, sys.mf_suhu['dingin']), color='#60A5FA', linewidth=2, label='Dingin [0, 0, 20]')
        ax1.plot(sys.suhu_range, trimf(sys.suhu_range, sys.mf_suhu['normal']), color=ACCENT_LIME, linewidth=2, label='Normal [15, 25, 35]')
        ax1.plot(sys.suhu_range, trimf(sys.suhu_range, sys.mf_suhu['panas']), color=ACCENT_ROSE, linewidth=2, label='Panas [25, 40, 40]')
        ax1.set_title("(a) Input: Suhu Udara Lingkungan (°C)", color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=4)
        ax1.set_xlim(0, 40); ax1.set_ylim(-0.05, 1.05)
        ax1.tick_params(colors="#CBD5E1", labelsize=8)
        ax1.grid(True, linestyle=':', color=COLOR_BORDER, alpha=0.6)
        ax1.legend(loc='upper right', facecolor='#18191E', edgecolor='#474C5A', labelcolor='#FFFFFF', fontsize=9, framealpha=0.96)
        for sp in ax1.spines.values(): sp.set_color(COLOR_BORDER)

        # Subplot 2: Kelembapan
        ax2 = axes[1]
        ax2.set_facecolor("#1A1B20")
        ax2.plot(sys.kelembapan_range, trimf(sys.kelembapan_range, sys.mf_kelembapan['kering']), color=ACCENT_AMBER, linewidth=2, label='Kering [0, 0, 50]')
        ax2.plot(sys.kelembapan_range, trimf(sys.kelembapan_range, sys.mf_kelembapan['normal']), color=ACCENT_LIME, linewidth=2, label='Normal [30, 50, 70]')
        ax2.plot(sys.kelembapan_range, trimf(sys.kelembapan_range, sys.mf_kelembapan['lembap']), color='#38BDF8', linewidth=2, label='Lembap [50, 100, 100]')
        ax2.set_title("(b) Input: Kelembapan Tanah (%)", color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=4)
        ax2.set_xlim(0, 100); ax2.set_ylim(-0.05, 1.05)
        ax2.tick_params(colors="#CBD5E1", labelsize=8)
        ax2.grid(True, linestyle=':', color=COLOR_BORDER, alpha=0.6)
        ax2.legend(loc='upper right', facecolor='#18191E', edgecolor='#474C5A', labelcolor='#FFFFFF', fontsize=9, framealpha=0.96)
        for sp in ax2.spines.values(): sp.set_color(COLOR_BORDER)

        # Subplot 3: Durasi
        ax3 = axes[2]
        ax3.set_facecolor("#1A1B20")
        ax3.plot(sys.durasi_range, trimf(sys.durasi_range, sys.mf_durasi['singkat']), color='#94A3B8', linewidth=2, label='Singkat [0, 0, 12]')
        ax3.plot(sys.durasi_range, trimf(sys.durasi_range, sys.mf_durasi['sedang']), color=ACCENT_PURPLE, linewidth=2, label='Sedang [8, 15, 22]')
        ax3.plot(sys.durasi_range, trimf(sys.durasi_range, sys.mf_durasi['lama']), color=ACCENT_LIME, linewidth=2, label='Lama [18, 30, 30]')
        ax3.set_title("(c) Output: Durasi Penyiraman (Menit)", color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=4)
        ax3.set_xlim(0, 30); ax3.set_ylim(-0.05, 1.05)
        ax3.tick_params(colors="#CBD5E1", labelsize=8)
        ax3.grid(True, linestyle=':', color=COLOR_BORDER, alpha=0.6)
        ax3.legend(loc='upper right', facecolor='#18191E', edgecolor='#474C5A', labelcolor='#FFFFFF', fontsize=9, framealpha=0.96)
        for sp in ax3.spines.values(): sp.set_color(COLOR_BORDER)

        fig_mf.tight_layout()
        canvas_mf = FigureCanvasTkAgg(fig_mf, master=card)
        canvas_mf.get_tk_widget().pack(fill="both", expand=True)

    # =========================================================================
    # VIEW 3: TABEL PENGUJIAN 10 SKENARIO
    # =========================================================================
    def build_view_tabel(self):
        card = tk.Frame(self.view_tabel, bg=COLOR_CARD, padx=18, pady=18,
                        highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        bar_action = tk.Frame(card, bg=COLOR_CARD)
        bar_action.pack(fill="x", pady=(0, 12))

        lbl_t_head = tk.Label(bar_action, text="Daftar Skenario & Riwayat Pengujian", bg=COLOR_CARD,
                              fg=TEXT_WHITE, font=("Segoe UI", 11, "bold"))
        lbl_t_head.pack(side="left")

        btn_export = tk.Button(bar_action, text="📥  Ekspor CSV", bg=COLOR_CARD_HOVER, fg=TEXT_WHITE,
                               font=("Segoe UI", 8, "bold"), relief="flat", activebackground="#353945",
                               cursor="hand2", padx=12, pady=5, bd=0, highlightbackground=COLOR_BORDER,
                               highlightthickness=1, command=self.export_table_to_csv)
        btn_export.pack(side="right", padx=(8, 0))

        btn_reset_tb = tk.Button(bar_action, text="🔄  Reset 10 Data Awal", bg=COLOR_CARD_HOVER, fg=TEXT_MUTED,
                                 font=("Segoe UI", 8, "bold"), relief="flat", activebackground="#353945",
                                 cursor="hand2", padx=12, pady=5, bd=0, highlightbackground=COLOR_BORDER,
                                 highlightthickness=1, command=self.populate_table_data)
        btn_reset_tb.pack(side="right", padx=(8, 0))

        btn_apply = tk.Button(bar_action, text="⚡  Terapkan ke Simulasi", bg=ACCENT_LIME, fg=TEXT_DARK,
                              font=("Segoe UI", 8, "bold"), relief="flat", activebackground="#BCE62C",
                              cursor="hand2", padx=12, pady=5, bd=0, command=self.load_selected_to_simulation)
        btn_apply.pack(side="right")

        # Treeview Kontainer
        tree_box = tk.Frame(card, bg=COLOR_CARD)
        tree_box.pack(fill="both", expand=True)

        cols = ("no", "suhu", "kelembapan", "durasi", "kategori", "keterangan")
        self.tree = ttk.Treeview(tree_box, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("no", text="No")
        self.tree.heading("suhu", text="Suhu (°C)")
        self.tree.heading("kelembapan", text="Kelembapan (%)")
        self.tree.heading("durasi", text="Durasi (Menit)")
        self.tree.heading("kategori", text="Kategori")
        self.tree.heading("keterangan", text="Skenario Pengujian UTS")

        self.tree.column("no", width=45, anchor="center")
        self.tree.column("suhu", width=95, anchor="center")
        self.tree.column("kelembapan", width=110, anchor="center")
        self.tree.column("durasi", width=120, anchor="center")
        self.tree.column("kategori", width=120, anchor="center")
        self.tree.column("keterangan", width=360, anchor="w")

        scroll = ttk.Scrollbar(tree_box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self.load_selected_to_simulation())
        self.populate_table_data()

    def populate_table_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        from main import DATA_PENGUJIAN
        for d in DATA_PENGUJIAN:
            res = self.fuzzy_engine.compute(d['suhu'], d['kelembapan'])
            dur = res['hasil_defuzzifikasi']
            if dur <= 10.0: kat = "Singkat"
            elif dur <= 20.0: kat = "Sedang"
            else: kat = "Lama"

            self.tree.insert("", "end", values=(
                d['no'], f"{d['suhu']:.1f}", f"{d['kelembapan']:.1f}",
                f"{dur:.2f}", kat, d['keterangan']
            ))

    def load_selected_to_simulation(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Pilih Baris", "Klik salah satu baris pada tabel untuk dimuat ke simulasi!")
            return
        vals = self.tree.item(sel[0], "values")
        s = float(vals[1])
        k = float(vals[2])

        self.var_suhu.set(s)
        self.var_kelembapan.set(k)
        self.var_suhu_text.set(f"{s:.1f}")
        self.var_kelembapan_text.set(f"{k:.1f}")

        self.switch_view("simulasi")

    def export_table_to_csv(self):
        fpath = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")],
                                             initialfile="hasil_pengujian_10_data_uts.csv")
        if not fpath: return
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["No", "Suhu (C)", "Kelembapan (%)", "Durasi (Menit)", "Kategori", "Skenario"])
            for child in self.tree.get_children():
                writer.writerow(self.tree.item(child, "values"))
        messagebox.showinfo("Berhasil", f"Data berhasil diekspor ke:\n{fpath}")

    # =========================================================================
    # VIEW 4: RULE BASE & ANALISIS SOAL UTS
    # =========================================================================
    def build_view_analisis(self):
        card = tk.Frame(self.view_analisis, bg=COLOR_CARD, padx=18, pady=18,
                        highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True)

        col_left = tk.Frame(card, bg=COLOR_CARD)
        col_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        col_right = tk.Frame(card, bg=COLOR_CARD)
        col_right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Matriks 9 Aturan
        lbl_r_head = tk.Label(col_left, text="Matriks 9 Aturan Fuzzy Mamdani", bg=COLOR_CARD,
                              fg=ACCENT_LIME, font=("Segoe UI", 10, "bold"))
        lbl_r_head.pack(anchor="w", pady=(0, 8))

        txt_r = tk.Text(col_left, bg=COLOR_INPUT_BOX, fg=TEXT_WHITE, font=("Consolas", 9),
                        bd=0, highlightbackground=COLOR_BORDER, highlightthickness=1, wrap="word")
        txt_r.pack(fill="both", expand=True)

        rules_str = """9 ATURAN INFERENSI FUZZY (MAMDANI):
------------------------------------------------
R1: IF Suhu DINGIN AND Kelembapan KERING
    THEN Durasi SEDANG
R2: IF Suhu DINGIN AND Kelembapan NORMAL
    THEN Durasi SINGKAT
R3: IF Suhu DINGIN AND Kelembapan LEMBAP
    THEN Durasi SINGKAT
------------------------------------------------
R4: IF Suhu NORMAL AND Kelembapan KERING
    THEN Durasi LAMA
R5: IF Suhu NORMAL AND Kelembapan NORMAL
    THEN Durasi SEDANG
R6: IF Suhu NORMAL AND Kelembapan LEMBAP
    THEN Durasi SINGKAT
------------------------------------------------
R7: IF Suhu PANAS  AND Kelembapan KERING
    THEN Durasi LAMA
R8: IF Suhu PANAS  AND Kelembapan NORMAL
    THEN Durasi LAMA
R9: IF Suhu PANAS  AND Kelembapan LEMBAP
    THEN Durasi SEDANG
------------------------------------------------
Prinsip Mekatronika:
• Kelembapan tanah memegang prioritas kendali.
• Saat tanah LEMBAP, durasi penyiraman dibatasi
  pada SINGKAT atau SEDANG demi mencegah busuk akar.
"""
        txt_r.insert(tk.END, rules_str)
        txt_r.configure(state="disabled")

        # Jawaban 4 Soal UTS
        lbl_a_head = tk.Label(col_right, text="Jawaban 4 Pertanyaan Analisis Soal UTS", bg=COLOR_CARD,
                              fg=ACCENT_LIME, font=("Segoe UI", 10, "bold"))
        lbl_a_head.pack(anchor="w", pady=(0, 8))

        txt_a = tk.Text(col_right, bg=COLOR_INPUT_BOX, fg=TEXT_WHITE, font=("Segoe UI", 9),
                        bd=0, highlightbackground=COLOR_BORDER, highlightthickness=1, wrap="word")
        txt_a.pack(fill="both", expand=True)

        ans_str = """1. Mengapa tanah kering durasi lebih lama dari tanah lembap?
Jawab:
Pada kondisi kering (kelembapan < 30%), air tanah berada di bawah kapasitas lapang. Air butuh waktu lebih lama agar meresap ke zona perakaran aktif (root zone). Jika disiram singkat, air hanya membasahi lapisan atas yang lekas menguap. Sebaliknya pada kondisi lembap, pori tanah sudah jenuh; kelebihan air memicu genangan (waterlogging) dan pembusukan akar.

2. Pengaruh perubahan membership function pada defuzzifikasi?
Jawab:
Bentuk dan parameter kurva segitiga menentukan nilai firing strength (α) dan luas area implikasi. Karena metode Centroid menghitung titik berat z* = ∫(y·μ)dy / ∫μ dy, memperlebar himpunan 'Lama' akan memperbesar momen area kanan sehingga titik centroid bergeser ke durasi yang lebih lama.

3. Apa jika kombinasi input tidak memicu rule apapun?
Jawab:
Seluruh α = 0, kurva agregasi datar pada nol (μ_agg = 0), dan terjadi pembagian nol (0/0 = NaN). Aktuator fisik akan mengalami undefined state/freeze. Di program ini dijamin aman dengan overlap kurva minimal 25% dan fallback nilai aman.

4. Apakah hasil selalu meningkat ketika suhu naik?
Jawab:
TIDAK SELALU. Durasi ditentukan oleh interaksi multivariabel antara suhu dan kelembapan.
Bukti Data:
• Suhu 35°C & Kelembapan 15% -> Durasi: 25.68 Menit (Lama)
• Suhu 32°C & Kelembapan 75% -> Durasi: 11.33 Menit (Sedang)
Meskipun suhu panas, jika tanah lembap, sistem memprioritaskan efisiensi air (Rule 9).
"""
        txt_a.insert(tk.END, ans_str)
        txt_a.configure(state="disabled")


if __name__ == "__main__":
    app = ModernFuzzySprinklerApp()
    app.mainloop()
