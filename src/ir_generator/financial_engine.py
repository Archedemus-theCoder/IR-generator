"""Financial data loading and computation engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import Assumptions, FinancialContext, LineItem, PLStatement


def load_pl(pl_path: Path) -> PLStatement:
    """Load P&L statement from YAML."""
    if not pl_path.exists():
        return PLStatement()
    data = yaml.safe_load(pl_path.read_text(encoding="utf-8")) or {}

    periods = data.get("periods", [])
    revenue = {
        k: LineItem(**v) for k, v in data.get("revenue", {}).items()
    }
    costs = {
        k: LineItem(**v) for k, v in data.get("costs", {}).items()
    }
    return PLStatement(periods=periods, revenue=revenue, costs=costs)


def load_assumptions(assumptions_path: Path) -> Assumptions:
    """Load financial assumptions from YAML."""
    if not assumptions_path.exists():
        return Assumptions()
    data = yaml.safe_load(assumptions_path.read_text(encoding="utf-8")) or {}
    return Assumptions(values=data)


def _sum_line_items(items: dict[str, LineItem], period: str) -> float:
    return sum(item.values.get(period, 0) for item in items.values())


def _sum_line_items_all(items: dict[str, LineItem], periods: list[str]) -> float:
    return sum(_sum_line_items(items, p) for p in periods)


def _periods_for_year(periods: list[str], year: str) -> list[str]:
    """Filter periods belonging to a specific year (e.g., '2024')."""
    return [p for p in periods if p.startswith(year)]


def _get_years(periods: list[str]) -> list[str]:
    """Extract unique years from period strings."""
    years = sorted(set(p.split("-")[0] for p in periods))
    return years


def compute_financial_context(
    pl: PLStatement,
    assumptions: Assumptions,
) -> FinancialContext:
    """Compute all financial variables for template rendering."""
    ctx: dict[str, Any] = {}

    # Copy all assumptions directly
    ctx.update(assumptions.values)

    years = _get_years(pl.periods)

    for year in years:
        year_periods = _periods_for_year(pl.periods, year)

        total_revenue = _sum_line_items_all(pl.revenue, year_periods)
        total_costs = _sum_line_items_all(pl.costs, year_periods)
        gross_profit = total_revenue - total_costs

        ctx[f"total_revenue_{year}"] = total_revenue
        ctx[f"total_costs_{year}"] = total_costs
        ctx[f"gross_profit_{year}"] = gross_profit
        ctx[f"gross_margin_{year}"] = (
            gross_profit / total_revenue if total_revenue else 0
        )

        # Per line item totals
        for key, item in pl.revenue.items():
            total = sum(item.values.get(p, 0) for p in year_periods)
            ctx[f"revenue_{key}_{year}"] = total

        for key, item in pl.costs.items():
            total = sum(item.values.get(p, 0) for p in year_periods)
            ctx[f"cost_{key}_{year}"] = total

    # Period-by-period data for charts
    ctx["periods"] = pl.periods
    ctx["revenue_by_period"] = [
        _sum_line_items(pl.revenue, p) for p in pl.periods
    ]
    ctx["costs_by_period"] = [
        _sum_line_items(pl.costs, p) for p in pl.periods
    ]
    ctx["profit_by_period"] = [
        r - c for r, c in zip(ctx["revenue_by_period"], ctx["costs_by_period"])
    ]

    # Revenue breakdown by line item (for stacked charts)
    ctx["revenue_items"] = {
        key: {
            "label": item.label,
            "values": [item.values.get(p, 0) for p in pl.periods],
        }
        for key, item in pl.revenue.items()
    }
    ctx["cost_items"] = {
        key: {
            "label": item.label,
            "values": [item.values.get(p, 0) for p in pl.periods],
        }
        for key, item in pl.costs.items()
    }

    return FinancialContext(variables=ctx)
