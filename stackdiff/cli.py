"""Command-line interface for stackdiff."""
import sys
import argparse

from stackdiff.providers.registry import get_provider, available_providers
from stackdiff.diff import compute_diff
from stackdiff.formatters.text import format_diff as format_text
from stackdiff.formatters.json_fmt import format_diff as format_json


FORMATTERS = {
    "text": format_text,
    "json": format_json,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stackdiff",
        description="Compare deployed cloud infrastructure states across environments.",
    )
    parser.add_argument(
        "--provider",
        required=True,
        choices=available_providers(),
        help="Cloud provider to use.",
    )
    parser.add_argument(
        "--source",
        required=True,
        metavar="STACK",
        help="Source stack / environment name.",
    )
    parser.add_argument(
        "--target",
        required=True,
        metavar="STACK",
        help="Target stack / environment name.",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="text",
        choices=list(FORMATTERS.keys()),
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found.",
    )
    return parser


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    provider = get_provider(args.provider)

    source_state = provider.fetch_state(args.source)
    target_state = provider.fetch_state(args.target)

    result = compute_diff(source_state, target_state)

    formatter = FORMATTERS[args.fmt]
    print(formatter(result))

    if args.exit_code and result.has_changes():
        return 1
    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
