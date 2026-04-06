"""Pydantic data models for IR Generator."""

from pathlib import Path
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


# --- Brand / Theme ---

class ColorScheme(BaseModel):
    primary: str = "#1A2B4F"
    secondary: str = "#4A90D9"
    accent: str = "#F5A623"
    background: str = "#FFFFFF"
    text_primary: str = "#1A1A1A"
    text_secondary: str = "#6B7280"
    positive: str = "#10B981"
    negative: str = "#EF4444"


class FontScheme(BaseModel):
    heading: str = "Inter"
    body: str = "Inter"
    mono: str = "Courier New"


class SizeScheme(BaseModel):
    title: int = 36
    subtitle: int = 24
    body: int = 16
    caption: int = 12
    metric_highlight: int = 72


class BrandTheme(BaseModel):
    colors: ColorScheme = Field(default_factory=ColorScheme)
    fonts: FontScheme = Field(default_factory=FontScheme)
    sizes: SizeScheme = Field(default_factory=SizeScheme)


# --- Slide Content ---

class SlideFrontMatter(BaseModel):
    layout: str = "content"
    audiences: list[str] = Field(default_factory=lambda: ["internal", "external"])
    title: str = ""
    chart: Optional[str] = None
    speaker_notes: Optional[str] = None
    order: Optional[int] = None


class Slide(BaseModel):
    file_path: str = ""
    front_matter: SlideFrontMatter = Field(default_factory=SlideFrontMatter)
    body: str = ""  # Raw markdown+jinja2 body
    rendered_body: str = ""  # After jinja2 rendering


# --- Deck Manifest ---

class DeckManifest(BaseModel):
    name: str
    description: str = ""
    audience: str = "external"
    slides: list[str]  # List of slide filenames (e.g., "01-cover.md")
    variables: dict[str, Any] = Field(default_factory=dict)


# --- Financial Data ---

class LineItem(BaseModel):
    label: str
    values: dict[str, float] = Field(default_factory=dict)  # period -> amount


class PLStatement(BaseModel):
    periods: list[str] = Field(default_factory=list)
    revenue: dict[str, LineItem] = Field(default_factory=dict)
    costs: dict[str, LineItem] = Field(default_factory=dict)


class Assumptions(BaseModel):
    values: dict[str, Union[float, str]] = Field(default_factory=dict)


class FinancialContext(BaseModel):
    """Flat dictionary of all computed financial variables for Jinja2."""
    variables: dict[str, Any] = Field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return self.variables


# --- Build Config ---

class BuildConfig(BaseModel):
    deck_name: Optional[str] = None
    audience: Optional[str] = None
    output_dir: Path = Path("output")
    var_overrides: dict[str, str] = Field(default_factory=dict)
