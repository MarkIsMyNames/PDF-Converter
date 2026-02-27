# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the converter

```bash
# Convert a file (input is required — there is no default)
python convert_to_pdf.py REPORT.md

# Fit output to N pages (binary-searches font scale)
python convert_to_pdf.py REPORT.md --pages 2

# Custom config
python convert_to_pdf.py REPORT.md --config minimal.toml
```

Output is always `<input_stem>.pdf` in the same directory as the input file.

## Architecture

Four modules with a linear pipeline:

| Module | Responsibility |
|---|---|
| `constants.py` | All constants, CSS/HTML template strings |
| `style.py` | `scale_pt`, `build_css`, `build_html` |
| `converter.py` | `render`, `find_scale_for_pages`, `convert` |
| `convert_to_pdf.py` | CLI entry point (`parse_args`, `main`, `load_config`) |

**Pipeline:** `load_config` → `build_css` → `build_html` → `render` → write output

**Page fitting:** `find_scale_for_pages` binary searches `[FONT_SCALE_MIN, FONT_SCALE_MAX]` (0.4–3.0) in up to `BINARY_SEARCH_ITERATIONS` (20) iterations, finding the largest font scale where `page_count <= target`. Page count is read from `Document.pages` (WeasyPrint), avoiding a separate PDF library.

## Config

`config.toml` is the single source of truth for all style values. Key sections:

- `[page]` — page size, margin, optional `target_pages`
- `[markdown]` — WeasyPrint markdown extensions list
- `[style.colors]`, `[style.fonts]`, `[style.spacing]` — all CSS values

`--pages` CLI flag takes precedence over `config.toml`'s `target_pages`. Margins and page size are never scaled — only the three font size keys.

## Linting and tests

These run automatically via GitHub Actions (`.github/workflows/ci.yml`) on every push and pull request to `main`.

```bash
# Lint
ruff check .

# Run all tests (includes magic-literal enforcement)
pytest

# Run a single test class or function
pytest tests/test_converter.py::TestScalePt
pytest tests/test_no_magic.py::test_no_magic_literals_in_source_modules
```

Install dev dependencies with `pip install pytest ruff` or via the `[dependency-groups] dev` entry in `pyproject.toml`.

## Code conventions

- **No f-strings** — use `.format()` for all string interpolation
- **No magic strings or values** — all hardcoded strings and numbers must be named constants in `constants.py`; enforced automatically by `tests/test_no_magic.py`
- **Allowed inline literals** — `""` (empty string), `0`, `1`, `2` (structural integers); dict-key subscripts (`config["page"]`) and `.get("key")` first args are also exempt
- **Templates at module level** — `CSS_TEMPLATE` and `HTML_TEMPLATE` in `constants.py` use `{named}` placeholders; `build_css` and `build_html` call `.format()` on them with explicit keyword arguments
- **Type hints on all functions** — use `| None` union syntax (Python 3.10+)
- **`pathlib.Path` throughout** — no bare string paths

## Dependencies

```
pip install markdown weasyprint
```
