#!/usr/bin/env python3
"""CLI entry point. Run: python convert_to_pdf.py input.md [--pages N] [--config FILE]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import tomllib

from constants import (
    CLI_ARG_CONFIG,
    CLI_ARG_INPUT,
    CLI_ARG_PAGES,
    CLI_CONFIG_HELP,
    CLI_CONFIG_METAVAR,
    CLI_DESCRIPTION,
    CLI_INPUT_HELP,
    CLI_PAGES_HELP,
    CLI_PAGES_METAVAR,
    DEFAULT_CONFIG,
    ERR_CONFIG_NOT_FOUND,
    ERR_INPUT_NOT_FOUND,
    PDF_SUFFIX,
    TOML_READ_MODE,
)
from converter import convert


def load_config(path: Path) -> dict:
    """Parse a TOML config file and return it as a dict."""
    with path.open(TOML_READ_MODE) as fh:
        return tomllib.load(fh)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument(CLI_ARG_INPUT, type=Path, help=CLI_INPUT_HELP)
    parser.add_argument(CLI_ARG_PAGES, type=int, metavar=CLI_PAGES_METAVAR, help=CLI_PAGES_HELP)
    parser.add_argument(
        CLI_ARG_CONFIG,
        type=Path,
        default=DEFAULT_CONFIG,
        metavar=CLI_CONFIG_METAVAR,
        help=CLI_CONFIG_HELP.format(DEFAULT_CONFIG),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if not args.config.exists():
        sys.exit(ERR_CONFIG_NOT_FOUND.format(args.config))

    config = load_config(args.config)

    if not args.input.exists():
        sys.exit(ERR_INPUT_NOT_FOUND.format(args.input))

    convert(args.input, args.input.with_suffix(PDF_SUFFIX), config, args.pages)


if __name__ == "__main__":
    main()
