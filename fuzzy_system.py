"""
Sistem Cerdas untuk Pengendalian Penyiraman Tanaman
Metode: Fuzzy Mamdani dengan Triangular Membership Function
Mata Kuliah: MKP501 Sistem Cerdas
NIM GENAP
"""

import numpy as np


def trimf(x, params):
    """
    Fungsi Keanggotaan Segitiga (Triangular Membership Function)
    params = [a, b, c]
    - a: batas kiri (mu = 0)
    - b: puncak segitiga (mu = 1)
    - c: batas kanan (mu = 0)
    Mendukung bahu kiri (a == b) dan bahu kanan (b == c).
    """
    a, b, c = params
    x = np.asarray(x)
    y = np.zeros_like(x, dtype=float)

    # Kasus 1: Bahu kiri (a == b) -> menurun dari 1 di a ke 0 di c
    if a == b and b < c:
        idx_left = x <= a
        y[idx_left] = 1.0
        idx_slope = (x > a) & (x < c)
        y[idx_slope] = (c - x[idx_slope]) / (c - a)
        return y

    # Kasus 2: Bahu kanan (b == c) -> naik dari 0 di a ke 1 di c
    if b == c and a < b:
        idx_slope = (x > a) & (x < c)
        y[idx_slope] = (x[idx_slope] - a) / (c - a)
        idx_right = x >= c
        y[idx_right] = 1.0
        return y

    # Kasus 3: Segitiga standar (a < b < c)
    # Lereng naik: a <= x <= b
    if a != b:
        idx1 = (x >= a) & (x <= b)
        y[idx1] = (x[idx1] - a) / (b - a)
    # Lereng turun: b < x <= c
    if b != c:
        idx2 = (x > b) & (x <= c)
        y[idx2] = (c - x[idx2]) / (c - b)

    return np.clip(y, 0.0, 1.0)


