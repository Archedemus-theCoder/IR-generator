"""PPT slide assembly using python-pptx."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from .brand_manager import hex_to_rgb
from .models import BrandTheme, Slide


def _rgb(hex_color: str) -> RGBColor:
    r, g, b = hex_to_rgb(hex_color)
    return RGBColor(r, g, b)


def _add_text_to_shape(
    shape: Any,
    text: str,
    theme: BrandTheme,
    font_size: int | None = None,
    bold: bool = False,
    color: str | None = None,
    alignment: PP_ALIGN = PP_ALIGN.LEFT,
) -> None:
    """Add formatted text to a shape's text frame."""
    tf = shape.text_frame
    tf.word_wrap = True

    # Parse markdown-like formatting
    lines = text.strip().split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        p.alignment = alignment

        # Handle bullet points
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            p.level = 0
            stripped = stripped[2:]
        elif stripped.startswith("  - ") or stripped.startswith("  * "):
            p.level = 1
            stripped = stripped[4:]

        # Parse bold segments **text**
        parts = re.split(r"(\*\*.*?\*\*)", stripped)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = p.add_run()
                run.text = part[2:-2]
                run.font.bold = True
            else:
                run = p.add_run()
                run.text = part

            run.font.size = Pt(font_size or theme.sizes.body)
            run.font.name = theme.fonts.body
            run.font.color.rgb = _rgb(color or theme.colors.text_primary)

        if bold:
            for run in p.runs:
                run.font.bold = True


def _create_blank_slide(prs: Presentation) -> Any:
    """Add a blank slide to the presentation."""
    layout = prs.slide_layouts[6]  # Blank layout
    return prs.slides.add_slide(layout)


def build_title_slide(
    prs: Presentation,
    slide: Slide,
    theme: BrandTheme,
    context: dict[str, Any],
) -> None:
    """Build a title/cover slide."""
    sld = _create_blank_slide(prs)
    width = prs.slide_width
    height = prs.slide_height

    # Background color
    background = sld.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(theme.colors.primary)

    # Title text box
    title_left = Inches(1)
    title_top = Inches(2.5)
    title_width = width - Inches(2)
    title_height = Inches(1.5)
    txBox = sld.shapes.add_textbox(title_left, title_top, title_width, title_height)
    _add_text_to_shape(
        txBox, slide.front_matter.title, theme,
        font_size=theme.sizes.title, bold=True,
        color="#FFFFFF", alignment=PP_ALIGN.CENTER,
    )

    # Subtitle from body
    if slide.rendered_body:
        sub_top = Inches(4.2)
        sub_height = Inches(1)
        txBox2 = sld.shapes.add_textbox(title_left, sub_top, title_width, sub_height)
        first_line = slide.rendered_body.strip().split("\n")[0]
        # Strip markdown headers
        first_line = re.sub(r"^#+\s*", "", first_line)
        _add_text_to_shape(
            txBox2, first_line, theme,
            font_size=theme.sizes.subtitle,
            color="#FFFFFF", alignment=PP_ALIGN.CENTER,
        )


