"""PPT slide assembly using python-pptx — polished visual output."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from .brand_manager import hex_to_rgb
from .models import BrandTheme, Slide


def _rgb(hex_color: str) -> RGBColor:
    r, g, b = hex_to_rgb(hex_color)
    return RGBColor(r, g, b)


def _add_rounded_rect(sld, left, top, width, height, hex_color, alpha=1.0):
    """Add a rounded rectangle background shape."""
    shape = sld.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height,
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(hex_color)
    shape.line.fill.background()
    shape.shadow.inherit = False
    # Adjust corner radius
    shape.adjustments[0] = 0.05
    return shape


def _add_rect(sld, left, top, width, height, hex_color):
    """Add a simple rectangle shape."""
    shape = sld.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height,
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(hex_color)
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _add_circle(sld, left, top, size, hex_color):
    """Add a circle shape."""
    shape = sld.shapes.add_shape(
        MSO_SHAPE.OVAL, left, top, size, size,
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(hex_color)
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _add_text_box(
    sld, left, top, width, height, text, theme,
    font_size=16, bold=False, color=None, alignment=PP_ALIGN.LEFT,
    font_name=None, vertical_anchor=None,
):
    """Add a text box with formatted text. Returns the shape."""
    txBox = sld.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    if vertical_anchor:
        tf.auto_size = None
        txBox.text_frame.paragraphs[0].alignment = alignment

    _populate_text_frame(tf, text, theme, font_size, bold, color, alignment, font_name)
    return txBox


def _populate_text_frame(
    tf, text, theme, font_size=16, bold=False, color=None,
    alignment=PP_ALIGN.LEFT, font_name=None,
):
    """Populate a text frame with markdown-parsed text."""
    lines = text.strip().split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        p.alignment = alignment
        p.space_after = Pt(4)
        p.space_before = Pt(2)

        stripped = line.strip()
        if not stripped:
            run = p.add_run()
            run.text = ""
            run.font.size = Pt(8)
            continue

        # Bullet handling with proper indent
        indent_level = None
        if stripped.startswith("- ") or stripped.startswith("* "):
            indent_level = 0
            stripped = stripped[2:]
        elif stripped.startswith("  - ") or stripped.startswith("  * "):
            indent_level = 1
            stripped = stripped[4:]

        if indent_level is not None:
            p.level = indent_level
            p.space_before = Pt(4)

        # Parse bold **text** segments
        parts = re.split(r"(\*\*.*?\*\*)", stripped)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run()
                run.text = part[2:-2]
                run.font.bold = True
            else:
                run = p.add_run()
                run.text = part

            run.font.size = Pt(font_size)
            run.font.name = font_name or theme.fonts.body
            run.font.color.rgb = _rgb(color or theme.colors.text_primary)

        if bold:
            for run in p.runs:
                run.font.bold = True


def _add_slide_number(sld, prs, theme, slide_num):
    """Add slide number in bottom right."""
    width = prs.slide_width
    height = prs.slide_height
    txBox = sld.shapes.add_textbox(
        width - Inches(1), height - Inches(0.5), Inches(0.7), Inches(0.3),
    )
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = str(slide_num)
    run.font.size = Pt(10)
    run.font.color.rgb = _rgb(theme.colors.text_secondary)
    run.font.name = theme.fonts.body


def _add_title_bar(sld, prs, title, theme):
    """Add consistent title bar with accent divider."""
    width = prs.slide_width
    title_left = Inches(0.8)
    title_top = Inches(0.4)
    title_width = width - Inches(1.6)

    # Title text
    _add_text_box(
        sld, title_left, title_top, title_width, Inches(0.7),
        title, theme,
        font_size=theme.sizes.subtitle, bold=True,
        color=theme.colors.primary, font_name=theme.fonts.heading,
    )

    # Accent divider line
    _add_rect(sld, title_left, Inches(1.15), Inches(1.5), Pt(3), theme.colors.accent)

    return title_left, title_width


# =====================================================
# SLIDE BUILDERS
# =====================================================

def build_title_slide(prs, slide, theme, context, **kwargs):
    """Cover slide with full background and centered title."""
    sld = prs.slides.add_slide(prs.slide_layouts[6])
    width = prs.slide_width
    height = prs.slide_height

    # Full background
    bg = sld.background.fill
    bg.solid()
    bg.fore_color.rgb = _rgb(theme.colors.primary)

    # Decorative accent bar at top
    _add_rect(sld, Inches(0), Inches(0), width, Inches(0.15), theme.colors.accent)

    # Title
    _add_text_box(
        sld, Inches(1.5), Inches(2.2), width - Inches(3), Inches(1.8),
        slide.front_matter.title, theme,
        font_size=44, bold=True, color="#FFFFFF",
        alignment=PP_ALIGN.CENTER, font_name=theme.fonts.heading,
    )

    # Subtitle from body
    if slide.rendered_body:
        first_line = re.sub(r"^#+\s*", "", slide.rendered_body.strip().split("\n")[0])
        _add_text_box(
            sld, Inches(2), Inches(4.2), width - Inches(4), Inches(0.8),
            first_line, theme,
            font_size=20, color="#FFFFFF",
            alignment=PP_ALIGN.CENTER,
        )

    # Bottom accent bar
    _add_rect(sld, Inches(0), height - Inches(0.08), width, Inches(0.08), theme.colors.accent)


def build_content_slide(prs, slide, theme, context, chart_path=None, **kwargs):
    """Content slide with title bar and body text, optional chart."""
    sld = prs.slides.add_slide(prs.slide_layouts[6])
    width = prs.slide_width
    height = prs.slide_height

    # Light background stripe at top
    _add_rect(sld, Inches(0), Inches(0), width, Inches(1.3), "#F8F9FA")

    title_left, title_width = _add_title_bar(sld, prs, slide.front_matter.title, theme)

    # Body text
    body_top = Inches(1.5)
    body_height = Inches(5.2)

    if chart_path and chart_path.exists():
        body_width = Inches(5)
        _add_text_box(
            sld, title_left, body_top, body_width, body_height,
            _strip_md_headers(slide.rendered_body), theme,
            font_size=theme.sizes.body,
        )
        # Chart on right with subtle card background
        card_left = Inches(6.3)
        card_top = Inches(1.5)
        card_w = Inches(6.2)
        card_h = Inches(5.2)
        _add_rounded_rect(sld, card_left, card_top, card_w, card_h, "#F8F9FA")
        sld.shapes.add_picture(
            str(chart_path),
            card_left + Inches(0.2), card_top + Inches(0.2),
            card_w - Inches(0.4), card_h - Inches(0.4),
        )
    else:
        _add_text_box(
            sld, title_left, body_top, title_width, body_height,
            _strip_md_headers(slide.rendered_body), theme,
            font_size=theme.sizes.body,
        )

    _add_slide_number(sld, prs, theme, len(prs.slides))


def build_two_column_slide(prs, slide, theme, context, chart_path=None, **kwargs):
    """Two-column: text left, chart/visual right."""
    sld = prs.slides.add_slide(prs.slide_layouts[6])
    width = prs.slide_width

    _add_rect(sld, Inches(0), Inches(0), width, Inches(1.3), "#F8F9FA")
    title_left, title_width = _add_title_bar(sld, prs, slide.front_matter.title, theme)

    # Left column text
    _add_text_box(
        sld, title_left, Inches(1.5), Inches(5.2), Inches(5.2),
        _strip_md_headers(slide.rendered_body), theme,
        font_size=theme.sizes.body,
    )

    # Right column
    right_left = Inches(6.5)
    right_top = Inches(1.5)
    right_w = Inches(6)
    right_h = Inches(5.2)

    if chart_path and chart_path.exists():
        _add_rounded_rect(sld, right_left, right_top, right_w, right_h, "#F8F9FA")
        sld.shapes.add_picture(
            str(chart_path),
            right_left + Inches(0.2), right_top + Inches(0.2),
            right_w - Inches(0.4), right_h - Inches(0.4),
        )
    else:
        # If no chart, show key metrics as cards from context
        _build_metric_cards(sld, theme, context, right_left, right_top, right_w)

    _add_slide_number(sld, prs, theme, len(prs.slides))


def build_metric_highlight_slide(prs, slide, theme, context, **kwargs):
    """Big metric with supporting KPI cards below."""
    sld = prs.slides.add_slide(prs.slide_layouts[6])
    width = prs.slide_width
    height = prs.slide_height

    _add_rect(sld, Inches(0), Inches(0), width, Inches(1.3), "#F8F9FA")
    _add_title_bar(sld, prs, slide.front_matter.title, theme)

    body_lines = slide.rendered_body.strip().split("\n")
    metric_text = _strip_md_headers(body_lines[0]) if body_lines else ""
    supporting_lines = [l.strip() for l in body_lines[1:] if l.strip()]

    # Big metric — centered with accent color
    _add_text_box(
        sld, Inches(1), Inches(1.8), width - Inches(2), Inches(1.8),
        metric_text, theme,
        font_size=64, bold=True, color=theme.colors.accent,
        alignment=PP_ALIGN.CENTER, font_name=theme.fonts.heading,
    )

    # Supporting metrics as cards
    metric_items = []
    for line in supporting_lines:
        line = line.lstrip("- *")
        if line:
            metric_items.append(line)

    if metric_items:
        num_cards = min(len(metric_items), 4)
        card_width = Inches(2.5)
        total_cards_width = num_cards * card_width + (num_cards - 1) * Inches(0.3)
        start_left = (width - total_cards_width) // 2

        for idx, item in enumerate(metric_items[:4]):
            card_left = start_left + idx * (card_width + Inches(0.3))
            card_top = Inches(4.0)
            card_h = Inches(2.2)

            # Card background
            _add_rounded_rect(sld, card_left, card_top, card_width, card_h, "#F8F9FA")

            # Accent top border on card
            _add_rect(
                sld, card_left + Inches(0.1), card_top + Inches(0.08),
                card_width - Inches(0.2), Pt(4),
                [theme.colors.primary, theme.colors.secondary, theme.colors.accent, theme.colors.positive][idx % 4],
            )

            # Split into value and label if possible (e.g., "150+ enterprise customers")
            parts = item.split(" ", 1)
            if parts[0] and any(c.isdigit() for c in parts[0]):
                value_text = parts[0]
                label_text = parts[1] if len(parts) > 1 else ""
            else:
                value_text = ""
                label_text = item

            if value_text:
                _add_text_box(
                    sld, card_left + Inches(0.2), card_top + Inches(0.4),
                    card_width - Inches(0.4), Inches(0.8),
                    value_text, theme,
                    font_size=28, bold=True,
                    color=theme.colors.primary,
                    alignment=PP_ALIGN.CENTER, font_name=theme.fonts.heading,
                )
                _add_text_box(
                    sld, card_left + Inches(0.2), card_top + Inches(1.3),
                    card_width - Inches(0.4), Inches(0.6),
                    label_text, theme,
                    font_size=11, color=theme.colors.text_secondary,
                    alignment=PP_ALIGN.CENTER,
                )
            else:
                _add_text_box(
                    sld, card_left + Inches(0.2), card_top + Inches(0.6),
                    card_width - Inches(0.4), Inches(1.2),
                    label_text, theme,
                    font_size=13, color=theme.colors.text_primary,
                    alignment=PP_ALIGN.CENTER,
                )

    _add_slide_number(sld, prs, theme, len(prs.slides))


def build_table_slide(prs, slide, theme, context, **kwargs):
    """Financial table with styled header and alternating rows."""
    sld = prs.slides.add_slide(prs.slide_layouts[6])
    width = prs.slide_width

    _add_rect(sld, Inches(0), Inches(0), width, Inches(1.3), "#F8F9FA")
    title_left, title_width = _add_title_bar(sld, prs, slide.front_matter.title, theme)

    periods = context.get("periods", [])[:8]
    revenue = context.get("revenue_by_period", [])[:8]
    costs = context.get("costs_by_period", [])[:8]
    profit = context.get("profit_by_period", [])[:8]

    if not periods:
        build_content_slide(prs, slide, theme, context)
        return

    rows = 4
    cols = len(periods) + 1

    table_left = Inches(0.8)
    table_top = Inches(1.6)
    table_width = width - Inches(1.6)
    table_height = Inches(3.2)

    table_shape = sld.shapes.add_table(rows, cols, table_left, table_top, table_width, table_height)
    table = table_shape.table

    # Style header row
    _set_cell(table.cell(0, 0), "", theme, bold=True, header=True)
    for i, p in enumerate(periods):
        _set_cell(table.cell(0, i + 1), p, theme, bold=True, header=True)

    row_data = [
        ("Revenue", revenue, theme.colors.primary),
        ("Costs", costs, theme.colors.text_primary),
        ("Profit", profit, None),
    ]

    for row_idx, (label, values, color) in enumerate(row_data, start=1):
        _set_cell(table.cell(row_idx, 0), label, theme, bold=True)
        for col_idx, val in enumerate(values):
            text = _format_table_number(val)
            cell_color = color
            if label == "Profit":
                cell_color = theme.colors.positive if val >= 0 else theme.colors.negative
            _set_cell(table.cell(row_idx, col_idx + 1), text, theme, color=cell_color)

        # Alternating row backgrounds
        if row_idx % 2 == 0:
            for c in range(cols):
                table.cell(row_idx, c).fill.solid()
                table.cell(row_idx, c).fill.fore_color.rgb = _rgb("#F8F9FA")

    _add_slide_number(sld, prs, theme, len(prs.slides))


def _build_metric_cards(sld, theme, context, left, top, total_width):
    """Build auto-generated metric cards when no chart is specified."""
    # Extract key metrics from context
    metrics = []
    years = sorted(set(
        k.split("_")[-1]
        for k in context
        if k.startswith("total_revenue_") and k.split("_")[-1].isdigit()
    ))

    if years:
        latest = years[-1]
        rev = context.get(f"total_revenue_{latest}", 0)
        margin = context.get(f"gross_margin_{latest}", 0)
        profit = context.get(f"gross_profit_{latest}", 0)
        metrics = [
            (f"${rev/1_000_000:.1f}M" if rev >= 1_000_000 else f"${rev/1_000:.0f}K", f"FY{latest} Revenue"),
            (f"{margin*100:.0f}%", f"FY{latest} Gross Margin"),
            (f"${profit/1_000_000:.1f}M" if abs(profit) >= 1_000_000 else f"${profit/1_000:.0f}K", f"FY{latest} Profit"),
        ]

    if not metrics:
        return

    card_h = Inches(1.4)
    gap = Inches(0.2)

    for idx, (value, label) in enumerate(metrics[:3]):
        card_top = top + idx * (card_h + gap)
        _add_rounded_rect(sld, left, card_top, total_width, card_h, "#F8F9FA")

        # Color accent on left edge
        accent_colors = [theme.colors.primary, theme.colors.accent, theme.colors.positive]
        _add_rect(sld, left, card_top + Inches(0.15), Inches(0.08), card_h - Inches(0.3), accent_colors[idx % 3])

        _add_text_box(
            sld, left + Inches(0.3), card_top + Inches(0.15),
            total_width - Inches(0.5), Inches(0.7),
            value, theme,
            font_size=26, bold=True, color=theme.colors.primary,
            font_name=theme.fonts.heading,
        )
        _add_text_box(
            sld, left + Inches(0.3), card_top + Inches(0.85),
            total_width - Inches(0.5), Inches(0.4),
            label, theme,
            font_size=12, color=theme.colors.text_secondary,
        )


def _set_cell(cell, text, theme, bold=False, header=False, color=None):
    """Set cell text with formatting."""
    cell.text = text
    for paragraph in cell.text_frame.paragraphs:
        paragraph.alignment = PP_ALIGN.RIGHT if not header and not bold else PP_ALIGN.CENTER if header else PP_ALIGN.LEFT
        for run in paragraph.runs:
            run.font.size = Pt(11)
            run.font.name = theme.fonts.body
            run.font.bold = bold
            if color:
                run.font.color.rgb = _rgb(color)
            elif header:
                run.font.color.rgb = _rgb("#FFFFFF")

    if header:
        cell.fill.solid()
        cell.fill.fore_color.rgb = _rgb(theme.colors.primary)


def _format_table_number(value):
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:,.0f}K"
    return f"${value:,.0f}"


def _strip_md_headers(text):
    """Remove markdown header prefixes."""
    lines = []
    for line in text.split("\n"):
        lines.append(re.sub(r"^#+\s*", "", line))
    return "\n".join(lines)


# Layout builder registry
LAYOUT_BUILDERS = {
    "title": build_title_slide,
    "content": build_content_slide,
    "two_column": build_two_column_slide,
    "metric_highlight": build_metric_highlight_slide,
    "table": build_table_slide,
}


def create_presentation(slides, theme, context, chart_paths,
                        base_template=None, output_path=Path("output/deck.pptx")):
    """Create a full PowerPoint presentation from slides."""
    if base_template and base_template.exists():
        prs = Presentation(str(base_template))
    else:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

    for slide in slides:
        layout = slide.front_matter.layout
        builder = LAYOUT_BUILDERS.get(layout, build_content_slide)
        chart_path = chart_paths.get(slide.front_matter.chart) if slide.front_matter.chart else None
        builder(prs, slide, theme, context, chart_path=chart_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return output_path
