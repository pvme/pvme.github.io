"""
Simple command line interface (CLI) to generate pvme-guides docs.
Mainly used for CI/CD integration.
"""
import argparse
import logging

from formatter.mkdocs import generate_sources


def main():
    return generate_sources()


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger('formatter.mkdocs').level = logging.DEBUG
    logging.getLogger('formatter.rules').level = logging.DEBUG
    logging.getLogger('formatter.util').level = logging.DEBUG

    exit(main())
