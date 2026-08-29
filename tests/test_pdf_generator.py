"""Tests for the PDF generator module."""

import pytest

from src.pdf_generator import generate_pdf, strip_zero_padding


def test_strip_zero_padding() -> None:
    """Test stripping zero padding."""
    assert strip_zero_padding("000-010") == "10"
    assert strip_zero_padding("020-044") == "20044"
    assert strip_zero_padding("010") == "10"
    assert strip_zero_padding("001-005") == "1005"
    assert strip_zero_padding("0") == "0"
    assert strip_zero_padding("000-000") == "0"
    assert strip_zero_padding("") == ""


def test_generate_pdf_small(tmp_path: pytest.TempPathFactory) -> None:
    """Test generating a small PDF."""
    items = [{"asset_id": "000-010", "name": "Item 1"}]
    pdf_path = generate_pdf(items, "small", "http://test/", output_dir=tmp_path)  # type: ignore
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert "-small.pdf" in pdf_path.name


def test_generate_pdf_large(tmp_path: pytest.TempPathFactory) -> None:
    """Test generating a large PDF."""
    items = [{"asset_id": "000-010", "name": "Item 1"}]
    pdf_path = generate_pdf(items, "large", "http://test/", output_dir=tmp_path)  # type: ignore
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert "-large.pdf" in pdf_path.name


def test_generate_pdf_scan(tmp_path: pytest.TempPathFactory) -> None:
    """Test generating a scan PDF."""
    items = [{"asset_id": "000-010", "name": "Item 1"}]
    pdf_path = generate_pdf(items, "scan", "http://test/", output_dir=tmp_path, offset=2)  # type: ignore
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert "-scan.pdf" in pdf_path.name


def test_generate_pdf_invalid_mode() -> None:
    """Test generating a PDF with an invalid mode."""
    items = [{"asset_id": "000-010", "name": "Item 1"}]
    with pytest.raises(ValueError, match="Unknown mode"):
        generate_pdf(items, "invalid", "http://test/")
