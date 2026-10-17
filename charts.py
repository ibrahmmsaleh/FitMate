"""Grafik SVG sederhana yang dibuat langsung dengan Python (tanpa JavaScript).

Warna diambil dari CSS (class .chart-*), jadi mudah diubah di style.css.
"""
import math

from markupsafe import Markup, escape

W, H = 640, 240
PAD_L, PAD_R, PAD_T, PAD_B = 48, 16, 16, 36


def _nice_step(span, integer=False, target=4):
    """Langkah sumbu yang 'bulat' (1, 2, 5, 10, ...) supaya angka di sumbu mudah dibaca."""
    raw = span / target
    magnitude = 10 ** math.floor(math.log10(raw))
    for factor in ((1, 2, 5, 10) if integer else (1, 2, 2.5, 5, 10)):
        if raw <= factor * magnitude:
            return max(factor * magnitude, 1) if integer else factor * magnitude
    return 10 * magnitude


def _scale(values, force_zero=False, integer=False):
    """Mengembalikan (batas_bawah, batas_atas, langkah) dengan angka bulat."""
    low, high = min(values), max(values)
    if force_zero:
        low = 0
    if high == low:
        high = low + 1
    if not force_zero:  # beri ruang agar titik tidak menempel tepi
        pad = (high - low) * 0.1
        low, high = low - pad, high + pad
    step = _nice_step(high - low, integer)
    return math.floor(low / step) * step, math.ceil(high / step) * step, step


def _nice(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _frame(low, high, step, aria):
    parts = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(aria)}" '
        f'preserveAspectRatio="xMidYMid meet">'
    ]
    ticks = int(round((high - low) / step))
    for i in range(ticks + 1):
        value = low + step * i
        y = PAD_T + (H - PAD_T - PAD_B) * (1 - (value - low) / (high - low))
        parts.append(f'<line class="chart-grid" x1="{PAD_L}" x2="{W - PAD_R}" y1="{y:.1f}" y2="{y:.1f}"/>')
        parts.append(f'<text class="chart-label" x="{PAD_L - 8}" y="{y + 4:.1f}" text-anchor="end">{_nice(value)}</text>')
    return parts


def line_chart(points, aria, unit=""):
    """points: daftar (label, nilai) berurutan waktu. Mengembalikan Markup SVG."""
    if not points:
        return Markup("")
    values = [v for _, v in points]
    low, high, step = _scale(values)
    parts = _frame(low, high, step, aria)
    n = len(points)
    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B

    def xy(i, v):
        x = PAD_L + (plot_w * i / (n - 1) if n > 1 else plot_w / 2)
        y = PAD_T + plot_h * (1 - (v - low) / (high - low))
        return x, y

    coords = [xy(i, v) for i, (_, v) in enumerate(points)]
    if n > 1:
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
        parts.append(f'<polyline class="chart-line" points="{path}"/>')
    for (x, y), (label, v) in zip(coords, points):
        parts.append(
            f'<circle class="chart-dot" cx="{x:.1f}" cy="{y:.1f}" r="4">'
            f"<title>{escape(label)}: {_nice(v)}{escape(unit)}</title></circle>"
        )
    # label sumbu x: pertama, terakhir, dan tengah bila cukup banyak
    shown = {0, n - 1} | ({n // 2} if n >= 5 else set())
    for i in sorted(shown):
        x, _ = coords[i]
        anchor = "start" if i == 0 and n > 1 else ("end" if i == n - 1 and n > 1 else "middle")
        parts.append(f'<text class="chart-label" x="{x:.1f}" y="{H - 12}" text-anchor="{anchor}">{escape(points[i][0])}</text>')
    parts.append("</svg>")
    return Markup("".join(parts))


def bar_chart(points, aria, unit=""):
    """points: daftar (label, nilai >= 0). Sumbu y selalu mulai dari 0."""
    if not points:
        return Markup("")
    values = [v for _, v in points]
    low, high, step = _scale(values, force_zero=True, integer=True)
    parts = _frame(low, high, step, aria)
    n = len(points)
    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B
    slot = plot_w / n
    bar_w = min(48, slot * 0.6)
    for i, (label, v) in enumerate(points):
        h = plot_h * (v - low) / (high - low)
        x = PAD_L + slot * i + (slot - bar_w) / 2
        y = PAD_T + plot_h - h
        parts.append(
            f'<rect class="chart-bar" x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(h, 0):.1f}">'
            f"<title>{escape(label)}: {_nice(v)}{escape(unit)}</title></rect>"
        )
        parts.append(f'<text class="chart-label" x="{x + bar_w / 2:.1f}" y="{H - 12}" text-anchor="middle">{escape(label)}</text>')
    parts.append("</svg>")
    return Markup("".join(parts))
