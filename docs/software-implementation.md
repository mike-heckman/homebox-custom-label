# Homebox PDF Label Generator Implementation Plan

This project will provide a standalone CLI application to generate PDF QR code labels for the Homebox inventory system. It will support three label formats (Small, Large, and Scan Mode for Avery 5160), read configuration from a SOPS-encrypted file, and interact with the Homebox API.

## Proposed Changes

### Setup and Configuration

#### [NEW] [pyproject.toml](file:///home/mike/Projects/mike-heckman/homebox-custom-label/pyproject.toml)
We will define the project metadata, standard dependencies (`click`, `qrcode`, `reportlab`, `requests`), and linting rules using standard `uv` setups. 

*Initialization Instruction for `uv`:*
To initialize this structure, you would run:
```bash
uv init
uv add click qrcode[pil] reportlab requests
```

#### [NEW] [config.enc.json](file:///home/mike/Projects/mike-heckman/homebox-custom-label/config.enc.json)
(Example file name, format pending answer to Question 1). 
*SOPS Structure Instruction:*
The unencrypted JSON should look like this before `sops` encryption:
```json
{
  "HOMEBOX_URL": "https://homebox.local",
  "HOMEBOX_TOKEN": "your-api-token",
  "QR_CODE_PREFIX": "http://ag4.in/a"
}
```

---

### Source Code

#### [NEW] [src/make_labels.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/src/make_labels.py)
This will be the main entry point utilizing `click` to handle the three CLI modes. It will define the main command group and subcommands `small`, `large`, and `scan`.

#### [NEW] [src/config.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/src/config.py)
A module to handle loading the SOPS-encrypted configuration file. It will handle decryption on the fly and provide a typed configuration object.

#### [NEW] [src/homebox_api.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/src/homebox_api.py)
A module containing a class `HomeboxClient` for all REST API interactions.
- `get_items_by_tag(tag: str)`
- `update_item_tags(item_id: str, tags_to_add: list[str], tags_to_remove: list[str])`

#### [NEW] [src/pdf_generator.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/src/pdf_generator.py)
A module using `reportlab` to generate PDFs based on the selected label templates:
- `#OL2050WX` (Small)
- `#OL450LP` (Large)
- `Avery 5160` (Scan Mode)
It will also use `qrcode` to generate the image data for placement on the labels.

---

### Tests

#### [NEW] [tests/test_cli.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/tests/test_cli.py)
Unit tests for the Click CLI arguments.

#### [NEW] [tests/test_pdf_generator.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/tests/test_pdf_generator.py)
Tests to verify the PDF layout calculations (mocking the actual PDF generation).

#### [NEW] [tests/test_homebox_api.py](file:///home/mike/Projects/mike-heckman/homebox-custom-label/tests/test_homebox_api.py)
Unit tests mocking the `requests` library to ensure API calls are formed correctly for fetching and the read-modify-write cycle.

## Verification Plan

### Automated Tests
- `uv run pytest tests/ -v`
- Mocking all API calls and SOPS executions to run in isolation.

### Manual Verification
- Generate a sample PDF for each mode (`--small`, `--large`, `--scan`) and ask the user to verify the layout, dimensions, and QR code resolution against their physical label templates.
- For `--scan` mode, run against a sandbox Homebox instance (or mock local server) to verify tag removal and addition logic works as expected.