def build_content_slide(
    prs: Presentation,
    slide: Slide,
    theme: BrandTheme,
    context: dict[str, Any],
    chart_path: Path | None = None,
) -> None:
    """Build a standard content slide with title and body text."""
    sld = _create_blank_slide(prs)
    width = prs.slide_width
    height = prs.slide_height

    # Title bar
    title_left = Inches(0.8)
    title_top = Inches(0.5)
    title_width = width - Inches(1.6)
    title_height = Inches(0.8)
    txBox = sld.shapes.add_textbox(title_left, title_top, title_width, title_height)
    _add_text_to_shape(
        txBox, slide.front_matter.title, theme,
        font_size=theme.sizes.subtitle, bold=True,
        color=theme.colors.primary,
    )

    # Divider line
    line_top = Inches(1.35)
    shape = sld.shapes.add_shape(
        1, title_left, line_top, title_width, Pt(2),  # 1 = rectangle
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(theme.colors.accent)
    shape.line.fill.background()

    # Body text
    body_top = Inches(1.6)
    body_height = Inches(5)
    body_width = title_width

    if chart_path and chart_path.exists():
        # If there's a chart, split: text left, chart right
        body_width = Inches(4.5)

    txBox2 = sld.shapes.add_textbox(title_left, body_top, body_width, body_height)
    # Strip markdown headers from body for cleaner display
    body_text = _strip_md_headers(slide.rendered_body)
    _add_text_to_shape(txBox2, body_text, theme, font_size=theme.sizes.body)

    # Chart image if present
    if chart_path and chart_path.exists():
        chart_left = Inches(5.5)
        chart_top = Inches(1.6)
        chart_width = Inches(4.2)
        chart_height = Inches(4.5)
        sld.shapes.add_picture(
            str(chart_path), chart_left, chart_top, chart_width, chart_height,
        )


def build_two_column_slide(
    prs: Presentation,
    slide: Slide,
    theme: BrandTheme,
    context: dict[str, Any],
    chart_path: Path | None = None,
) -> None:
    """Build a two-column slide: text left, chart/image right."""
    sld = _create_blank_slide(prs)
    width = prs.slide_width

    # Title
    title_left = Inches(0.8)
    title_top = Inches(0.5)
    title_width = width - Inches(1.6)
    title_height = Inches(0.8)
    txBox = sld.shapes.add_textbox(title_left, title_top, title_width, title_height)
    _add_text_to_shape(
        txBox, slide.front_matter.title, theme,
        font_size=theme.sizes.subtitle, bold=True,
        color=theme.colors.primary,
    )

    # Divider line
    line_top = Inches(1.35)
    shape = sld.shapes.add_shape(
        1, title_left, line_top, title_width, Pt(2),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(theme.colors.accent)
    shape.line.fill.background()

    # Left column: text
    left_top = Inches(1.6)
    left_width = Inches(4.5)
    left_height = Inches(5)
    txBox2 = sld.shapes.add_textbox(title_left, left_top, left_width, left_height)
    body_text = _strip_md_headers(slide.rendered_body)
    _add_text_to_shape(txBox2, body_text, theme, font_size=theme.sizes.body)

    # Right column: chart or placeholder
    right_left = Inches(5.5)
    right_top = Inches(1.6)
    right_width = Inches(4.2)
    right_height = Inches(4.5)

    if chart_path and chart_path.exists():
        sld.shapes.add_picture(
            str(chart_path), right_left, right_top, right_width, right_height,
        )


def build_metric_highlight_slide(
    prs: Presentation,
    slide: Slide,
    theme: BrandTheme,
    context: dict[str, Any],
) -> None:
    """Build a big metric highlight slide."""
    sld = _create_blank_slide(prs)
    width = prs.slide_width
    height = prs.slide_height

    # Title at top
    title_left = Inches(0.8)
    title_top = Inches(0.5)
    title_width = width - Inches(1.6)
    txBox = sld.shapes.add_textbox(title_left, title_top, title_width, Inches(0.8))
    _add_text_to_shape(
        txBox, slide.front_matter.title, theme,
        font_size=theme.sizes.subtitle, bold=True,
        color=theme.colors.primary,
    )

    # Big metric in center - extract first line as the metric
    body_lines = slide.rendered_body.strip().split("\n")
    metric_text = _strip_md_headers(body_lines[0]) if body_lines else ""
    remaining = "\n".join(body_lines[1:]).strip() if len(body_lines) > 1 else ""

    metric_top = Inches(2.5)
    metric_height = Inches(1.8)
    txBox2 = sld.shapes.add_textbox(title_left, metric_top, title_width, metric_height)
    _add_text_to_shape(
        txBox2, metric_text, theme,
        font_size=theme.sizes.metric_highlight, bold=True,
        color=theme.colors.accent, alignment=PP_ALIGN.CENTER,
    )

    # Supporting text below
    if remaining:
        sub_top = Inches(4.5)
        sub_height = Inches(2)
        txBox3 = sld.shapes.add_textbox(title_left, sub_top, title_width, sub_height)
        _add_text_to_shape(
            txBox3, _strip_md_headers(remaining), theme,
            font_size=theme.sizes.body, alignment=PP_ALIGN.CENTER,
        )


def build_table_slide(
    prs: Presentation,
    slide: Slide,
    theme: BrandTheme,
    context: dict[str, Any],
) -> None:
    """Build a financial table slide from context data."""
    sld = _create_blank_slide(prs)
    width = prs.slide_width

    # Title
    title_left = Inches(0.8)
    title_top = Inches(0.5)
    title_width = width - Inches(1.6)
    txBox = sld.shapes.add_textbox(title_left, title_top, title_width, Inches(0.8))
    _add_text_to_shape(
        txBox, slide.front_matter.title, theme,
        font_size=theme.sizes.subtitle, bold=True,
        color=theme.colors.primary,
    )

    # Build a P&L summary table from context
    periods = context.get("periods", [])[:8]  # Max 8 columns
    revenue = context.get("revenue_by_period", [])[:8]
    costs = context.get("costs_by_period", [])[:8]
    profit = context.get("profit_by_period", [])[:8]

    if not periods:
        # Fallback to body text if no data
        build_content_slide(prs, slide, theme, context)
        return

    rows = 4  # Header, Revenue, Costs, Profit
    cols = len(periods) + 1  # Label + periods

    table_left = Inches(0.8)
    table_top = Inches(1.6)
    table_width = width - Inches(1.6)
    table_height = Inches(3)

    table_shape = sld.shapes.add_table(rows, cols, table_left, table_top, table_width, table_height)
    table = table_shape.table

    # Header row
    _set_cell(table.cell(0, 0), "", theme, bold=True, header=True)
    for i, p in enumerate(periods):
        _set_cell(table.cell(0, i + 1), p, theme, bold=True, header=True)

    # Data rows
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


def _set_cell(
    cell: Any,
    text: str,
    theme: BrandTheme,
    bold: bool = False,
    header: bool = False,
    color: str | None = None,
) -> None:
    """Set cell text with formatting."""
    cell.text = text
    for paragraph in cell.text_frame.paragraphs:
        paragraph.alignment = PP_ALIGN.RIGHT if not bold or header else PP_ALIGN.LEFT
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


def _format_table_number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:,.0f}K"
    return f"${value:,.0f}"


def _strip_md_headers(text: str) -> str:
    """Remove markdown header prefixes (## ) from text."""
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


def create_presentation(
    slides: list[Slide],
    theme: BrandTheme,
    context: dict[str, Any],
    chart_paths: dict[str, Path],
    base_template: Path | None = None,
    output_path: Path = Path("output/deck.pptx"),
) -> Path:
    """Create a full PowerPoint presentation from slides."""
    if base_template and base_template.exists():
        prs = Presentation(str(base_template))
    else:
        prs = Presentation()
        prs.slide_width = Inches(13.333)  # Widescreen 16:9
        prs.slide_height = Inches(7.5)

    for slide in slides:
        layout = slide.front_matter.layout
        builder = LAYOUT_BUILDERS.get(layout, build_content_slide)

        chart_path = chart_paths.get(slide.front_matter.chart) if slide.front_matter.chart else None

        if layout in ("content", "two_column"):
            builder(prs, slide, theme, context, chart_path=chart_path)
        elif layout == "table":
            builder(prs, slide, theme, context)
        else:
            builder(prs, slide, theme, context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return output_path
