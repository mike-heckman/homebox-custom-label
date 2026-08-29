# Task 4: Setup CLI Entrypoint

## Context
The CLI binds together Config, API, and PDF generation into the `make-labels.py` command managed by `click`.

## Implementation Plan
1. Create `src/make_labels.py`.
2. Implement main `@click.group()` entrypoint to load config and ensure `pdf-output` exists.
3. Implement `@click.command("small")` taking `--starting` and `--count` (default 1).
4. Implement `@click.command("large")` taking `--starting` and `--count`.
5. Implement `@click.command("scan")` taking `--offset` (default 0).
   - Fetches items with `#needs-label`
   - Generates the PDF for those items
   - Updates items replacing `#needs-label` with `#label-printed`.
6. Write tests in `tests/test_cli.py` using `click.testing.CliRunner`.

## Success Criteria
- [ ] CLI correctly parses arguments and dispatches to the correct logic.
- [ ] Unit tests pass with >= 80% coverage.
