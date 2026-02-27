"""CSS and HTML document construction."""

from constants import (
    CSS_TEMPLATE,
    DEFAULT_FONT_SCALE,
    ENCODING,
    FONT_UNIT,
    FONT_WEIGHT_BOLD,
    FONT_WEIGHT_SEMIBOLD,
    H1_BORDER,
    H1_LETTER_SPACING,
    H1_PADDING_BOTTOM,
    H2_BORDER,
    H2_PADDING_LEFT,
    HR_BORDER_TOP,
    HTML_TEMPLATE,
    SCALE_PT_FORMAT,
)


def scale_pt(size_str: str, factor: float) -> str:
    """Scale a CSS pt string by a factor. e.g. scale_pt("9.5pt", 1.2) -> "11.40pt"."""
    numeric_value = float(size_str.rstrip(FONT_UNIT))
    return SCALE_PT_FORMAT.format(numeric_value * factor, FONT_UNIT)


def build_css(config: dict, font_scale: float = DEFAULT_FONT_SCALE) -> str:
    """Build the document CSS, scaling body/h1/h2 font sizes by font_scale."""
    page = config["page"]
    fonts = config["style"]["fonts"]
    colors = config["style"]["colors"]
    spacing = config["style"]["spacing"]

    return CSS_TEMPLATE.format(
        page_size=page["size"],
        page_margin=page["margin"],
        body_font=fonts["body"],
        body_size=scale_pt(fonts["body_size"], font_scale),
        line_height=fonts["line_height"],
        color_body_text=colors["body_text"],
        color_background=colors["background"],
        heading_font=fonts["heading"],
        h1_size=scale_pt(fonts["h1_size"], font_scale),
        weight_bold=FONT_WEIGHT_BOLD,
        color_heading=colors["heading"],
        h1_border=H1_BORDER,
        color_accent=colors["accent"],
        h1_padding_bottom=H1_PADDING_BOTTOM,
        h1_margin=spacing["h1_margin"],
        h1_letter_spacing=H1_LETTER_SPACING,
        h2_size=scale_pt(fonts["h2_size"], font_scale),
        h2_margin=spacing["h2_margin"],
        h2_border=H2_BORDER,
        h2_padding_left=H2_PADDING_LEFT,
        p_margin=spacing["p_margin"],
        weight_semibold=FONT_WEIGHT_SEMIBOLD,
        ul_margin=spacing["ul_margin"],
        ul_padding_left=spacing["ul_padding_left"],
        li_margin_bottom=spacing["li_margin_bottom"],
        hr_border_top=HR_BORDER_TOP,
        color_rule=colors["rule"],
        hr_margin=spacing["hr_margin"],
    )


def build_html(body: str, css: str) -> str:
    """Wrap a Markdown-rendered body and CSS into a complete HTML document."""
    return HTML_TEMPLATE.format(charset=ENCODING, css=css, body=body)
