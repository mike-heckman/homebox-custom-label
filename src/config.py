"""Configuration module for the Homebox Custom Label generator.

This module handles loading the SOPS-encrypted configuration file.
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """
    Base exception for configuration errors.

    This exception should be inherited by all custom exceptions in this module.
    """


class SopsDecryptionError(ConfigError):
    """
    Raised when SOPS decryption fails.

    This exception is thrown if the SOPS binary returns a non-zero exit code.
    """


class SopsNotFoundError(ConfigError):
    """
    Raised when the SOPS binary is not found.

    This exception is thrown if the 'sops' executable cannot be located on the PATH.
    """


class ConfigParseError(ConfigError):
    """
    Raised when the decrypted configuration cannot be parsed.

    This exception is thrown if the output is not valid JSON or lacks required fields.
    """


@dataclass
class Config:
    """
    Represents the application configuration.

    Attributes:
        homebox_url: The URL to the Homebox instance.
        homebox_token: The API token for authenticating with Homebox.
        qr_code_prefix: The prefix to use for generating QR code URLs.
    """

    homebox_url: str
    homebox_token: str = field(repr=False)
    qr_code_prefix: str


def load_config(path: str | Path) -> Config:
    """
    Loads and decrypts the configuration using SOPS.

    Args:
        path: The path to the SOPS-encrypted configuration file.

    Returns:
        The decrypted configuration object.

    Raises:
        SopsNotFoundError: If the 'sops' binary is not found on the system path.
        SopsDecryptionError: If the decryption process fails.
        ConfigParseError: If the decrypted output is not valid JSON or lacks required fields.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise ConfigError(f"Configuration file not found: {path_obj}")

    try:
        result = subprocess.run(
            ["sops", "-d", str(path_obj)],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as e:
        raise SopsNotFoundError("The 'sops' binary was not found. Please install SOPS.") from e
    except subprocess.CalledProcessError as e:
        logger.error("SOPS decryption failed: %s", e.stderr)
        raise SopsDecryptionError(f"Failed to decrypt configuration: {e.stderr}") from e

    try:
        data: dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise ConfigParseError("Failed to parse the decrypted configuration as JSON.") from e

    try:
        return Config(
            homebox_url=data["HOMEBOX_URL"],
            homebox_token=data["HOMEBOX_TOKEN"],
            qr_code_prefix=data["QR_CODE_PREFIX"],
        )
    except KeyError as e:
        raise ConfigParseError(f"Missing required configuration key: {e}") from e
