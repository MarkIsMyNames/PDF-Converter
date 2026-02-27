"""Shared constants and document template strings."""

from pathlib import Path

# ── Runtime ────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = Path("config.toml")
ENCODING = "utf-8"

FONT_SCALE_MIN = 0.4
FONT_SCALE_MAX = 3.0
FONT_SCALE_TOLERANCE = 0.001
BINARY_SEARCH_ITERATIONS = 20

# ── CSS structural values (not exposed in config.toml) ─────────────────────────

FONT_UNIT = "pt"
FONT_WEIGHT_BOLD = 700
FONT_WEIGHT_SEMIBOLD = 600
H1_BORDER = "2px solid"
H1_PADDING_BOTTOM = "5px"
H1_LETTER_SPACING = "-0.3px"
H2_BORDER = "3px solid"
H2_PADDING_LEFT = "8px"
HR_BORDER_TOP = "1px solid"

# ── Formatting ────────────────────────────────────────────────────────────────

DEFAULT_FONT_SCALE = 1.0
TOML_READ_MODE = "rb"
SCALE_PT_FORMAT = "{:.2f}{}"
PLURAL_SUFFIX = "s"
PDF_SUFFIX = ".pdf"

# ── Messages ──────────────────────────────────────────────────────────────────

MSG_FITTING = "Fitting to {} page{}..."
MSG_PDF_CREATED = "PDF created: {} ({} page{})"
ERR_CONFIG_NOT_FOUND = "Config file not found: {}"
ERR_INPUT_NOT_FOUND = "Input file not found: {}"

# ── CLI ───────────────────────────────────────────────────────────────────────

CLI_DESCRIPTION = "Convert a Markdown file to a styled PDF."
CLI_ARG_INPUT = "input"
CLI_INPUT_HELP = "Input Markdown file"
CLI_ARG_PAGES = "--pages"
CLI_PAGES_METAVAR = "N"
CLI_PAGES_HELP = "Scale font to fit N pages"
CLI_ARG_CONFIG = "--config"
CLI_CONFIG_METAVAR = "FILE"
CLI_CONFIG_HELP = "Config file (default: {})"

# ── Templates (allocated once; CSS braces that are literals must be doubled) ───

CSS_TEMPLATE = """
  @page {{
    size: {page_size};
    margin: {page_margin};
  }}

  body {{
    font-family: {body_font};
    font-size: {body_size};
    line-height: {line_height};
    color: {color_body_text};
    background: {color_background};
  }}

  h1 {{
    font-family: {heading_font};
    font-size: {h1_size};
    font-weight: {weight_bold};
    color: {color_heading};
    border-bottom: {h1_border} {color_accent};
    padding-bottom: {h1_padding_bottom};
    margin: {h1_margin};
    letter-spacing: {h1_letter_spacing};
  }}

  h2 {{
    font-family: {heading_font};
    font-size: {h2_size};
    font-weight: {weight_bold};
    color: {color_heading};
    margin: {h2_margin};
    border-left: {h2_border} {color_accent};
    padding-left: {h2_padding_left};
  }}

  p {{
    margin: {p_margin};
  }}

  strong {{
    font-weight: {weight_semibold};
    color: {color_heading};
  }}

  ul {{
    margin: {ul_margin};
    padding-left: {ul_padding_left};
  }}

  li {{
    margin-bottom: {li_margin_bottom};
  }}

  hr {{
    border: none;
    border-top: {hr_border_top} {color_rule};
    margin: {hr_margin};
  }}"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="{charset}">
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""
