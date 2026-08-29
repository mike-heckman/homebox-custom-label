"""PDF generation module for Homebox custom labels.

Design Pattern: Factory & Strategy pattern for different label layouts.
"""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import qrcode
from PIL import Image  # pyright: ignore[reportMissingImports]
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)


def strip_zero_padding(asset_id: str) -> str:
    """Strips leading zeros from the numeric part of the asset ID.

    Args:
        asset_id: The asset ID to format (e.g., "000-010" or "010").

    Returns:
        The stripped asset ID (e.g., "10").
    """
    if not asset_id:
        return ""

    stripped = asset_id.replace("-", "").lstrip("0")
    return stripped if stripped else "0"


def generate_qr_image(payload: str, size_inches: float) -> Image.Image:
    """Generates a QR code image, scaling error correction by physical size.

    Args:
        payload: The URL or text to encode.
        size_inches: The physical size of the QR code in inches.

    Returns:
        A PIL Image of the QR code.
    """
    # Scale error correction based on physical size.
    # Larger codes can handle denser grids, offering better damage resilience.
    if size_inches >= 2.0:
        ec = qrcode.constants.ERROR_CORRECT_Q  # pyright: ignore[reportAttributeAccessIssue]
    elif size_inches >= 1.0:
        ec = qrcode.constants.ERROR_CORRECT_M  # pyright: ignore[reportAttributeAccessIssue]
    else:
        ec = qrcode.constants.ERROR_CORRECT_L  # pyright: ignore[reportAttributeAccessIssue]

    qr = qrcode.QRCode(
        version=1,
        error_correction=ec,  # pyright: ignore[reportAttributeAccessIssue]
        box_size=10,
        border=0,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").get_image()  # type: ignore


def generate_pdf(
    items: list[dict[str, Any]], mode: str, qr_prefix: str, output_dir: Path | None = None, offset: int = 0
) -> Path:
    """Generates a PDF of labels for the given items.

    Args:
        items: List of dictionaries containing 'asset_id' and 'name'.
        mode: The label mode ('small', 'large', 'scan').
        qr_prefix: The prefix for the QR code URL.
        output_dir: The directory to save the PDF. Defaults to ./pdf-output.
        offset: Number of labels to skip (for 'scan' mode).

    Returns:
        The path to the generated PDF.
    """
    if output_dir is None:
        output_dir = Path("pdf-output")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{mode}.pdf"
    filepath = output_dir / filename

    c = canvas.Canvas(str(filepath), pagesize=letter)

    if mode == "small":
        _render_small_labels(c, items, qr_prefix, offset)
    elif mode == "large":
        _render_large_labels(c, items, qr_prefix, offset)
    elif mode == "scan":
        _render_scan_labels(c, items, qr_prefix, offset)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    c.save()
    logger.info(f"Generated PDF: {filepath}")
    return filepath


def _render_small_labels(c: canvas.Canvas, items: list[dict[str, Any]], qr_prefix: str, offset: int) -> None:
    """Renders small labels (OL2050WX). 0.5" x 0.5". Grid 13x17.

    Args:
        c: The canvas.
        items: The items to render.
        qr_prefix: The QR code prefix.
        offset: The number of labels to skip.
    """
    label_width = 0.5 * inch
    label_height = 0.5 * inch
    cols = 13
    rows = 17

    margin_x = 1.0 * inch
    margin_y = 1.25 * inch

    _render_grid(
        c, items, qr_prefix, offset, cols, rows, label_width, label_height, margin_x, margin_y, _draw_small_label
    )


def _render_large_labels(c: canvas.Canvas, items: list[dict[str, Any]], qr_prefix: str, offset: int) -> None:
    """
    Renders large labels (OL450LP). 4.25" x 5.5". Grid 2x2.

    Args:
        c: The canvas.
        items: The items to render.
        qr_prefix: The QR code prefix.
        offset: The number of labels to skip.
    """
    label_width = 4.25 * inch
    label_height = 5.5 * inch
    cols = 2
    rows = 2

    margin_x = 0.0
    margin_y = 0.0

    _render_grid(
        c, items, qr_prefix, offset, cols, rows, label_width, label_height, margin_x, margin_y, _draw_large_label
    )


def _render_scan_labels(c: canvas.Canvas, items: list[dict[str, Any]], qr_prefix: str, offset: int) -> None:
    """
    Renders scan labels (Avery 5160). 1" x 2.625". Grid 3x10.

    Args:
        c: The canvas.
        items: The items to render.
        qr_prefix: The QR code prefix.
        offset: The number of labels to skip.
    """
    label_width = 2.625 * inch
    label_height = 1.0 * inch
    cols = 3
    rows = 10

    margin_x = 0.1875 * inch
    margin_y = 0.5 * inch
    gap_x = 0.125 * inch

    _render_grid(
        c,
        items,
        qr_prefix,
        offset,
        cols,
        rows,
        label_width,
        label_height,
        margin_x,
        margin_y,
        _draw_scan_label,
        gap_x=gap_x,
    )


def _render_grid(
    c: canvas.Canvas,
    items: list[dict[str, Any]],
    qr_prefix: str,
    offset: int,
    cols: int,
    rows: int,
    label_width: float,
    label_height: float,
    margin_x: float,
    margin_y: float,
    draw_func: Callable[[canvas.Canvas, float, float, float, float, dict[str, Any], str], None],
    gap_x: float = 0,
    gap_y: float = 0,
) -> None:
    """
    Generic grid renderer for laying out labels on a page.

    Args:
        c: The reportlab canvas.
        items: List of item dictionaries to render.
        qr_prefix: The prefix URL for the QR code payload.
        offset: Number of labels to skip before printing.
        cols: Number of columns in the grid.
        rows: Number of rows in the grid.
        label_width: Width of each label in inches.
        label_height: Height of each label in inches.
        margin_x: Horizontal margin from the edge of the page.
        margin_y: Vertical margin from the edge of the page.
        draw_func: A function to draw the individual label contents.
        gap_x: Horizontal gap between labels.
        gap_y: Vertical gap between labels.
    """
    current_item_idx = 0
    total_slots = cols * rows

    while current_item_idx < len(items):
        for position in range(total_slots):
            if offset > 0:
                offset -= 1
                continue

            if current_item_idx >= len(items):
                break

            item = items[current_item_idx]

            row = position // cols
            col = position % cols

            x = margin_x + col * (label_width + gap_x)
            y = 11.0 * inch - margin_y - (row + 1) * (label_height + gap_y)

            draw_func(c, x, y, label_width, label_height, item, qr_prefix)
            current_item_idx += 1

        if current_item_idx < len(items):
            c.showPage()


def _draw_small_label(
    c: canvas.Canvas, x: float, y: float, w: float, h: float, item: dict[str, Any], qr_prefix: str
) -> None:
    """
    Draws a small label.

    Args:
        c: The reportlab canvas.
        x: The x-coordinate of the bottom-left corner of the label.
        y: The y-coordinate of the bottom-left corner of the label.
        w: The width of the label.
        h: The height of the label.
        item: The dictionary containing item data.
        qr_prefix: The prefix for the QR code.
    """
    asset_id = str(item.get("asset_id", ""))
    short_id = strip_zero_padding(asset_id)
    payload = f"{qr_prefix}{short_id}"

    qr_size = 0.4 * inch
    offset = (0.5 * inch - qr_size) / 2

    img = generate_qr_image(payload, qr_size)
    c.drawImage(ImageReader(img), x + offset, y + offset, width=qr_size, height=qr_size)


def _draw_large_label(
    c: canvas.Canvas, x: float, y: float, w: float, h: float, item: dict[str, Any], qr_prefix: str
) -> None:
    """
    Draws a large label.

    Args:
        c: The reportlab canvas.
        x: The x-coordinate of the bottom-left corner of the label.
        y: The y-coordinate of the bottom-left corner of the label.
        w: The width of the label.
        h: The height of the label.
        item: The dictionary containing item data.
        qr_prefix: The prefix for the QR code.
    """
    asset_id = str(item.get("asset_id", ""))
    short_id = strip_zero_padding(asset_id)
    payload = f"{qr_prefix}{short_id}"

    qr_size = 3.4 * inch
    offset_x = (4.25 * inch - qr_size) / 2
    offset_y = 5.5 * inch - 4.25 * inch + offset_x

    img = generate_qr_image(payload, qr_size)
    c.drawImage(ImageReader(img), x + offset_x, y + offset_y, width=qr_size, height=qr_size)

    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(x + w / 2, y + 0.5 * inch, asset_id)


def _draw_scan_label(
    c: canvas.Canvas, x: float, y: float, w: float, h: float, item: dict[str, Any], qr_prefix: str
) -> None:
    """
    Draws a scan label.

    Args:
        c: The reportlab canvas.
        x: The x-coordinate of the bottom-left corner of the label.
        y: The y-coordinate of the bottom-left corner of the label.
        w: The width of the label.
        h: The height of the label.
        item: The dictionary containing item data.
        qr_prefix: The prefix for the QR code.
    """
    asset_id = str(item.get("asset_id", ""))
    name = str(item.get("name", ""))
    short_id = strip_zero_padding(asset_id)
    payload = f"{qr_prefix}{short_id}"

    qr_size = 0.8 * inch
    offset_y = (1.0 * inch - qr_size) / 2

    img = generate_qr_image(payload, qr_size)
    c.drawImage(ImageReader(img), x + 0.1 * inch, y + offset_y, width=qr_size, height=qr_size)

    text_x = x + 1.0 * inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_x, y + 0.6 * inch, name)
    c.setFont("Helvetica", 10)
    c.drawString(text_x, y + 0.4 * inch, asset_id)
