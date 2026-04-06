"""Loads and manages brand theme configuration."""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import BrandTheme


def load_theme(theme_path: Path) -> BrandTheme:
    """Load brand theme from YAML file."""
    if not theme_path.exists():
        return BrandTheme()
    data = yaml.safe_load(theme_path.read_text(encoding="utf-8")) or {}
    return BrandTheme(**data)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )
