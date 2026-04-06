"""Pre-build validation checks."""

from __future__ import annotations

from pathlib import Path

from .content_loader import load_deck_manifest, load_slides, parse_slide_file
from .financial_engine import load_pl, load_assumptions
from .brand_manager import load_theme


class ValidationError:
    def __init__(self, level: str, message: str):
        self.level = level  # "error" or "warning"
        self.message = message

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.message}"


def validate_project(project_root: Path) -> list[ValidationError]:
    """Run all validation checks on the project."""
    errors: list[ValidationError] = []

    # Check directory structure
    content_dir = project_root / "content"
    slides_dir = content_dir / "slides"
    financials_dir = project_root / "financials"
    brand_dir = project_root / "brand"

    for d in [content_dir, slides_dir]:
        if not d.exists():
            errors.append(ValidationError("error", f"Missing directory: {d}"))

    # Validate slides
    if slides_dir.exists():
        for md_file in sorted(slides_dir.glob("*.md")):
            try:
                slide = parse_slide_file(md_file)
                if not slide.front_matter.title:
                    errors.append(ValidationError(
                        "warning",
                        f"Slide {md_file.name} has no title",
                    ))
                valid_layouts = {"title", "content", "two_column", "metric_highlight", "table", "chart", "section_divider"}
                if slide.front_matter.layout not in valid_layouts:
                    errors.append(ValidationError(
                        "warning",
                        f"Slide {md_file.name} has unknown layout: {slide.front_matter.layout}",
                    ))
            except Exception as e:
                errors.append(ValidationError("error", f"Failed to parse {md_file.name}: {e}"))

    # Validate deck manifests
    decks_dir = content_dir / "decks"
    if decks_dir.exists():
        for yaml_file in sorted(decks_dir.glob("*.yaml")):
            try:
                manifest = load_deck_manifest(yaml_file)
                for slide_name in manifest.slides:
                    slide_path = slides_dir / slide_name
                    if not slide_path.exists():
                        errors.append(ValidationError(
                            "error",
                            f"Deck {yaml_file.name} references missing slide: {slide_name}",
                        ))
            except Exception as e:
                errors.append(ValidationError("error", f"Failed to parse deck {yaml_file.name}: {e}"))

    # Validate financial data
    pl_path = financials_dir / "pl.yaml"
    if pl_path.exists():
        try:
            pl = load_pl(pl_path)
            if not pl.periods:
                errors.append(ValidationError("warning", "P&L has no periods defined"))
        except Exception as e:
            errors.append(ValidationError("error", f"Failed to parse pl.yaml: {e}"))

    # Validate theme
    theme_path = brand_dir / "theme.yaml"
    if theme_path.exists():
        try:
            load_theme(theme_path)
        except Exception as e:
            errors.append(ValidationError("error", f"Failed to parse theme.yaml: {e}"))

    if not errors:
        errors.append(ValidationError("info", "All validations passed"))

    return errors
