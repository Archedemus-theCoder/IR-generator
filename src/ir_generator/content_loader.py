"""Loads slide content from Markdown files with YAML front matter."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import DeckManifest, Slide, SlideFrontMatter


def parse_slide_file(file_path: Path) -> Slide:
    """Parse a single slide Markdown file with YAML front matter."""
    text = file_path.read_text(encoding="utf-8")

    front_matter_data = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            front_matter_data = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()

    return Slide(
        file_path=str(file_path),
        front_matter=SlideFrontMatter(**front_matter_data),
        body=body,
    )


def load_slides(slides_dir: Path) -> list[Slide]:
    """Load all slide files from a directory, sorted by filename."""
    slides = []
    for md_file in sorted(slides_dir.glob("*.md")):
        slides.append(parse_slide_file(md_file))
    return slides


def load_deck_manifest(manifest_path: Path) -> DeckManifest:
    """Load a deck manifest YAML file."""
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return DeckManifest(**data)


def load_defaults(defaults_path: Path) -> dict:
    """Load shared default variables."""
    if not defaults_path.exists():
        return {}
    return yaml.safe_load(defaults_path.read_text(encoding="utf-8")) or {}


def resolve_deck_slides(
    manifest: DeckManifest,
    slides_dir: Path,
    audience: str | None = None,
) -> list[Slide]:
    """Load slides specified in a deck manifest, filtering by audience."""
    slides = []
    for slide_filename in manifest.slides:
        file_path = slides_dir / slide_filename
        if not file_path.exists():
            raise FileNotFoundError(f"Slide not found: {file_path}")
        slide = parse_slide_file(file_path)
        if audience and audience not in slide.front_matter.audiences:
            continue
        slides.append(slide)
    return slides
