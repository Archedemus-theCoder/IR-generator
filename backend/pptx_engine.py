"""PPT generation engine — Rovothome brand design."""

from __future__ import annotations
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from schema import IRDocument

# --- Brand constants ---
W, H = 13.333, 7.5  # 16:9 widescreen
M = 0.7  # Margin

ORANGE = "#E8470A"
BLACK = "#111111"
WHITE = "#FFFFFF"
GRAY = "#F5F5F5"
DARK_GRAY = "#808080"
CARD_BG = "#F2F2F2"
HEADER_BG = "#1A1A1A"

FONT_KR = "Arial"  # Fallback (Pretendard won't be on all systems)
FONT_EN = "Arial"


def _rgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rect(sld, l, t, w, h, color):
    s = sld.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = _rgb(color)
    s.line.fill.background(); s.shadow.inherit = False
    return s


def _rrect(sld, l, t, w, h, color):
    s = sld.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = _rgb(color)
    s.line.fill.background(); s.shadow.inherit = False; s.adjustments[0] = 0.03
    return s


def _tb(sld, l, t, w, h, text, size=14, bold=False, color=BLACK, align=PP_ALIGN.LEFT, font=FONT_KR):
    """Add text box with orange-highlight support: <<text>> becomes orange."""
    tb = sld.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    import re
    lines = text.strip().split("\n") if text.strip() else [""]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(3)
        stripped = line.strip()
        if not stripped:
            r = p.add_run(); r.text = " "; r.font.size = Pt(6); continue
        # Bullet
        if stripped.startswith("- ") or stripped.startswith("• "):
            p.level = 0; stripped = stripped[2:]
        # Parse <<orange>> and **bold**
        parts = re.split(r"(<<.*?>>|\*\*.*?\*\*)", stripped)
        for part in parts:
            r = p.add_run()
            if part.startswith("<<") and part.endswith(">>"):
                r.text = part[2:-2]; r.font.color.rgb = _rgb(ORANGE); r.font.bold = True
            elif part.startswith("**") and part.endswith("**"):
                r.text = part[2:-2]; r.font.bold = True; r.font.color.rgb = _rgb(color)
            else:
                r.text = part; r.font.color.rgb = _rgb(color)
                if bold: r.font.bold = True
            r.font.size = Pt(size); r.font.name = font
    return tb


def _slide_num(sld, n):
    _tb(sld, W - 0.8, 0.25, 0.5, 0.3, str(n), size=12, color=DARK_GRAY, align=PP_ALIGN.RIGHT)


def _section_label(sld, text):
    _tb(sld, M, 0.4, 8, 0.35, text, size=15, bold=True, color=ORANGE, font=FONT_EN)


def _headline(sld, text, top=0.85, width=None):
    w = width or (W - M * 2)
    _tb(sld, M, top, w, 1.6, text, size=26, bold=True, color=BLACK, font=FONT_KR)


