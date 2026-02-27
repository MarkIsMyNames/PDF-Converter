# PDF Converter

Converts a Markdown file to a styled PDF. Font size auto-scales to hit a target page count if requested.

## Requirements

- Python 3.11+
- `markdown`
- `weasyprint`

```
pip install markdown weasyprint
```

## Usage

```
python convert_to_pdf.py input.md [--pages N] [--config FILE]
```

| Argument | Description |
|---|---|
| `input.md` | Markdown file to convert (required) |
| `--pages N` | Auto-scale font size so the output is exactly N pages |
| `--config FILE` | Path to config file (default: `config.toml`) |

The output PDF is always saved as `<input_name>.pdf` in the same directory as the input file.

### Examples

```bash
# Convert a file
python convert_to_pdf.py REPORT.md

# Squeeze a document to fit on 2 pages
python convert_to_pdf.py REPORT.md --pages 2

# Use a different config
python convert_to_pdf.py REPORT.md --config minimal.toml
```

## Configuration

All styling lives in `config.toml`. Set `target_pages` there to avoid passing `--pages` every run.

```toml
[page]
size   = "A4"
margin = "1.4cm 1.8cm 1.4cm 1.8cm"
# target_pages = 2              # uncomment to always scale to this many pages

[markdown]
extensions = ["tables"]

[style.colors]
body_text  = "#2C2218"
background = "#FFFDF8"
heading    = "#3A2D26"
accent     = "#8A6B5A"          # used for heading borders
rule       = "#D4C4B0"          # used for <hr>

[style.fonts]
body        = "'Helvetica Neue', Arial, sans-serif"
heading     = "Georgia, serif"
body_size   = "9.5pt"           # scaled when --pages is used
line_height = "1.45"
h1_size     = "20pt"            # scaled proportionally
h2_size     = "11pt"            # scaled proportionally

[style.spacing]
h1_margin        = "0 0 4px 0"
h2_margin        = "10px 0 3px 0"
p_margin         = "0 0 5px 0"
ul_margin        = "3px 0 5px 0"
ul_padding_left  = "18px"
li_margin_bottom = "3px"
hr_margin        = "8px 0"
```

### How page fitting works

When `--pages N` is set, the script binary-searches for the largest font scale factor
where the rendered output fits in N pages. `body_size`, `h1_size`, and `h2_size` are
all scaled proportionally. Margins and page size stay fixed.
