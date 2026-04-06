"""Main build orchestrator: content + financials + brand → PPT."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .brand_manager import load_theme
from .chart_renderer import render_chart
from .content_loader import (
    load_deck_manifest,
    load_defaults,
    load_slides,
    resolve_deck_slides,
)
from .financial_engine import compute_financial_context, load_assumptions, load_pl
from .models import BrandTheme, BuildConfig, Slide
from .pptx_writer import create_presentation
from .template_engine import render_slide_body


def build_deck(
    project_root: Path,
    config: BuildConfig,
) -> Path:
    """Build a complete PPT deck from project sources.

    Pipeline:
    1. Load brand theme
    2. Load financial data and compute context
    3. Load slides (from manifest or all)
    4. Render Jinja2 templates in slide bodies
    5. Generate charts
    6. Assemble PPT
    """
    # 1. Load brand theme
    theme = load_theme(project_root / "brand" / "theme.yaml")

    # 2. Load financial data
    financials_dir = project_root / "financials"
    pl = load_pl(financials_dir / "pl.yaml")
    assumptions = load_assumptions(financials_dir / "assumptions.yaml")
    financial_ctx = compute_financial_context(pl, assumptions)

    # Build full template context
    defaults = load_defaults(project_root / "content" / "_defaults.yaml")
    context: dict[str, Any] = {}
    context.update(defaults)
    context.update(financial_ctx.as_dict())
    context.update(config.var_overrides)

    # 3. Load slides
    slides_dir = project_root / "content" / "slides"
    decks_dir = project_root / "content" / "decks"

    if config.deck_name:
        manifest_path = decks_dir / f"{config.deck_name}.yaml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Deck manifest not found: {manifest_path}")
        manifest = load_deck_manifest(manifest_path)
        slides = resolve_deck_slides(manifest, slides_dir, config.audience)
        deck_display_name = config.deck_name
    else:
        slides = load_slides(slides_dir)
        if config.audience:
            slides = [
                s for s in slides
                if config.audience in s.front_matter.audiences
            ]
        deck_display_name = "deck"

    # 4. Render Jinja2 templates (both title and body)
    for slide in slides:
        slide.rendered_body = render_slide_body(slide.body, context)
        if slide.front_matter.title:
            slide.front_matter.title = render_slide_body(
                slide.front_matter.title, context
            )

    # 5. Generate charts
    chart_paths: dict[str, Path] = {}
    for slide in slides:
        chart_name = slide.front_matter.chart
        if chart_name and chart_name not in chart_paths:
            chart_path = render_chart(chart_name, context, theme)
            if chart_path:
                chart_paths[chart_name] = chart_path

    # 6. Assemble PPT
    base_template = project_root / "brand" / "base_template.pptx"
    output_path = config.output_dir / f"{deck_display_name}.pptx"

    result = create_presentation(
        slides=slides,
        theme=theme,
        context=context,
        chart_paths=chart_paths,
        base_template=base_template if base_template.exists() else None,
        output_path=output_path,
    )

    return result
