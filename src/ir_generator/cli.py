"""CLI interface for IR Generator."""

from __future__ import annotations

from pathlib import Path

import click

from .builder import build_deck
from .financial_engine import compute_financial_context, load_assumptions, load_pl
from .models import BuildConfig
from .validators import validate_project


@click.group()
@click.option("--project", "-p", default=".", help="Project root directory")
@click.pass_context
def cli(ctx: click.Context, project: str) -> None:
    """IR Generator - Automated IR deck management and PPT generation."""
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = Path(project).resolve()


@cli.command()
@click.argument("deck_name", required=False)
@click.option("--audience", "-a", help="Filter slides by audience (internal/external)")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--var", "-v", multiple=True, help="Variable override (key=value)")
@click.pass_context
def build(
    ctx: click.Context,
    deck_name: str | None,
    audience: str | None,
    output: str,
    var: tuple[str, ...],
) -> None:
    """Build PPT deck from content and financial data."""
    project_root = ctx.obj["project_root"]

    # Parse variable overrides
    var_overrides = {}
    for v in var:
        if "=" in v:
            key, value = v.split("=", 1)
            var_overrides[key.strip()] = value.strip()

    config = BuildConfig(
        deck_name=deck_name,
        audience=audience,
        output_dir=project_root / output,
        var_overrides=var_overrides,
    )

    click.echo(f"Building deck: {deck_name or 'all slides'}...")
    try:
        result = build_deck(project_root, config)
        click.echo(f"✓ Generated: {result}")
    except Exception as e:
        click.echo(f"✗ Build failed: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate project content, financials, and configuration."""
    project_root = ctx.obj["project_root"]
    errors = validate_project(project_root)

    has_errors = False
    for err in errors:
        if err.level == "error":
            click.echo(click.style(str(err), fg="red"))
            has_errors = True
        elif err.level == "warning":
            click.echo(click.style(str(err), fg="yellow"))
        else:
            click.echo(click.style(str(err), fg="green"))

    if has_errors:
        raise SystemExit(1)


@cli.group()
def financials() -> None:
    """Financial data commands."""
    pass


@financials.command()
@click.pass_context
def summary(ctx: click.Context) -> None:
    """Print financial summary to terminal."""
    project_root = ctx.obj["project_root"]
    financials_dir = project_root / "financials"

    pl = load_pl(financials_dir / "pl.yaml")
    assumptions = load_assumptions(financials_dir / "assumptions.yaml")
    fin_ctx = compute_financial_context(pl, assumptions)
    ctx_dict = fin_ctx.as_dict()

    click.echo("\n=== Financial Summary ===\n")

    # Find years in context
    years = sorted(set(
        k.split("_")[-1]
        for k in ctx_dict
        if k.startswith("total_revenue_") and k.split("_")[-1].isdigit()
    ))

    if not years:
        click.echo("No financial data found.")
        return

    # Header
    header = f"{'Metric':<25}" + "".join(f"{y:>15}" for y in years)
    click.echo(header)
    click.echo("-" * len(header))

    # Revenue
    row = f"{'Revenue':<25}"
    for y in years:
        val = ctx_dict.get(f"total_revenue_{y}", 0)
        row += f"${val:>14,.0f}"
    click.echo(row)

    # Costs
    row = f"{'Costs':<25}"
    for y in years:
        val = ctx_dict.get(f"total_costs_{y}", 0)
        row += f"${val:>14,.0f}"
    click.echo(row)

    # Profit
    row = f"{'Gross Profit':<25}"
    for y in years:
        val = ctx_dict.get(f"gross_profit_{y}", 0)
        row += f"${val:>14,.0f}"
    click.echo(click.style(row, fg="green" if val >= 0 else "red"))

    # Margin
    row = f"{'Gross Margin':<25}"
    for y in years:
        val = ctx_dict.get(f"gross_margin_{y}", 0)
        row += f"{val:>14.1%}"
    click.echo(row)

    click.echo()