def _card_header(sld, text, l, t, w):
    _rect(sld, l, t, w, 0.42, HEADER_BG)
    _tb(sld, l + 0.15, t + 0.05, w - 0.3, 0.32, text, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


# ===== SLIDE BUILDERS =====

def _build_cover(prs, d, n):
    sld = _blank(prs)
    bg = sld.background.fill; bg.solid(); bg.fore_color.rgb = _rgb(BLACK)
    _rect(sld, 0, 0, W, 0.12, ORANGE)
    _tb(sld, 1.5, 1.5, W - 3, 1.2, d.company_name, size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font=FONT_EN)
    _tb(sld, 2, 3.0, W - 4, 0.8, d.tagline, size=18, color=WHITE, align=PP_ALIGN.CENTER)
    # KPI cards
    if d.kpis:
        nc = len(d.kpis)
        cw, gap = 3.2, 0.3
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, k in enumerate(d.kpis):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 4.2, cw, 1.3, "#222222")
            _tb(sld, cx + 0.2, 4.3, cw - 0.4, 0.6, k.value, size=22, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.2, 4.9, cw - 0.4, 0.4, k.label, size=10, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    # Contact
    c = d.contact
    _tb(sld, 2, 6.2, W - 4, 0.4, f"{c.name}  |  {c.phone}  |  {c.email}", size=11, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    _rect(sld, 0, H - 0.08, W, 0.08, ORANGE)


def _build_problem(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.body:
        _tb(sld, M, 2.6, W - M * 2, 0.8, d.body, size=14, color="#555555")
    # Data cards
    if d.data_cards:
        nc = len(d.data_cards)
        cw, gap = 3.5, 0.3
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, c in enumerate(d.data_cards):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.8, cw, 2.5, CARD_BG)
            _rect(sld, cx + 0.15, 3.9, cw - 0.3, 0.05, [ORANGE, BLACK, DARK_GRAY][i % 3])
            _tb(sld, cx + 0.3, 4.2, cw - 0.6, 0.9, c.value, size=28, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.3, 5.2, cw - 0.6, 0.5, c.label, size=12, color=DARK_GRAY, align=PP_ALIGN.CENTER)


def _build_solution(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    pw, gap = 5.8, 0.4
    # Left panel
    lx = M
    _rrect(sld, lx, 2.8, pw, 3.8, CARD_BG)
    _card_header(sld, d.left_title, lx, 2.8, pw)
    _tb(sld, lx + 0.3, 3.4, pw - 0.6, 2.8, d.left_desc, size=14, color=BLACK)
    # Right panel
    rx = M + pw + gap
    _rrect(sld, rx, 2.8, pw, 3.8, CARD_BG)
    _card_header(sld, d.right_title, rx, 2.8, pw)
    _tb(sld, rx + 0.3, 3.4, pw - 0.6, 2.8, d.right_desc, size=14, color=BLACK)


def _build_why_now(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.points:
        nc = len(d.points)
        cw, gap = 3.5, 0.3
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, p in enumerate(d.points):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.2, cw, 3.2, CARD_BG)
            accent = [ORANGE, BLACK, "#2ECC71"][i % 3]
            _rect(sld, cx + 0.15, 3.3, cw - 0.3, 0.05, accent)
            _tb(sld, cx + 0.3, 3.6, cw - 0.6, 0.6, p.label, size=18, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.3, 4.4, cw - 0.6, 1.5, p.sub, size=13, color="#555555", align=PP_ALIGN.CENTER)


def _build_market_size(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    # TAM/SAM/SOM cards
    items = [d.tam, d.sam, d.som]
    sizes = [4.0, 3.2, 2.6]  # Decreasing card widths for visual hierarchy
    colors = [ORANGE, BLACK, DARK_GRAY]
    sx = (W - sum(sizes) - 0.6) / 2
    cx = sx
    for i, (item, cw, clr) in enumerate(zip(items, sizes, colors)):
        _rrect(sld, cx, 3.0, cw, 3.0, CARD_BG)
        _tb(sld, cx + 0.2, 3.3, cw - 0.4, 0.5, item.label, size=14, bold=True, color=DARK_GRAY, align=PP_ALIGN.CENTER)
        _tb(sld, cx + 0.2, 3.8, cw - 0.4, 1.0, item.value, size=36, bold=True, color=clr, align=PP_ALIGN.CENTER)
        cx += cw + 0.3
    if d.growth_note:
        _tb(sld, M, 6.3, W - M * 2, 0.4, d.growth_note, size=13, color=DARK_GRAY, align=PP_ALIGN.CENTER)


def _build_business_model(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.model_types:
        nc = len(d.model_types)
        cw, gap = 3.5, 0.3
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, m in enumerate(d.model_types):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.2, cw, 3.5, CARD_BG)
            _card_header(sld, m.label, cx, 3.2, cw)
            _tb(sld, cx + 0.3, 3.8, cw - 0.6, 0.6, m.value, size=15, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.3, 4.5, cw - 0.6, 1.5, m.sub, size=12, color="#555555", align=PP_ALIGN.CENTER)


def _build_traction(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.items:
        nc = len(d.items)
        cw, gap = 3.5, 0.3
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, item in enumerate(d.items):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.2, cw, 3.2, CARD_BG)
            accent = [ORANGE, BLACK, "#2ECC71"][i % 3]
            _rect(sld, cx + 0.15, 3.3, cw - 0.3, 0.05, accent)
            _tb(sld, cx + 0.3, 3.6, cw - 0.6, 0.5, item.label, size=14, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.3, 4.2, cw - 0.6, 0.7, item.value, size=22, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.3, 5.0, cw - 0.6, 0.8, item.sub, size=12, color="#555555", align=PP_ALIGN.CENTER)


def _build_tech_moat(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.moats:
        nc = min(len(d.moats), 4)
        cw, gap = 2.7, 0.25
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, m in enumerate(d.moats[:4]):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.0, cw, 3.5, CARD_BG)
            _rect(sld, cx + 0.1, 3.08, cw - 0.2, 0.05, ORANGE)
            _tb(sld, cx + 0.2, 3.4, cw - 0.4, 0.5, m.label, size=15, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.2, 4.1, cw - 0.4, 1.8, m.value, size=12, color="#555555", align=PP_ALIGN.CENTER)


def _build_gtm(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.phases:
        nc = len(d.phases)
        cw, gap = 3.5, 0.3
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, p in enumerate(d.phases):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.0, cw, 3.8, CARD_BG)
            accent = [ORANGE, BLACK, "#2ECC71"][i % 3]
            _card_header(sld, p.phase, cx, 3.0, cw)
            _tb(sld, cx + 0.3, 3.6, cw - 0.6, 0.4, p.period, size=13, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
            _tb(sld, cx + 0.3, 4.1, cw - 0.6, 2.2, p.description, size=12, color="#555555", align=PP_ALIGN.CENTER)


def _build_roadmap(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.phases:
        pw, gap = 5.8, 0.4
        for i, p in enumerate(d.phases[:2]):
            px = M + i * (pw + gap)
            _rrect(sld, px, 3.0, pw, 3.8, CARD_BG)
            _card_header(sld, p.phase, px, 3.0, pw)
            _tb(sld, px + 0.3, 3.6, pw - 0.6, 0.4, p.period, size=14, bold=True, color=ORANGE)
            _tb(sld, px + 0.3, 4.1, pw - 0.6, 2.2, p.description, size=13, color=BLACK)


def _build_pl(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if not d.years or not d.rows:
        return

    # Left side: P&L table (narrower to make room for chart)
    table_w = 5.5
    rows = len(d.rows) + 1
    cols = len(d.years) + 1
    tbl = sld.shapes.add_table(rows, cols, Inches(M), Inches(3.0), Inches(table_w), Inches(3.5))
    table = tbl.table
    # Header
    for i in range(cols):
        cell = table.cell(0, i)
        cell.fill.solid(); cell.fill.fore_color.rgb = _rgb(HEADER_BG)
        text = "" if i == 0 else d.years[i - 1]
        _style_cell(cell, text, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # Rows
    for ri, row in enumerate(d.rows, 1):
        _style_cell(table.cell(ri, 0), row.label, bold=True)
        if ri % 2 == 0:
            for c in range(cols):
                table.cell(ri, c).fill.solid()
                table.cell(ri, c).fill.fore_color.rgb = _rgb(CARD_BG)
        for ci, yr in enumerate(d.years):
            val = row.values.get(yr, "")
            clr = BLACK
            if val.startswith("-"):
                clr = "#E74C3C"
            _style_cell(table.cell(ri, ci + 1), val, color=clr, align=PP_ALIGN.RIGHT)

    # Right side: Auto-generated chart
    try:
        from charts import render_pl_chart
        import tempfile
        chart_bytes = render_pl_chart(d)
        if chart_bytes:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.write(chart_bytes)
            tmp.close()
            chart_left = M + table_w + 0.3
            chart_w = W - chart_left - M
            _rrect(sld, chart_left, 2.8, chart_w, 4.0, CARD_BG)
            sld.shapes.add_picture(tmp.name, Inches(chart_left + 0.15), Inches(2.95), Inches(chart_w - 0.3), Inches(3.7))
    except Exception:
        pass  # Chart generation failed — table only


def _build_investment(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    # Amount + Valuation
    _rrect(sld, M, 3.0, 5.5, 2.0, CARD_BG)
    _tb(sld, M + 0.3, 3.2, 5, 0.5, "투자 모집 금액", size=13, color=DARK_GRAY)
    _tb(sld, M + 0.3, 3.6, 5, 0.8, d.amount, size=36, bold=True, color=ORANGE)
    _tb(sld, M + 0.3, 4.3, 5, 0.4, f"Pre-money Valuation: {d.valuation}", size=14, color=BLACK)
    # Use of Funds cards
    if d.use_of_funds:
        nc = len(d.use_of_funds)
        cw, gap = 2.2, 0.2
        sx = 7.0
        for i, uf in enumerate(d.use_of_funds):
            cy = 3.0 + i * (1.2 + gap)
            _rrect(sld, sx, cy, 5.5, 1.2, CARD_BG)
            _rect(sld, sx, cy + 0.15, 0.07, 0.9, [ORANGE, BLACK, "#2ECC71"][i % 3])
            _tb(sld, sx + 0.3, cy + 0.1, 1.2, 0.5, uf.value, size=22, bold=True, color=ORANGE)
            _tb(sld, sx + 1.6, cy + 0.1, 3.5, 0.4, uf.label, size=14, bold=True, color=BLACK)
            _tb(sld, sx + 1.6, cy + 0.55, 3.5, 0.4, uf.sub, size=11, color=DARK_GRAY)


def _build_team(prs, d, n):
    sld = _blank(prs); _slide_num(sld, n)
    _section_label(sld, d.section_label)
    _headline(sld, d.headline)
    if d.members:
        nc = min(len(d.members), 3)
        cw, gap = 5.5, 0.4
        sx = (W - nc * cw - (nc - 1) * gap) / 2
        for i, m in enumerate(d.members[:3]):
            cx = sx + i * (cw + gap)
            _rrect(sld, cx, 3.0, cw, 3.5, CARD_BG)
            _tb(sld, cx + 0.3, 3.3, cw - 0.6, 0.5, m.name, size=20, bold=True, color=BLACK)
            _tb(sld, cx + 0.3, 3.8, cw - 0.6, 0.4, m.title, size=14, bold=True, color=ORANGE)
            _tb(sld, cx + 0.3, 4.3, cw - 0.6, 1.8, m.bio, size=12, color="#555555")


def _build_closing(prs, d, n):
    sld = _blank(prs)
    bg = sld.background.fill; bg.solid(); bg.fore_color.rgb = _rgb(BLACK)
    _rect(sld, 0, 0, W, 0.12, ORANGE)
    _tb(sld, 1, 1.5, W - 2, 0.5, d.section_label, size=16, bold=True, color=ORANGE, align=PP_ALIGN.CENTER, font=FONT_EN)
    _tb(sld, 1.5, 2.5, W - 3, 1.5, d.headline, size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    _tb(sld, 2, 4.5, W - 4, 1.0, d.body, size=16, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    c = d.contact
    _tb(sld, 2, 6.0, W - 4, 0.4, f"{c.name}  |  {c.phone}  |  {c.email}", size=12, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    _rect(sld, 0, H - 0.08, W, 0.08, ORANGE)


def _build_generic(prs, d, n):
    """Generic slide for optional/unknown slide types."""
    sld = _blank(prs); _slide_num(sld, n)
    label = getattr(d, "section_label", "")
    headline = getattr(d, "headline", "")
    body = getattr(d, "body", "")
    if label: _section_label(sld, label)
    if headline: _headline(sld, headline)
    if body: _tb(sld, M, 2.8, W - M * 2, 4, body, size=14, color=BLACK)


def _style_cell(cell, text, bold=False, color=BLACK, align=PP_ALIGN.LEFT):
    cell.text = text
    for p in cell.text_frame.paragraphs:
        p.alignment = align
        for r in p.runs:
            r.font.size = Pt(12); r.font.name = FONT_KR
            r.font.bold = bold; r.font.color.rgb = _rgb(color)


# --- Builder registry ---

BUILDERS = {
    "cover": _build_cover,
    "problem": _build_problem,
    "solution": _build_solution,
    "why_now": _build_why_now,
    "market_size": _build_market_size,
    "business_model": _build_business_model,
    "traction": _build_traction,
    "tech_moat": _build_tech_moat,
    "gtm": _build_gtm,
    "roadmap": _build_roadmap,
    "pl": _build_pl,
    "investment": _build_investment,
    "team": _build_team,
    "closing": _build_closing,
}


def generate_pptx(doc: IRDocument, output_path: Path) -> Path:
    """Generate the full IR deck PPT."""
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    # Sort enabled slides by order
    enabled = sorted(
        [sc for sc in doc.slide_config if sc.enabled],
        key=lambda x: x.order,
    )

    slide_num = 1
    for sc in enabled:
        slide_data = getattr(doc, sc.id, None)
        if slide_data is None:
            continue
        builder = BUILDERS.get(sc.id, _build_generic)
        builder(prs, slide_data, slide_num)
        slide_num += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return output_path


def generate_single_slide_png(doc: IRDocument, slide_id: str):
    """Generate a single slide as PNG bytes (for preview).

    Since python-pptx can't render to image directly, we generate
    the slide as a 1-slide PPTX and use a simplified HTML-like approach
    via matplotlib for preview.
    """
    slide_data = getattr(doc, slide_id, None)
    if slide_data is None:
        return None

    from charts import render_pl_chart, render_revenue_growth_chart
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import io
    import textwrap

    fig, ax = plt.subplots(figsize=(13.333, 7.5))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 13.333)
    ax.set_ylim(0, 7.5)
    ax.invert_yaxis()
    ax.set_axis_off()

    label = getattr(slide_data, "section_label", "")
    headline = getattr(slide_data, "headline", "")

    if slide_id == "cover":
        # Dark background
        ax.add_patch(patches.Rectangle((0, 0), 13.333, 7.5, facecolor=BLACK))
        ax.add_patch(patches.Rectangle((0, 0), 13.333, 0.12, facecolor=ORANGE))
        ax.text(6.666, 2.5, getattr(slide_data, "company_name", ""), ha="center", va="center",
                fontsize=40, fontweight="bold", color="white")
        ax.text(6.666, 3.5, getattr(slide_data, "tagline", ""), ha="center", va="center",
                fontsize=16, color="#999999")
        # KPI cards
        kpis = getattr(slide_data, "kpis", [])
        for i, k in enumerate(kpis[:3]):
            cx = 3 + i * 3
            ax.add_patch(patches.FancyBboxPatch((cx - 1.3, 4.5), 2.6, 1.2,
                         boxstyle="round,pad=0.1", facecolor="#222222", edgecolor="none"))
            ax.text(cx, 4.9, k.value, ha="center", va="center", fontsize=18, fontweight="bold", color=ORANGE)
            ax.text(cx, 5.3, k.label, ha="center", va="center", fontsize=9, color="#888888")
        ax.add_patch(patches.Rectangle((0, 7.42), 13.333, 0.08, facecolor=ORANGE))
    elif slide_id == "pl":
        # Section label
        ax.text(0.7, 0.5, label, fontsize=14, fontweight="bold", color=ORANGE)
        wrapped = textwrap.fill(headline, width=50)
        ax.text(0.7, 1.2, wrapped, fontsize=20, fontweight="bold", color=BLACK, va="top")
        # Simple table representation
        years = getattr(slide_data, "years", [])
        rows = getattr(slide_data, "rows", [])
        if years and rows:
            ax.text(0.7, 3.2, "  ".join(["항목"] + years), fontsize=11, fontweight="bold", color="white",
                    bbox=dict(boxstyle="square,pad=0.3", facecolor=BLACK))
            for ri, row in enumerate(rows):
                vals = [row.values.get(y, "") for y in years]
                y_pos = 3.7 + ri * 0.4
                row_text = "  ".join([row.label] + vals)
                ax.text(0.7, y_pos, row_text, fontsize=10, color=BLACK)
        ax.text(8, 3.0, "[차트 자동 생성됨]", fontsize=14, fontweight="bold", color=ORANGE,
                ha="center", bbox=dict(boxstyle="round,pad=0.5", facecolor=LIGHT_GRAY, edgecolor="none"))
    else:
        # Generic preview
        ax.text(0.7, 0.5, label, fontsize=14, fontweight="bold", color=ORANGE)
        wrapped = textwrap.fill(headline, width=50)
        ax.text(0.7, 1.2, wrapped, fontsize=20, fontweight="bold", color=BLACK, va="top")

        # Show body/items as preview
        body = getattr(slide_data, "body", "")
        items = getattr(slide_data, "data_cards", None) or getattr(slide_data, "items", None) or \
                getattr(slide_data, "points", None) or getattr(slide_data, "model_types", None) or \
                getattr(slide_data, "moats", None) or getattr(slide_data, "phases", None) or \
                getattr(slide_data, "members", None) or getattr(slide_data, "use_of_funds", None)

        if items and hasattr(items[0], "label"):
            n = min(len(items), 4)
            cw = 2.8
            gap = 0.2
            sx = (13.333 - n * cw - (n - 1) * gap) / 2
            for i, item in enumerate(items[:4]):
                cx = sx + i * (cw + gap)
                ax.add_patch(patches.FancyBboxPatch((cx, 3.5), cw, 2.8,
                             boxstyle="round,pad=0.1", facecolor=LIGHT_GRAY, edgecolor="none"))
                color_bar = [ORANGE, BLACK, "#2ECC71", "#6366F1"][i % 4]
                ax.add_patch(patches.Rectangle((cx + 0.1, 3.58), cw - 0.2, 0.05, facecolor=color_bar))
                ax.text(cx + cw / 2, 4.0, getattr(item, "label", ""), ha="center", fontsize=12, fontweight="bold")
                val = getattr(item, "value", "")
                ax.text(cx + cw / 2, 4.6, val, ha="center", fontsize=16, fontweight="bold", color=ORANGE)
                sub = getattr(item, "sub", "") or getattr(item, "description", "") or getattr(item, "bio", "")
                if sub:
                    wrapped_sub = textwrap.fill(sub, width=20)
                    ax.text(cx + cw / 2, 5.2, wrapped_sub, ha="center", fontsize=9, color="#555555")
        elif body:
            wrapped_body = textwrap.fill(body, width=70)
            ax.text(0.7, 3.0, wrapped_body, fontsize=13, color=BLACK, va="top")

    # Slide number
    ax.text(12.8, 0.4, "", fontsize=10, color=GRAY, ha="right")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
