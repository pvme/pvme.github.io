"""
Simple command line interface (CLI) to generate pvme-guides docs.
Mainly used for CI/CD integration.
"""
import argparse
import logging

from formatter.mkdocs import generate_sources


def main():
    parser = argparse.ArgumentParser(description='CLI to integrate formatters in CI/CD.')

    parser.add_argument('--generate_mkdocs', nargs=3, type=str, metavar=('INPUT_DIR', 'OUTPUT_DIR', 'MKDOCS_YML'),
                        help='Generate mkdocs sources from the pvme-guides "guide.txt" files')

    match = parser.parse_args()

    if match.generate_mkdocs:
        result = generate_sources(*match.generate_mkdocs)
    else:
        result = 0

    return result


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger('formatter.mkdocs').level = logging.DEBUG
    logging.getLogger('formatter.rules').level = logging.DEBUG
    logging.getLogger('formatter.util').level = logging.DEBUG

    exit(main())
