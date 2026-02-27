"""Unit tests for the Markdown-to-PDF converter modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from constants import (
    ENCODING,
    FONT_SCALE_MAX,
    FONT_SCALE_MIN,
    FONT_WEIGHT_BOLD,
    FONT_WEIGHT_SEMIBOLD,
    H1_BORDER,
    H2_BORDER,
    HR_BORDER_TOP,
)
from convert_to_pdf import load_config
from converter import find_scale_for_pages
from style import build_css, build_html, scale_pt

# ── Shared fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def minimal_config() -> dict:
    """Minimal config dict matching the structure expected by build_css."""
    return {
        "files": {"input": "test.md"},
        "page": {"size": "A4", "margin": "1cm"},
        "markdown": {"extensions": ["tables"]},
        "style": {
            "fonts": {
                "body": "Arial, sans-serif",
                "heading": "Georgia, serif",
                "body_size": "10pt",
                "line_height": "1.5",
                "h1_size": "18pt",
                "h2_size": "12pt",
            },
            "colors": {
                "body_text": "#000000",
                "background": "#ffffff",
                "heading": "#111111",
                "accent": "#336699",
                "rule": "#cccccc",
            },
            "spacing": {
                "h1_margin": "0 0 4px 0",
                "h2_margin": "8px 0 3px 0",
                "p_margin": "0 0 4px 0",
                "ul_margin": "3px 0 4px 0",
                "ul_padding_left": "16px",
                "li_margin_bottom": "2px",
                "hr_margin": "6px 0",
            },
        },
    }


# ── scale_pt ──────────────────────────────────────────────────────────────────


class TestScalePt:
    def test_identity_scale_preserves_value(self):
        assert scale_pt("9.5pt", 1.0) == "9.50pt"

    def test_scale_up_doubles_value(self):
        assert scale_pt("10pt", 2.0) == "20.00pt"

    def test_scale_down_halves_value(self):
        assert scale_pt("20pt", 0.5) == "10.00pt"

    def test_fractional_scale_rounds_to_two_decimal_places(self):
        assert scale_pt("9.5pt", 1.2) == "11.40pt"

    def test_output_always_ends_with_pt(self):
        assert scale_pt("12pt", 1.5).endswith("pt")


# ── build_css ─────────────────────────────────────────────────────────────────


class TestBuildCss:
    def test_page_size_present(self, minimal_config):
        assert "A4" in build_css(minimal_config)

    def test_page_margin_present(self, minimal_config):
        assert "1cm" in build_css(minimal_config)

    def test_body_font_present(self, minimal_config):
        assert "Arial, sans-serif" in build_css(minimal_config)

    def test_heading_font_present(self, minimal_config):
        assert "Georgia, serif" in build_css(minimal_config)

    def test_colors_present(self, minimal_config):
        css = build_css(minimal_config)
        assert "#000000" in css
        assert "#ffffff" in css
        assert "#336699" in css

    def test_font_scale_applied_to_body_size(self, minimal_config):
        # body_size "10pt" * 2.0 = "20.00pt"
        assert "20.00pt" in build_css(minimal_config, font_scale=2.0)

    def test_font_scale_applied_to_h1_size(self, minimal_config):
        # h1_size "18pt" * 0.5 = "9.00pt"
        assert "9.00pt" in build_css(minimal_config, font_scale=0.5)

    def test_font_scale_applied_to_h2_size(self, minimal_config):
        # h2_size "12pt" * 0.5 = "6.00pt"
        assert "6.00pt" in build_css(minimal_config, font_scale=0.5)

    def test_structural_constants_embedded(self, minimal_config):
        css = build_css(minimal_config)
        assert H1_BORDER in css
        assert H2_BORDER in css
        assert HR_BORDER_TOP in css
        assert str(FONT_WEIGHT_BOLD) in css
        assert str(FONT_WEIGHT_SEMIBOLD) in css

    def test_default_scale_matches_explicit_scale_of_one(self, minimal_config):
        assert build_css(minimal_config) == build_css(minimal_config, font_scale=1.0)


# ── build_html ────────────────────────────────────────────────────────────────


class TestBuildHtml:
    def test_charset_is_encoding_constant(self):
        assert ENCODING in build_html(body="<p>x</p>", css="")

    def test_body_content_present(self):
        body = "<p>Hello world</p>"
        assert body in build_html(body=body, css="")

    def test_css_embedded_in_document(self):
        css = "body { color: red; }"
        assert css in build_html(body="", css=css)

    def test_produces_valid_html_skeleton(self):
        html = build_html(body="<p>x</p>", css="")
        expected_tags = [
            "<!DOCTYPE html>", "<html>", "</html>", "<head>", "</head>", "<body>", "</body>",
        ]
        for tag in expected_tags:
            assert tag in html


# ── load_config ───────────────────────────────────────────────────────────────


class TestLoadConfig:
    def test_loads_valid_toml(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('[page]\nsize = "A4"\n', encoding=ENCODING)
        assert load_config(config_file)["page"]["size"] == "A4"

    def test_raises_on_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.toml")

    def test_nested_keys_accessible(self, tmp_path: Path):
        config_file = tmp_path / "config.toml"
        config_file.write_text('[style.colors]\nbody_text = "#000"\n', encoding=ENCODING)
        assert load_config(config_file)["style"]["colors"]["body_text"] == "#000"


# ── find_scale_for_pages ──────────────────────────────────────────────────────


class TestFindScaleForPages:
    """Uses a mock render() to control page counts without WeasyPrint."""

    def test_returns_max_scale_when_content_always_fits(self, minimal_config):
        with patch("converter.render", return_value=(b"pdf", 1)):
            scale = find_scale_for_pages(
                target=2, config=minimal_config, html_body="<p>short</p>", base_url="."
            )
        assert scale == FONT_SCALE_MAX

    def test_returns_min_scale_when_content_never_fits(self, minimal_config):
        with patch("converter.render", return_value=(b"pdf", 5)):
            scale = find_scale_for_pages(
                target=2, config=minimal_config, html_body="<p>long</p>", base_url="."
            )
        assert scale == FONT_SCALE_MIN

    def test_result_is_within_valid_range(self, minimal_config):
        def fake_render(html: str, base_url: str) -> tuple[bytes, int]:
            pages = 3 if "20.00pt" in html else 1
            return b"pdf", pages

        with patch("converter.render", side_effect=fake_render):
            scale = find_scale_for_pages(
                target=2, config=minimal_config, html_body="<p>content</p>", base_url="."
            )

        assert FONT_SCALE_MIN <= scale <= FONT_SCALE_MAX
