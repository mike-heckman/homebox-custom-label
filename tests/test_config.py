"""Unit tests for the configuration module."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.config import (
    Config,
    ConfigError,
    ConfigParseError,
    SopsDecryptionError,
    SopsNotFoundError,
    load_config,
)


@pytest.fixture
def mock_sops_output() -> str:
    """Provides a valid mock output for SOPS decryption.

    Returns:
        A JSON string representing valid configuration data.
    """
    data = {
        "HOMEBOX_URL": "https://homebox.local",
        "HOMEBOX_TOKEN": "secret-token",
        "QR_CODE_PREFIX": "http://ag4.in/a",
    }
    return json.dumps(data)


def test_load_config_success(mocker: MagicMock, tmp_path: Path, mock_sops_output: str) -> None:
    """Tests loading the configuration successfully.

    Args:
        mocker: The pytest-mock fixture.
        tmp_path: The pytest tmp_path fixture.
        mock_sops_output: The mock SOPS JSON output fixture.
    """
    config_file = tmp_path / "config.enc.json"
    config_file.touch()

    mock_run = mocker.patch("src.config.subprocess.run")
    mock_run.return_value = subprocess.CompletedProcess(
        args=["sops", "-d", str(config_file)],
        returncode=0,
        stdout=mock_sops_output,
        stderr="",
    )

    config = load_config(config_file)

    assert isinstance(config, Config)
    assert config.homebox_url == "https://homebox.local"
    assert config.homebox_token == "secret-token"
    assert config.qr_code_prefix == "http://ag4.in/a"
    mock_run.assert_called_once_with(
        ["sops", "-d", str(config_file)],
        capture_output=True,
        text=True,
        check=True,
    )


def test_load_config_file_not_found(tmp_path: Path) -> None:
    """Tests loading configuration when the file does not exist.

    Args:
        tmp_path: The pytest tmp_path fixture.
    """
    missing_file = tmp_path / "missing.json"

    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config(missing_file)


def test_load_config_sops_not_found(mocker: MagicMock, tmp_path: Path) -> None:
    """Tests loading configuration when the 'sops' binary is missing.

    Args:
        mocker: The pytest-mock fixture.
        tmp_path: The pytest tmp_path fixture.
    """
    config_file = tmp_path / "config.enc.json"
    config_file.touch()

    mock_run = mocker.patch("src.config.subprocess.run")
    mock_run.side_effect = FileNotFoundError()

    with pytest.raises(SopsNotFoundError, match="The 'sops' binary was not found"):
        load_config(config_file)


def test_load_config_sops_decryption_error(mocker: MagicMock, tmp_path: Path) -> None:
    """Tests loading configuration when SOPS decryption fails.

    Args:
        mocker: The pytest-mock fixture.
        tmp_path: The pytest tmp_path fixture.
    """
    config_file = tmp_path / "config.enc.json"
    config_file.touch()

    mock_run = mocker.patch("src.config.subprocess.run")
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["sops", "-d", str(config_file)],
        stderr="Mac verification failed",
    )

    with pytest.raises(SopsDecryptionError, match="Failed to decrypt configuration"):
        load_config(config_file)


def test_load_config_invalid_json(mocker: MagicMock, tmp_path: Path) -> None:
    """Tests loading configuration when the decrypted output is invalid JSON.

    Args:
        mocker: The pytest-mock fixture.
        tmp_path: The pytest tmp_path fixture.
    """
    config_file = tmp_path / "config.enc.json"
    config_file.touch()

    mock_run = mocker.patch("src.config.subprocess.run")
    mock_run.return_value = subprocess.CompletedProcess(
        args=["sops", "-d", str(config_file)],
        returncode=0,
        stdout="Not valid JSON",
        stderr="",
    )

    with pytest.raises(ConfigParseError, match="Failed to parse the decrypted configuration as JSON"):
        load_config(config_file)


def test_load_config_missing_keys(mocker: MagicMock, tmp_path: Path) -> None:
    """Tests loading configuration when required keys are missing from the JSON.

    Args:
        mocker: The pytest-mock fixture.
        tmp_path: The pytest tmp_path fixture.
    """
    config_file = tmp_path / "config.enc.json"
    config_file.touch()

    mock_run = mocker.patch("src.config.subprocess.run")
    mock_run.return_value = subprocess.CompletedProcess(
        args=["sops", "-d", str(config_file)],
        returncode=0,
        stdout='{"HOMEBOX_URL": "https://homebox.local"}',
        stderr="",
    )

    with pytest.raises(ConfigParseError, match="Missing required configuration key"):
        load_config(config_file)
