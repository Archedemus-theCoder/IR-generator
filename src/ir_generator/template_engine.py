"""Jinja2 template rendering for slide content."""

from __future__ import annotations

from typing import Any

from jinja2 import Environment, BaseLoader, Undefined


def _currency_filter(value: Any) -> str:
    """Format number as currency: $1.2M, $850K, $1,200."""
    if isinstance(value, Undefined) or value is None:
        return "$0"
    value = float(value)
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    if abs_value >= 1_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"{sign}${abs_value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{sign}${abs_value / 1_000:.0f}K"
    return f"{sign}${abs_value:,.0f}"


def _percent_filter(value: Any) -> str:
    """Format as percentage: 72%."""
    if isinstance(value, Undefined) or value is None:
        return "0%"
    return f"{float(value) * 100:.0f}%"


def _delta_filter(value: Any) -> str:
    """Format as delta: +15% or -3%."""
    if isinstance(value, Undefined) or value is None:
        return "0%"
    v = float(value) * 100
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.0f}%"


def _compact_filter(value: Any) -> str:
    """Compact number format: 1.2M, 850K."""
    if isinstance(value, Undefined) or value is None:
        return "0"
    value = float(value)
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    if abs_value >= 1_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"{sign}{abs_value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{sign}{abs_value / 1_000:.0f}K"
    return f"{sign}{abs_value:,.0f}"


def create_jinja_env() -> Environment:
    """Create a Jinja2 environment with custom filters."""
    env = Environment(
        loader=BaseLoader(),
        undefined=Undefined,
    )
    env.filters["currency"] = _currency_filter
    env.filters["percent"] = _percent_filter
    env.filters["delta"] = _delta_filter
    env.filters["compact"] = _compact_filter
    return env


def render_slide_body(body: str, context: dict[str, Any]) -> str:
    """Render Jinja2 template tags in slide body with financial context."""
    env = create_jinja_env()
    template = env.from_string(body)
    return template.render(**context)
