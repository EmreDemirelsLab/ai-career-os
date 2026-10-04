import argparse
import json
import logging
from pathlib import Path

from career_os.config import Settings
from career_os.contracts import FixtureAdapter
from career_os.db import build_engine
from career_os.governance import seed_sources, set_enabled
from career_os.ingestion import fail_run, ingest, inspect_run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local trusted operator CLI; no network collection"
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
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    engine = build_engine(Settings().database_url)
    try:
        if args.command == "seed":
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
    except ValueError as exc:
        parser.exit(2, f"Operation refused: {exc}\n")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
