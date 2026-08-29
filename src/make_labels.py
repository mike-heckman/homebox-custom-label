"""
CLI Entrypoint for the Homebox Custom Label generator.

Design Pattern: Command Pattern (via Click) for CLI operations.
"""

import logging
from pathlib import Path

import click

from src.config import load_config
from src.homebox_api import HomeboxClient
from src.pdf_generator import generate_pdf

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="config.enc.json",
    help="Path to the SOPS encrypted configuration file.",
)
@click.pass_context
def cli(ctx: click.Context, config: Path) -> None:
    """
    Homebox Custom Label Generator CLI.

    Args:
        ctx: The click context object.
        config: Path to the SOPS encrypted configuration file.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Load configuration
    cfg = load_config(config)

    # Ensure pdf-output directory exists
    pdf_dir = Path("pdf-output")
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Store config and client in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["CONFIG"] = cfg
    ctx.obj["CLIENT"] = HomeboxClient(cfg.homebox_url, cfg.homebox_token)
    ctx.obj["PDF_DIR"] = pdf_dir


@cli.command("small")
@click.option("--starting", type=int, required=True, help="Starting asset ID (numeric).")
@click.option("--count", type=int, default=1, help="Number of labels to generate.")
@click.pass_context
def small(ctx: click.Context, starting: int, count: int) -> None:
    """
    Generate small layout labels (OL2050WX).

    Args:
        ctx: The click context object.
        starting: Starting numeric asset ID.
        count: Number of labels to generate.
    """
    cfg = ctx.obj["CONFIG"]
    pdf_dir = ctx.obj["PDF_DIR"]

    items = [{"asset_id": f"{starting + i}"} for i in range(count)]

    output_path = generate_pdf(items=items, mode="small", qr_prefix=cfg.qr_code_prefix, output_dir=pdf_dir)
    click.echo(f"Generated small labels at {output_path}")


@cli.command("large")
@click.option("--starting", type=int, required=True, help="Starting asset ID (numeric).")
@click.option("--count", type=int, default=1, help="Number of labels to generate.")
@click.pass_context
def large(ctx: click.Context, starting: int, count: int) -> None:
    """
    Generate large layout labels (OL450LP).

    Args:
        ctx: The click context object.
        starting: Starting numeric asset ID.
        count: Number of labels to generate.
    """
    cfg = ctx.obj["CONFIG"]
    pdf_dir = ctx.obj["PDF_DIR"]

    items = [{"asset_id": f"{starting + i}"} for i in range(count)]

    output_path = generate_pdf(items=items, mode="large", qr_prefix=cfg.qr_code_prefix, output_dir=pdf_dir)
    click.echo(f"Generated large labels at {output_path}")


@cli.command("scan")
@click.option("--offset", type=int, default=0, help="Number of label positions to skip.")
@click.pass_context
def scan(ctx: click.Context, offset: int) -> None:
    """
    Scan Homebox for items needing labels and generate them (Avery 5160).

    Args:
        ctx: The click context object.
        offset: Number of label positions to skip before rendering.
    """
    cfg = ctx.obj["CONFIG"]
    client: HomeboxClient = ctx.obj["CLIENT"]
    pdf_dir = ctx.obj["PDF_DIR"]

    click.echo("Fetching items with #needs-label...")
    items = client.get_items_by_tag("#needs-label")

    if not items:
        click.echo("No items found needing a label.")
        return

    click.echo(f"Found {len(items)} items. Generating PDF...")
    output_path = generate_pdf(
        items=items, mode="scan", qr_prefix=cfg.qr_code_prefix, output_dir=pdf_dir, offset=offset
    )
    click.echo(f"Generated scan labels at {output_path}")

    click.echo("Updating items in Homebox...")
    for item in items:
        item_id = item.get("id")
        if item_id:
            try:
                client.update_item_tags(
                    item_id=item_id, tags_to_add=["#label-printed"], tags_to_remove=["#needs-label"]
                )
                logger.info(f"Updated tags for item {item_id}")
            except RuntimeError as e:
                logger.error(f"Failed to update tags for item {item_id}: {e}")

    click.echo("Done.")


if __name__ == "__main__":
    cli()
