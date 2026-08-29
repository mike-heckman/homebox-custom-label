# Task 3: Setup PDF Generator (Layout & Printing)

## Context
We need to generate PDFs matching exact physical label dimensions using `reportlab` and `qrcode[pil]`.
Output PDFs should be written to `./pdf-output/YYYYMMDD-HHMMSS-{mode}.pdf`.

## Implementation Plan
1. Create `src/pdf_generator.py`.
2. Implement PDF generation logic supporting 3 modes:
   - **Mode 1 (Small):** OL2050WX. 0.5" x 0.5". Grid 13x17. QR code ~80% of label, no text.
   - **Mode 2 (Large):** OL450LP. 4.25" x 5.5". Grid 2x2. QR ~80% of top 4.25x4.25. Text: asset id (format e.g. #000-000) under the QR code in bold.
   - **Mode 3 (Scan):** Avery 5160. 1" x 2.625". Grid 3x10. QR code 0.8" left justified. Text right of QR code: Bold item name, asset ID under item name (format e.g. #000-000). Supports `--offset` parameter to skip `N` labels.
3. Implement a helper to correctly strip zero padding for QR Code payload (e.g. `000-010` -> `10`, encoded as `<QR_CODE_PREFIX>10`).
4. Write tests in `tests/test_pdf_generator.py` testing layout coordinates and calculations.

## Success Criteria
- [x] Reportlab generates PDFs correctly sized for each mode.
- [x] Output files are named with the correct timestamp format.
- [x] Unit tests pass with >= 80% coverage.
