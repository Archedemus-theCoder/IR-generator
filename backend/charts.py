"""Chart generation for IR slides using matplotlib."""

from __future__ import annotations
import io
import re
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm

# --- Korean font setup ---
def _setup_korean_font():
    """Find and set a Korean-capable font for matplotlib."""
    system = platform.system()
    candidates = []
    if system == "Darwin":  # macOS
        candidates = ["AppleGothic", "Apple SD Gothic Neo", "Noto Sans CJK KR", "Malgun Gothic"]
    elif system == "Windows":
        candidates = ["Malgun Gothic", "맑은 고딕", "NanumGothic"]
    else:  # Linux
        candidates = ["Noto Sans CJK KR", "NanumGothic", "UnDotum", "DejaVu Sans"]

    available = {f.name for f in fm.fontManager.ttflist}
    for font_name in candidates:
        if font_name in available:
            plt.rcParams["font.family"] = font_name
            plt.rcParams["axes.unicode_minus"] = False
            return font_name

    # Fallback: try to find ANY font with Korean glyphs
    for f in fm.fontManager.ttflist:
        if any(kw in f.name.lower() for kw in ["gothic", "nanum", "noto", "malgun", "gulim", "batang"]):
            plt.rcParams["font.family"] = f.name
            plt.rcParams["axes.unicode_minus"] = False
            return f.name

    # Last resort
    plt.rcParams["axes.unicode_minus"] = False
    return None

KOREAN_FONT = _setup_korean_font()

ORANGE = "#E8470A"
BLACK = "#111111"
GRAY = "#808080"
LIGHT_GRAY = "#F2F2F2"
GREEN = "#2ECC71"
RED = "#E74C3C"


def _parse_korean_number(s: str) -> float:
    """Parse Korean financial numbers like '89억', '-5억', '15%'."""
    s = s.strip().replace(",", "")
    if not s or s == "-":
        return 0
    # Handle percentage
    if s.endswith("%"):
        return float(s[:-1])
    multiplier = 1
    if "억" in s:
        multiplier = 100_000_000
        s = s.replace("억", "")
    elif "만" in s:
        multiplier = 10_000
        s = s.replace("만", "")
    try:
        return float(s) * multiplier
    except ValueError:
        return 0


def render_pl_chart(pl_data) -> bytes:
    """Render P&L bar chart (revenue + operating profit)."""
    years = pl_data.years
    if not years or not pl_data.rows:
        return _empty_chart()

    revenue_row = next((r for r in pl_data.rows if "매출" in r.label and "률" not in r.label), None)
    profit_row = next((r for r in pl_data.rows if "영업이익" in r.label and "률" not in r.label), None)

    if not revenue_row:
        return _empty_chart()

    revenues = [_parse_korean_number(revenue_row.values.get(y, "0")) for y in years]
    profits = [_parse_korean_number(profit_row.values.get(y, "0")) for y in years] if profit_row else [0] * len(years)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    x = range(len(years))
    bar_width = 0.35

    # Revenue bars
    bars1 = ax.bar([i - bar_width / 2 for i in x], [v / 1e8 for v in revenues],
                    bar_width, color=ORANGE, alpha=0.9, label="매출", zorder=2)

    # Profit bars
    profit_colors = [GREEN if v >= 0 else RED for v in profits]
    bars2 = ax.bar([i + bar_width / 2 for i in x], [v / 1e8 for v in profits],
                    bar_width, color=profit_colors, alpha=0.85, label="영업이익", zorder=2)

    # Value labels
    for bar, val in zip(bars1, revenues):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(revenues) / 1e8 * 0.03,
                f'{val / 1e8:.0f}억', ha='center', va='bottom', fontsize=10, fontweight='bold', color=BLACK)

    for bar, val in zip(bars2, profits):
        y = bar.get_height() if val >= 0 else bar.get_height() - abs(val) / 1e8 * 0.1
        offset = max(revenues) / 1e8 * 0.03 if val >= 0 else -max(revenues) / 1e8 * 0.06
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + offset,
                f'{val / 1e8:.0f}억', ha='center', va='bottom', fontsize=10, fontweight='bold',
                color=GREEN if val >= 0 else RED)

    ax.set_xticks(list(x))
    ax.set_xticklabels(years, fontsize=12, fontweight='bold')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}억"))
    ax.axhline(y=0, color=GRAY, linewidth=0.5, linestyle='-')
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper left", frameon=False, fontsize=11)
    ax.set_title("매출 및 영업이익 전망", fontsize=16, fontweight="bold", pad=15, color=BLACK)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_revenue_growth_chart(pl_data) -> bytes:
    """Render revenue growth line chart."""
    years = pl_data.years
    revenue_row = next((r for r in pl_data.rows if "매출" in r.label and "률" not in r.label), None)
    if not revenue_row or not years:
        return _empty_chart()

    revenues = [_parse_korean_number(revenue_row.values.get(y, "0")) / 1e8 for y in years]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.fill_between(range(len(years)), revenues, alpha=0.1, color=ORANGE)
    ax.plot(range(len(years)), revenues, color=ORANGE, linewidth=3,
            marker="o", markersize=10, markerfacecolor="white",
            markeredgecolor=ORANGE, markeredgewidth=2.5, zorder=3)

    for i, v in enumerate(revenues):
        ax.annotate(f"{v:.0f}억", (i, v), textcoords="offset points",
                    xytext=(0, 15), ha="center", fontsize=11, fontweight="bold", color=ORANGE)

    ax.set_xticks(list(range(len(years))))
    ax.set_xticklabels(years, fontsize=12, fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}억"))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_title("매출 성장 전망", fontsize=16, fontweight="bold", pad=15, color=BLACK)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _empty_chart() -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, "데이터 없음", ha="center", va="center", fontsize=16, color=GRAY)
    ax.set_axis_off()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
