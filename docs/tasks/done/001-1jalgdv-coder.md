# Task 1: Setup Configuration & SOPS Decryption

## Context
We need a robust way to securely load credentials using `sops` via the command-line binary. 

## Implementation Plan
1. Create `src/config.py`.
2. Write a function `load_config(path: str)` that uses `subprocess.run` to call `sops -d {path}`.
3. The decrypted output should be parsed as JSON.
4. Define a dataclass or typed dict for the configuration (HOMEBOX_URL, HOMEBOX_TOKEN, QR_CODE_PREFIX).
5. Add appropriate error handling if `sops` is missing or decryption fails.
6. Write tests in `tests/test_config.py` mocking `subprocess.run`.

## Success Criteria
- [x] `config.py` correctly parses SOPS-decrypted JSON.
- [x] Unit tests pass with >= 80% coverage.
