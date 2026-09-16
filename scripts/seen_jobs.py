"""Local JSONL state helper for Easy Apply seen jobs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from lib.identity import build_job_key, build_source_identity

VALID_DECISIONS = {"keep", "reject", "needs_verification"}


def state_file(workspace: str | Path) -> Path:
    return Path(workspace).expanduser().resolve() / "state" / "seen-jobs.jsonl"


def read_events(workspace: str | Path) -> list[dict[str, Any]]:
    path = state_file(workspace)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_no}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_no}")
            events.append(value)
    return events


def latest_records(workspace: str | Path) -> list[dict[str, Any]]:
    """Collapse append-only history so the latest event wins per job_key."""
    latest: dict[str, dict[str, Any]] = {}
    for event in read_events(workspace):
        key = str(event.get("job_key") or "")
        if key:
            latest[key] = event
    return list(latest.values())


def find_seen_job(
    workspace: str | Path,
    *,
    source: str | None = None,
    source_job_id: str | None = None,
    canonical_url: str | None = None,
    job_key: str | None = None,
) -> dict[str, Any] | None:
    records = latest_records(workspace)

    if source and source_job_id:
        target = build_source_identity(source, source_job_id)
        for record in records:
            current = build_source_identity(record.get("source", ""), record.get("source_job_id"))
            if current == target:
                return record

    if canonical_url:
        target_url = canonical_url.strip()
        for record in records:
            if str(record.get("canonical_url") or "").strip() == target_url:
                return record

    if job_key:
        for record in records:
            if record.get("job_key") == job_key:
                return record

    return None


def add_seen_job(
    workspace: str | Path,
    *,
    job_key: str,
    source: str,
    decision: str,
    source_job_id: str | None = None,
    canonical_url: str | None = None,
) -> dict[str, Any]:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision: {decision}")

    now = datetime.now().astimezone().isoformat(timespec="seconds")
    previous = find_seen_job(
        workspace,
        source=source,
        source_job_id=source_job_id,
        canonical_url=canonical_url,
        job_key=job_key,
    )

    record = {
        "job_key": job_key,
        "source": source.strip().lower(),
        "source_job_id": source_job_id.strip() if source_job_id else None,
        "canonical_url": canonical_url.strip() if canonical_url else None,
        "decision": decision,
        "first_seen": previous.get("first_seen", now) if previous else now,
        "last_seen": now,
    }

    path = state_file(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Easy Apply seen-jobs state helper")
    sub = parser.add_subparsers(dest="command", required=True)

    find_cmd = sub.add_parser("find")
    find_cmd.add_argument("--workspace", required=True)
    find_cmd.add_argument("--source")
    find_cmd.add_argument("--source-job-id")
    find_cmd.add_argument("--canonical-url")
    find_cmd.add_argument("--job-key")
    find_cmd.add_argument("--company")
    find_cmd.add_argument("--title")
    find_cmd.add_argument("--location")

    add_cmd = sub.add_parser("add")
    add_cmd.add_argument("--workspace", required=True)
    add_cmd.add_argument("--source", required=True)
    add_cmd.add_argument("--source-job-id")
    add_cmd.add_argument("--canonical-url")
    add_cmd.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    add_cmd.add_argument("--job-key")
    add_cmd.add_argument("--company")
    add_cmd.add_argument("--title")
    add_cmd.add_argument("--location")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--workspace", required=True)
    return parser


def resolve_job_key(args: argparse.Namespace) -> str | None:
    if getattr(args, "job_key", None):
        return args.job_key
    company = getattr(args, "company", None)
    title = getattr(args, "title", None)
    location = getattr(args, "location", None)
    if company and title and location:
        return build_job_key(company, title, location)
    return None


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        print(json.dumps(latest_records(args.workspace), ensure_ascii=False, indent=2))
        return 0

    job_key = resolve_job_key(args)

    if args.command == "find":
        record = find_seen_job(
            args.workspace,
            source=args.source,
            source_job_id=args.source_job_id,
            canonical_url=args.canonical_url,
            job_key=job_key,
        )
        if record is None:
            return 1
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0

    if not job_key:
        parser.error("add requires --job-key or --company + --title + --location")

    record = add_seen_job(
        args.workspace,
        job_key=job_key,
        source=args.source,
        source_job_id=args.source_job_id,
        canonical_url=args.canonical_url,
        decision=args.decision,
    )
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
