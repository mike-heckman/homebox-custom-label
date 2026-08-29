"""Tests for the CLI module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.config import Config
from src.make_labels import cli


@pytest.fixture
def runner() -> CliRunner:
    """Fixture providing a Click CliRunner."""
    return CliRunner()


@pytest.fixture
def mock_config() -> Config:
    """Fixture providing a mock Config object."""
    return Config(homebox_url="http://test", homebox_token="secret", qr_code_prefix="http://test/qr/")


@patch("src.make_labels.load_config")
@patch("src.make_labels.generate_pdf")
def test_cli_small(
    mock_generate_pdf: MagicMock,
    mock_load_config: MagicMock,
    runner: CliRunner,
    mock_config: Config,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the 'small' CLI command."""
    mock_load_config.return_value = mock_config
    mock_generate_pdf.return_value = Path("test.pdf")

    monkeypatch.chdir(tmp_path)
    Path("test-config.json").touch()

    result = runner.invoke(cli, ["--config", "test-config.json", "small", "--starting", "10", "--count", "5"])

    assert result.exit_code == 0
    assert "Generated small labels at test.pdf" in result.output

    mock_generate_pdf.assert_called_once()
    kwargs = mock_generate_pdf.call_args.kwargs
    assert kwargs["mode"] == "small"
    assert kwargs["qr_prefix"] == "http://test/qr/"
    assert len(kwargs["items"]) == 5
    assert kwargs["items"][0]["asset_id"] == "10"
    assert kwargs["items"][4]["asset_id"] == "14"


@patch("src.make_labels.load_config")
@patch("src.make_labels.generate_pdf")
def test_cli_large(
    mock_generate_pdf: MagicMock,
    mock_load_config: MagicMock,
    runner: CliRunner,
    mock_config: Config,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the 'large' CLI command."""
    mock_load_config.return_value = mock_config
    mock_generate_pdf.return_value = Path("test.pdf")

    monkeypatch.chdir(tmp_path)
    Path("test-config.json").touch()

    result = runner.invoke(cli, ["--config", "test-config.json", "large", "--starting", "100"])

    assert result.exit_code == 0
    assert "Generated large labels at test.pdf" in result.output

    mock_generate_pdf.assert_called_once()
    kwargs = mock_generate_pdf.call_args.kwargs
    assert kwargs["mode"] == "large"
    assert len(kwargs["items"]) == 1
    assert kwargs["items"][0]["asset_id"] == "100"


@patch("src.make_labels.load_config")
@patch("src.make_labels.HomeboxClient")
@patch("src.make_labels.generate_pdf")
def test_cli_scan(
    mock_generate_pdf: MagicMock,
    mock_client_class: MagicMock,
    mock_load_config: MagicMock,
    runner: CliRunner,
    mock_config: Config,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the 'scan' CLI command."""
    mock_load_config.return_value = mock_config
    mock_generate_pdf.return_value = Path("test.pdf")

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.get_items_by_tag.return_value = [{"id": "id1", "asset_id": "001"}, {"id": "id2", "asset_id": "002"}]

    monkeypatch.chdir(tmp_path)
    Path("test-config.json").touch()

    result = runner.invoke(cli, ["--config", "test-config.json", "scan", "--offset", "2"])

    assert result.exit_code == 0
    assert "Generated scan labels at test.pdf" in result.output

    mock_client.get_items_by_tag.assert_called_once_with("#needs-label")

    mock_generate_pdf.assert_called_once()
    kwargs = mock_generate_pdf.call_args.kwargs
    assert kwargs["mode"] == "scan"
    assert kwargs["offset"] == 2
    assert len(kwargs["items"]) == 2

    assert mock_client.update_item_tags.call_count == 2
    mock_client.update_item_tags.assert_any_call(
        item_id="id1", tags_to_add=["#label-printed"], tags_to_remove=["#needs-label"]
    )


@patch("src.make_labels.load_config")
@patch("src.make_labels.HomeboxClient")
def test_cli_scan_no_items(
    mock_client_class: MagicMock,
    mock_load_config: MagicMock,
    runner: CliRunner,
    mock_config: Config,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the 'scan' CLI command when no items are found."""
    mock_load_config.return_value = mock_config

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.get_items_by_tag.return_value = []

    monkeypatch.chdir(tmp_path)
    Path("test-config.json").touch()

    result = runner.invoke(cli, ["--config", "test-config.json", "scan"])

    assert result.exit_code == 0
    assert "No items found needing a label." in result.output
