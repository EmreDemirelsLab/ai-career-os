"""Run locally only. Never execute uploaded learner code inside the API."""

import argparse
import importlib
import sqlite3
import unittest

from fastapi.testclient import TestClient

parser = argparse.ArgumentParser()
parser.add_argument("--week", type=int, choices=[1, 2, 3, 4])
parser.add_argument(
    "--reference", action="store_true", help="Assisted reference smoke, not mastery"
)
args = parser.parse_args()
exercise = importlib.import_module("reference" if args.reference else "exercises")


class Week1(unittest.TestCase):
    def test_normalize_without_mutation(self):
        data = {"source_job_id": " 42 ", "title": " Engineer "}
        original = data.copy()
        self.assertEqual(exercise.validate_job(data), {"source_job_id": "42", "title": "Engineer"})
        self.assertEqual(data, original)

    def test_invalid_inputs(self):
        for value in (
            None,
            {},
            {"source_job_id": "1", "title": 9},
            {"source_job_id": "1", "title": "   "},
            {"source_job_id": "1", "title": "a" * 201},
            {"source_job_id": "1", "title": "ok", "extra": "x"},
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                exercise.validate_job(value)


class Week2(unittest.TestCase):
    def test_constraints_and_zero_count(self):
        with sqlite3.connect(":memory:") as db:
            exercise.create_schema(db)
            exercise.create_schema(db)
            db.executemany("INSERT INTO sources VALUES (?,?)", [(1, "A"), (2, "B"), (3, "A")])
            db.executemany(
                "INSERT INTO jobs VALUES (?,?,?)", [(1, 1, "x"), (2, 1, "y"), (3, 3, "x")]
            )
            self.assertEqual(exercise.source_counts(db), [("A", 2), ("B", 0), ("A", 1)])
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO jobs VALUES (4,1,'x')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO jobs VALUES (5,999,'x')")


class Week3(unittest.TestCase):
    def test_valid_and_invalid_requests(self):
        with TestClient(exercise.create_app()) as client:
            response = client.post("/jobs", json={"source_job_id": " 1 ", "title": " Engineer "})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {"source_job_id": "1", "title": "Engineer"})
            for value in (
                {},
                {"source_job_id": "1", "title": " "},
                {"source_job_id": "1", "title": 7},
                {"source_job_id": "1", "title": "ok", "extra": 1},
            ):
                self.assertEqual(client.post("/jobs", json=value).status_code, 422)


class Week4(unittest.TestCase):
    def test_replay_changed_content_and_source_scope(self):
        store = {}
        row = dict(
            source_id="A",
            source_job_id="1",
            title="Engineer",
            description="Python",
            fetched_at="t1",
        )
        original = row.copy()
        self.assertEqual(exercise.ingest_revision(store, row), "inserted")
        self.assertEqual(row, original)
        self.assertEqual(exercise.ingest_revision(store, {**row, "fetched_at": "t2"}), "duplicate")
        self.assertEqual(exercise.ingest_revision(store, {**row, "description": "SQL"}), "revised")
        self.assertEqual(exercise.ingest_revision(store, {**row, "source_id": "B"}), "inserted")
        self.assertEqual(len(store), 2)
        before = store.copy()
        with self.assertRaises(ValueError):
            exercise.ingest_revision(store, {**row, "description": None})
        self.assertEqual(store, before)


suite = unittest.TestSuite()
for week, case in enumerate((Week1, Week2, Week3, Week4), 1):
    if args.week is None or week == args.week:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
