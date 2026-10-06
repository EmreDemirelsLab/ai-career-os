import argparse
import json
import logging
import os
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from career_os.collection_worker import work_one
from career_os.config import Settings
from career_os.contracts import FixtureAdapter
from career_os.db import build_engine
from career_os.governance import seed_sources, set_enabled
from career_os.greenhouse import collect_greenhouse
from career_os.ingestion import fail_run, ingest, inspect_run
from career_os.models import Source
from career_os.retention import retain_source
from career_os.scheduling import configure_schedule, enqueue_due, inspect_schedule


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trusted operator CLI; network sources require explicit source review"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    seed = sub.add_parser("seed")
    seed.add_argument("--path", type=Path, default=Path("seed/source_registry_seed.csv"))
    fixture = sub.add_parser("ingest-fixture")
    fixture.add_argument("--path", type=Path, default=Path("tests/fixtures/jobs.json"))
    fixture.add_argument("--key", required=True)
    state = sub.add_parser("source-state")
    state.add_argument("source_id")
    state.add_argument("state", choices=["enable", "disable"])
    inspect = sub.add_parser("run")
    inspect.add_argument("run_id")
    recover = sub.add_parser("fail-run")
    recover.add_argument("run_id")
    gh = sub.add_parser("collect-greenhouse")
    gh.add_argument("source_id")
    gh.add_argument("--board", required=True)
    gh.add_argument("--key", required=True)
    register = sub.add_parser("register-greenhouse")
    register.add_argument("source_id")
    register.add_argument("--name", required=True)
    register.add_argument("--board", required=True)
    register.add_argument("--policy-reference", required=True)
    register.add_argument("--reviewed-by", required=True)
    register.add_argument("--retention-days", type=int, required=True)
    retention = sub.add_parser("retention")
    retention.add_argument("source_id")
    retention.add_argument("--key", required=True)
    retention.add_argument("--apply", action="store_true")
    retention.add_argument("--confirm", default="")
    schedule = sub.add_parser("schedule-source")
    schedule.add_argument("source_id")
    schedule.add_argument("--interval-minutes", type=int, default=1440)
    schedule.add_argument("--state", choices=["enable", "disable"], required=True)
    tick = sub.add_parser("schedule-tick")
    tick.add_argument("--limit", type=int, default=25)
    show_schedule = sub.add_parser("schedule-status")
    show_schedule.add_argument("source_id")
    worker = sub.add_parser("collection-work")
    worker.add_argument("job_id")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if args.command == "retention":
        maintenance_url = os.environ.get("CAREER_MAINTENANCE_DATABASE_URL")
        if not maintenance_url:
            parser.exit(2, "Set a separate CAREER_MAINTENANCE_DATABASE_URL for maintenance\n")
        if args.apply and args.confirm != "delete-expired-source-data":
            parser.exit(2, "Apply requires --confirm delete-expired-source-data\n")
        try:
            engine = build_engine(maintenance_url)
        except Exception:
            parser.exit(2, "Invalid maintenance database configuration\n")
    else:
        engine = build_engine(Settings().database_url)
    try:
        if args.command == "collection-work":
            print(json.dumps(work_one(engine, args.job_id)))
        elif args.command == "schedule-source":
            configure_schedule(
                engine, args.source_id, args.interval_minutes, args.state == "enable"
            )
        elif args.command == "schedule-tick":
            print(json.dumps(enqueue_due(engine, args.limit)))
        elif args.command == "schedule-status":
            print(json.dumps(inspect_schedule(engine, args.source_id)))
        elif args.command == "retention":
            print(json.dumps(retain_source(engine, args.source_id, args.key, apply=args.apply)))
        elif args.command == "register-greenhouse":
            import re

            if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", args.board):
                raise ValueError("invalid_board")
            if not (1 <= args.retention_days <= 365):
                raise ValueError("invalid_retention_days")
            if not (
                1 <= len(args.source_id) <= 80
                and 1 <= len(args.name) <= 200
                and 1 <= len(args.policy_reference) <= 500
                and 1 <= len(args.reviewed_by) <= 120
            ):
                raise ValueError("invalid_source_metadata")
            with Session(engine) as session, session.begin():
                if session.get(Source, args.source_id):
                    raise ValueError("source_already_exists")
                session.add(
                    Source(
                        id=args.source_id,
                        name=args.name,
                        source_type="greenhouse",
                        enabled=False,
                        policy_status="APPROVED",
                        collection_method="greenhouse:" + args.board,
                        policy_reference=args.policy_reference,
                        reviewed_by=args.reviewed_by,
                        retention_days=args.retention_days,
                    )
                )
        elif args.command == "collect-greenhouse":
            result = collect_greenhouse(engine, args.source_id, args.board, args.key)
            print(json.dumps(result))
            if result["status"] == "FAILED":
                raise SystemExit(1)
        elif args.command == "seed":
            seed_sources(engine, args.path)
        elif args.command == "source-state":
            set_enabled(engine, args.source_id, args.state == "enable")
        elif args.command == "fail-run":
            fail_run(engine, args.run_id)
        elif args.command == "run":
            print(json.dumps(inspect_run(engine, args.run_id)))
        else:
            if args.path.stat().st_size > 5_000_000:
                raise ValueError("fixture_exceeds_5MB")
            records = json.loads(args.path.read_text())
            if not isinstance(records, list) or len(records) > 1000:
                raise ValueError("fixture_must_be_list_max_1000")
            result = ingest(engine, "DEMO", args.key, FixtureAdapter(records))
            print(json.dumps(result))
            if result["status"] == "FAILED":
                raise SystemExit(1)
    except SQLAlchemyError:
        parser.exit(2, "Database operation refused; inspect maintenance permissions and policy\n")
    except ValueError as exc:
        parser.exit(2, f"Operation refused: {exc}\n")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