class FuzzySprinklerSystem:
    def __init__(self):
        # 1. Semesta Pembicaraan (Universe of Discourse)
        self.suhu_range = np.linspace(0, 40, 401)          # 0 - 40 C
        self.kelembapan_range = np.linspace(0, 100, 501)   # 0 - 100 %
        self.durasi_range = np.linspace(0, 30, 601)        # 0 - 30 menit

        # 2. Parameter Membership Function (Triangular)
        # Suhu
        self.mf_suhu = {
            'dingin': [0, 0, 20],
            'normal': [15, 25, 35],
            'panas':  [25, 40, 40]
        }

        # Kelembapan Tanah
        self.mf_kelembapan = {
            'kering': [0, 0, 50],
            'normal': [30, 50, 70],
            'lembap': [50, 100, 100]
        }

        # Durasi Penyiraman
        self.mf_durasi = {
            'singkat': [0, 0, 12],
            'sedang':  [8, 15, 22],
            'lama':    [18, 30, 30]
        }

        # 3. Rule Base (9 Aturan IF-THEN Mamdani)
        self.rules = [
            # Rule 1: DINGIN & KERING -> SEDANG
            ('dingin', 'kering', 'sedang', 'R1: IF Suhu DINGIN AND Kelembapan KERING THEN Durasi SEDANG'),
            # Rule 2: DINGIN & NORMAL -> SINGKAT
            ('dingin', 'normal', 'singkat', 'R2: IF Suhu DINGIN AND Kelembapan NORMAL THEN Durasi SINGKAT'),
            # Rule 3: DINGIN & LEMBAP -> SINGKAT
            ('dingin', 'lembap', 'singkat', 'R3: IF Suhu DINGIN AND Kelembapan LEMBAP THEN Durasi SINGKAT'),
            # Rule 4: NORMAL & KERING -> LAMA
            ('normal', 'kering', 'lama',    'R4: IF Suhu NORMAL AND Kelembapan KERING THEN Durasi LAMA'),
            # Rule 5: NORMAL & NORMAL -> SEDANG
            ('normal', 'normal', 'sedang',  'R5: IF Suhu NORMAL AND Kelembapan NORMAL THEN Durasi SEDANG'),
            # Rule 6: NORMAL & LEMBAP -> SINGKAT
            ('normal', 'lembap', 'singkat', 'R6: IF Suhu NORMAL AND Kelembapan LEMBAP THEN Durasi SINGKAT'),
            # Rule 7: PANAS & KERING -> LAMA
            ('panas',  'kering', 'lama',    'R7: IF Suhu PANAS AND Kelembapan KERING THEN Durasi LAMA'),
            # Rule 8: PANAS & NORMAL -> LAMA
            ('panas',  'normal', 'lama',    'R8: IF Suhu PANAS AND Kelembapan NORMAL THEN Durasi LAMA'),
            # Rule 9: PANAS & LEMBAP -> SEDANG
            ('panas',  'lembap', 'sedang',  'R9: IF Suhu PANAS AND Kelembapan LEMBAP THEN Durasi SEDANG'),
        ]

    def fuzzifikasi_suhu(self, val):
        """Menghitung derajat keanggotaan untuk input Suhu"""
        return {
            'dingin': float(trimf(val, self.mf_suhu['dingin'])),
            'normal': float(trimf(val, self.mf_suhu['normal'])),
            'panas':  float(trimf(val, self.mf_suhu['panas']))
        }

    def fuzzifikasi_kelembapan(self, val):
        """Menghitung derajat keanggotaan untuk input Kelembapan"""
        return {
            'kering': float(trimf(val, self.mf_kelembapan['kering'])),
            'normal': float(trimf(val, self.mf_kelembapan['normal'])),
            'lembap': float(trimf(val, self.mf_kelembapan['lembap']))
        }

    def compute(self, suhu_val, kelembapan_val):
        """
        Melakukan inferensi Fuzzy Mamdani lengkap:
        1. Fuzzifikasi
        2. Firing strength (MIN)
        3. Implikasi (MIN)
        4. Agregasi (MAX)
        5. Defuzzifikasi Centroid
        """
        # Validasi batas rentang
        suhu_val = np.clip(suhu_val, 0, 40)
        kelembapan_val = np.clip(kelembapan_val, 0, 100)

        # 1. Fuzzifikasi
        mu_suhu = self.fuzzifikasi_suhu(suhu_val)
        mu_kelembapan = self.fuzzifikasi_kelembapan(kelembapan_val)

        # 2 & 3. Evaluasi Rules & Implikasi (Operator MIN)
        rule_evaluations = []
        implications = []

        # Kurva MF asli dari durasi
        mf_durasi_curves = {
            'singkat': trimf(self.durasi_range, self.mf_durasi['singkat']),
            'sedang':  trimf(self.durasi_range, self.mf_durasi['sedang']),
            'lama':    trimf(self.durasi_range, self.mf_durasi['lama'])
        }

        for s_label, k_label, out_label, description in self.rules:
            # Firing strength: operator MIN
            alpha = min(mu_suhu[s_label], mu_kelembapan[k_label])
            # Implikasi: pemotongan kurva konsekuen dengan operator MIN
            implied_curve = np.fmin(alpha, mf_durasi_curves[out_label])

            rule_evaluations.append({
                'description': description,
                'alpha': alpha,
                'output_label': out_label,
                'curve': implied_curve
            })
            implications.append(implied_curve)

        # 4. Agregasi seluruh output (Operator MAX)
        aggregated = np.zeros_like(self.durasi_range)
        for curve in implications:
            aggregated = np.fmax(aggregated, curve)

        # 5. Defuzzifikasi: Metode Centroid (Center of Gravity)
        # z* = sum(z * mu(z)) / sum(mu(z))
        sum_mu = np.sum(aggregated)
        if sum_mu == 0:
            # Default fallback jika tidak ada rule aktif
            centroid = (self.durasi_range[0] + self.durasi_range[-1]) / 2.0
        else:
            centroid = np.sum(self.durasi_range * aggregated) / sum_mu

        return {
            'input': {
                'suhu': suhu_val,
                'kelembapan': kelembapan_val
            },
            'fuzzifikasi': {
                'suhu': mu_suhu,
                'kelembapan': mu_kelembapan
            },
            'rule_evaluations': rule_evaluations,
            'aggregated': aggregated,
            'durasi_range': self.durasi_range,
            'mf_durasi_curves': mf_durasi_curves,
            'hasil_defuzzifikasi': float(centroid)
        }
