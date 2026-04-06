"""Matplotlib chart generation for IR slides."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from .brand_manager import hex_to_rgb
from .models import BrandTheme


def _apply_theme(theme: BrandTheme) -> None:
    """Apply brand theme to matplotlib defaults."""
    colors = theme.colors
    plt.rcParams.update({
        "figure.facecolor": colors.background,
        "axes.facecolor": colors.background,
        "axes.edgecolor": colors.text_secondary,
        "axes.labelcolor": colors.text_primary,
        "text.color": colors.text_primary,
        "xtick.color": colors.text_secondary,
        "ytick.color": colors.text_secondary,
        "grid.color": "#E5E7EB",
        "grid.alpha": 0.5,
        "font.family": "sans-serif",
        "font.size": 12,
    })


def _format_currency_axis(ax: plt.Axes) -> None:
    """Format y-axis with currency labels."""
    def fmt(x, _):
        if abs(x) >= 1_000_000:
            return f"${x/1_000_000:.1f}M"
        if abs(x) >= 1_000:
            return f"${x/1_000:.0f}K"
        return f"${x:,.0f}"
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt))


def render_revenue_chart(
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path:
    """Render a revenue bar chart with cost overlay line."""
    _apply_theme(theme)
    colors = theme.colors

    periods = context.get("periods", [])
    revenue = context.get("revenue_by_period", [])
    costs = context.get("costs_by_period", [])
    profit = context.get("profit_by_period", [])

    fig, ax = plt.subplots(figsize=(10, 5.5))

    x = range(len(periods))
    bar_colors = [colors.positive if p >= 0 else colors.negative for p in profit]

    ax.bar(x, revenue, color=colors.primary, alpha=0.85, label="Revenue", zorder=2)
    ax.plot(x, costs, color=colors.accent, linewidth=2.5, marker="o",
            markersize=6, label="Costs", zorder=3)

    # Profit/loss annotation on bars
    for i, (r, p) in enumerate(zip(revenue, profit)):
        if r > 0:
            ax.text(i, r + max(revenue) * 0.02, _compact_num(r),
                    ha="center", va="bottom", fontsize=9, color=colors.text_secondary)

    ax.set_xticks(list(x))
    ax.set_xticklabels(periods, rotation=45, ha="right", fontsize=10)
    _format_currency_axis(ax)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Revenue vs. Costs", fontsize=16, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--")

    plt.tight_layout()

    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".png"))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_pl_summary_chart(
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path:
    """Render a P&L summary stacked bar chart."""
    _apply_theme(theme)
    colors = theme.colors

    periods = context.get("periods", [])
    revenue_items = context.get("revenue_items", {})
    cost_items = context.get("cost_items", {})

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = range(len(periods))
    palette = [colors.primary, colors.secondary, colors.accent, "#6366F1", "#EC4899"]

    # Stack revenue bars
    bottom = [0.0] * len(periods)
    for i, (key, item) in enumerate(revenue_items.items()):
        values = item["values"]
        color = palette[i % len(palette)]
        ax.bar(x, values, bottom=bottom, color=color, alpha=0.85,
               label=item["label"], zorder=2)
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_xticks(list(x))
    ax.set_xticklabels(periods, rotation=45, ha="right", fontsize=10)
    _format_currency_axis(ax)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("Revenue Breakdown", fontsize=16, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--")

    plt.tight_layout()

    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".png"))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_growth_line_chart(
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path:
    """Render a growth trend line chart."""
    _apply_theme(theme)
    colors = theme.colors

    periods = context.get("periods", [])
    revenue = context.get("revenue_by_period", [])

    # Compute period-over-period growth rates
    growth_rates = [0.0]
    for i in range(1, len(revenue)):
        if revenue[i - 1] > 0:
            growth_rates.append((revenue[i] - revenue[i - 1]) / revenue[i - 1])
        else:
            growth_rates.append(0.0)

    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    ax1.fill_between(range(len(periods)), revenue, alpha=0.15, color=colors.primary)
    ax1.plot(range(len(periods)), revenue, color=colors.primary, linewidth=2.5,
             marker="o", markersize=6, label="Revenue")
    _format_currency_axis(ax1)
    ax1.set_ylabel("Revenue", color=colors.primary)

    ax2 = ax1.twinx()
    ax2.bar(range(len(periods)), [g * 100 for g in growth_rates],
            alpha=0.3, color=colors.accent, label="Growth %", zorder=1)
    ax2.set_ylabel("Growth %", color=colors.accent)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    ax1.set_xticks(list(range(len(periods))))
    ax1.set_xticklabels(periods, rotation=45, ha="right", fontsize=10)
    ax1.set_title("Revenue Growth Trend", fontsize=16, fontweight="bold", pad=12)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False)

    plt.tight_layout()

    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".png"))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_cost_breakdown_donut(
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path:
    """Render a donut chart showing cost breakdown."""
    _apply_theme(theme)
    colors = theme.colors
    palette = [colors.primary, colors.secondary, colors.accent, "#6366F1", "#EC4899"]

    cost_items = context.get("cost_items", {})
    if not cost_items:
        return render_revenue_chart(context, theme, output_path)

    labels = [item["label"] for item in cost_items.values()]
    totals = [sum(item["values"]) for item in cost_items.values()]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        totals, labels=None, autopct="%1.0f%%",
        colors=palette[:len(totals)],
        startangle=90, pctdistance=0.75,
        wedgeprops={"width": 0.4, "edgecolor": "white", "linewidth": 2},
    )

    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    # Center text
    total = sum(totals)
    ax.text(0, 0.05, _compact_num(total), ha="center", va="center",
            fontsize=22, fontweight="bold", color=colors.text_primary)
    ax.text(0, -0.12, "Total Costs", ha="center", va="center",
            fontsize=11, color=colors.text_secondary)

    ax.legend(labels, loc="lower center", ncol=2, frameon=False,
              fontsize=10, bbox_to_anchor=(0.5, -0.05))
    ax.set_title("Cost Structure", fontsize=16, fontweight="bold", pad=20)

    plt.tight_layout()
    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".png"))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_margin_trend(
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path:
    """Render margin trend with area fill."""
    _apply_theme(theme)
    colors = theme.colors

    periods = context.get("periods", [])
    revenue = context.get("revenue_by_period", [])
    costs = context.get("costs_by_period", [])

    margins = []
    for r, c in zip(revenue, costs):
        margins.append((r - c) / r * 100 if r > 0 else 0)

    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Fill area
    ax.fill_between(range(len(periods)), margins, alpha=0.15, color=colors.primary)
    ax.plot(range(len(periods)), margins, color=colors.primary, linewidth=3,
            marker="o", markersize=8, markerfacecolor="white",
            markeredgecolor=colors.primary, markeredgewidth=2)

    # Zero line
    ax.axhline(y=0, color=colors.negative, linestyle="--", alpha=0.5, linewidth=1)

    # Annotate each point
    for i, m in enumerate(margins):
        offset = 8 if m >= 0 else -15
        ax.annotate(f"{m:.0f}%", (i, m), textcoords="offset points",
                   xytext=(0, offset), ha="center", fontsize=10,
                   fontweight="bold", color=colors.primary)

    ax.set_xticks(list(range(len(periods))))
    ax.set_xticklabels(periods, rotation=45, ha="right", fontsize=10)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_title("Gross Margin Trend", fontsize=16, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    plt.tight_layout()
    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".png"))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_revenue_breakdown_bar(
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path:
    """Render stacked bar chart of revenue breakdown by source."""
    _apply_theme(theme)
    colors = theme.colors
    palette = [colors.primary, colors.secondary, colors.accent, "#6366F1"]

    periods = context.get("periods", [])
    revenue_items = context.get("revenue_items", {})

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = range(len(periods))

    bottom = [0.0] * len(periods)
    for i, (key, item) in enumerate(revenue_items.items()):
        values = item["values"]
        color = palette[i % len(palette)]
        bars = ax.bar(x, values, bottom=bottom, color=color, alpha=0.9,
                      label=item["label"], zorder=2, edgecolor="white", linewidth=0.5)
        bottom = [b + v for b, v in zip(bottom, values)]

    # Total labels on top
    for i, total in enumerate(bottom):
        ax.text(i, total + max(bottom) * 0.02, _compact_num(total),
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                color=colors.text_secondary)

    ax.set_xticks(list(x))
    ax.set_xticklabels(periods, rotation=45, ha="right", fontsize=10)
    _format_currency_axis(ax)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax.set_title("Revenue Breakdown", fontsize=16, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    plt.tight_layout()
    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".png"))
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


# Chart registry
CHART_REGISTRY: dict[str, Any] = {
    "revenue_chart": render_revenue_chart,
    "pl_summary": render_pl_summary_chart,
    "growth_line": render_growth_line_chart,
    "cost_donut": render_cost_breakdown_donut,
    "margin_trend": render_margin_trend,
    "revenue_breakdown": render_revenue_breakdown_bar,
}


def render_chart(
    chart_name: str,
    context: dict[str, Any],
    theme: BrandTheme,
    output_path: Path | None = None,
) -> Path | None:
    """Render a chart by name from the registry."""
    renderer = CHART_REGISTRY.get(chart_name)
    if renderer is None:
        return None
    return renderer(context, theme, output_path)


def _compact_num(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:,.0f}"
