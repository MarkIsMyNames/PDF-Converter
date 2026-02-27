"""Core PDF conversion pipeline."""

from pathlib import Path

import markdown
from weasyprint import HTML

from constants import (
    BINARY_SEARCH_ITERATIONS,
    DEFAULT_FONT_SCALE,
    ENCODING,
    FONT_SCALE_MAX,
    FONT_SCALE_MIN,
    FONT_SCALE_TOLERANCE,
    MSG_FITTING,
    MSG_PDF_CREATED,
    PLURAL_SUFFIX,
)
from style import build_css, build_html


def render(html: str, base_url: str) -> tuple[bytes, int]:
    """Render HTML to PDF via WeasyPrint and return (pdf_bytes, page_count).

    Page count is read from Document.pages, avoiding a separate PDF library.
    """
    document = HTML(string=html, base_url=base_url).render()
    return document.write_pdf(), len(document.pages)


def find_scale_for_pages(
    target: int, config: dict, html_body: str, base_url: str
) -> float:
    """Binary search for the largest font scale that fits content in target pages.

    Searches [FONT_SCALE_MIN, FONT_SCALE_MAX]. Returns the largest scale where
    page_count <= target, giving the biggest text that still fits.
    """

    def count_pages_at_scale(scale: float) -> int:
        _pdf_bytes, pages = render(build_html(html_body, build_css(config, scale)), base_url)
        return pages

    if count_pages_at_scale(FONT_SCALE_MIN) > target:
        return FONT_SCALE_MIN  # can't fit even at minimum scale

    if count_pages_at_scale(FONT_SCALE_MAX) <= target:
        return FONT_SCALE_MAX  # fits even at maximum scale

    # Narrow the interval until the scale gap drops below tolerance.
    # Invariant: count_pages_at_scale(lo) <= target < count_pages_at_scale(hi)
    lo: float = FONT_SCALE_MIN
    hi: float = FONT_SCALE_MAX

    for _ in range(BINARY_SEARCH_ITERATIONS):
        if hi - lo < FONT_SCALE_TOLERANCE:
            break
        mid: float = (lo + hi) / 2
        if count_pages_at_scale(mid) <= target:
            lo = mid  # fits; try a larger font
        else:
            hi = mid  # overflows; try a smaller font

    return lo


def convert(
    input_path: Path,
    output_path: Path,
    config: dict,
    target_pages: int | None,
) -> None:
    """Run the Markdown-to-PDF pipeline.

    Scales font size via binary search when target_pages is set;
    otherwise renders at the font sizes defined in config.
    """
    html_body = markdown.markdown(
        input_path.read_text(encoding=ENCODING),
        extensions=config["markdown"]["extensions"],
    )
    base_url = str(input_path.parent)

    if target_pages is not None:
        print(MSG_FITTING.format(target_pages, PLURAL_SUFFIX if target_pages != 1 else ""))
        font_scale = find_scale_for_pages(target_pages, config, html_body, base_url)
    else:
        font_scale = DEFAULT_FONT_SCALE

    pdf_bytes, pages = render(build_html(html_body, build_css(config, font_scale)), base_url)
    output_path.write_bytes(pdf_bytes)
    print(MSG_PDF_CREATED.format(output_path, pages, PLURAL_SUFFIX if pages != 1 else ""))
