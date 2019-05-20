#!/usr/bin/env python3

"""Command-line interface for wiki2beamer."""

import sys

from .main import main


def cli() -> None:
    """Entry point for the command-line interface."""
    main(sys.argv)


if __name__ == "__main__":
    cli()
