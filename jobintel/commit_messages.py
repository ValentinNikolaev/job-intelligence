from __future__ import annotations

import argparse
from collections.abc import Sequence


COLLECTION_TEMPLATES = (
    "Bring in {active} active {active_noun} and set aside {rejected} {rejected_noun}",
    "Refresh the vacancy pool with {active} active {active_noun} ({rejected} rejected)",
    "Add {active} active {active_noun} after filtering out {rejected}",
    "Update the job search: {active} active, {rejected} rejected",
    "Collect {active} active {active_noun} and file {rejected} {rejected_noun}",
)

ARCHIVE_TEMPLATES = (
    "Archive {count} {reason} {noun}",
    "Clear {count} {reason} {noun} from the current registry",
    "Move {count} {reason} {noun} into the long-term archive",
    "File away {count} {reason} {noun}",
    "Tidy the registry by archiving {count} {reason} {noun}",
)


def _select_template(templates: Sequence[str], run_number: int) -> str:
    if run_number < 1:
        raise ValueError("run_number must be at least 1")
    return templates[(run_number - 1) % len(templates)]


def _noun(count: int, singular: str, plural: str) -> str:
    if count < 0:
        raise ValueError("counts must not be negative")
    return singular if count == 1 else plural


def collection_subject(run_number: int, active: int, rejected: int) -> str:
    template = _select_template(COLLECTION_TEMPLATES, run_number)
    return template.format(
        active=active,
        active_noun=_noun(active, "vacancy", "vacancies"),
        rejected=rejected,
        rejected_noun=_noun(rejected, "reject", "rejects"),
    )


def archive_subject(run_number: int, count: int, reason: str) -> str:
    if not reason.strip():
        raise ValueError("reason must not be empty")
    template = _select_template(ARCHIVE_TEMPLATES, run_number)
    return template.format(
        count=count,
        reason=reason.strip(),
        noun=_noun(count, "vacancy", "vacancies"),
    )


def _non_negative(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must not be negative")
    return parsed


def _positive(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Choose a deterministic GitHub workflow commit subject."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    collection = subparsers.add_parser("collection")
    collection.add_argument("--run-number", type=_positive, required=True)
    collection.add_argument("--active", type=_non_negative, required=True)
    collection.add_argument("--rejected", type=_non_negative, required=True)

    archive = subparsers.add_parser("archive")
    archive.add_argument("--run-number", type=_positive, required=True)
    archive.add_argument("--count", type=_non_negative, required=True)
    archive.add_argument("--reason", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.command == "collection":
        subject = collection_subject(
            arguments.run_number,
            arguments.active,
            arguments.rejected,
        )
    else:
        subject = archive_subject(
            arguments.run_number,
            arguments.count,
            arguments.reason,
        )
    print(subject)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
