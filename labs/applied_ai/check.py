"""Offline acceptance cases. Run --week N; --reference checks the worked solutions."""

import argparse
import importlib
import unittest

parser = argparse.ArgumentParser()
parser.add_argument("--week", type=int, choices=range(9, 25))
parser.add_argument("--reference", action="store_true")
args = parser.parse_args()
lab = importlib.import_module("reference" if args.reference else "exercises")


class AppliedChecks(unittest.TestCase):
    def test_09_gradient(self):
        loss, gradient = lab.loss_gradient([1, 2], [2, 4], 1)
        self.assertEqual((loss, gradient), (2.5, -5))
        eps = 1e-5
        numerical = (
            lab.loss_gradient([1, 2], [2, 4], 1 + eps)[0]
            - lab.loss_gradient([1, 2], [2, 4], 1 - eps)[0]
        ) / (2 * eps)
        self.assertAlmostEqual(gradient, numerical)
        with self.assertRaises(ValueError):
            lab.loss_gradient([], [], 1)
        with self.assertRaises(ValueError):
            lab.loss_gradient([float("nan")], [1], 1)

    def test_10_train_validation(self):
        first = lab.train_linear([1, 2], [2, 4], [3], [6], 0.1, 20)
        second = lab.train_linear([1, 2], [2, 4], [3], [100], 0.1, 20)
        self.assertAlmostEqual(first["weight"], 2, places=5)
        self.assertEqual(first["weight"], second["weight"])
        self.assertLess(first["history"][-1]["train"], first["history"][0]["train"])
        self.assertGreater(second["history"][-1]["validation"], 1000)
        with self.assertRaises(ValueError):
            lab.train_linear([1], [2], [3], [6], -0.1, 20)

    def test_11_experiment_provenance(self):
        config = dict(data_version="d1", code_version="c1", seed=7, parameters={"lr": 0.1})
        self.assertEqual(
            lab.experiment_id(config), lab.experiment_id(dict(reversed(list(config.items()))))
        )
        self.assertNotEqual(
            lab.experiment_id(config), lab.experiment_id({**config, "data_version": "d2"})
        )
        with self.assertRaises(ValueError):
            lab.experiment_id({"seed": 7})

    def test_12_serving_contract(self):
        model = {"version": "linear-v1", "weight": 2}
        self.assertEqual(
            lab.predict_batch(model, [1, 3]), {"model_version": "linear-v1", "predictions": [2, 6]}
        )
        for values in ([], [1] * 101, [float("inf")], [True]):
            with self.assertRaises(ValueError):
                lab.predict_batch(model, values)

    def test_13_token_budget(self):
        self.assertEqual(
            lab.pack_context([[1, 2, 3], [4, 5], [6]], 5, 1),
            {"indices": [0, 2], "input_tokens": 4, "reserved_tokens": 1},
        )
        self.assertEqual(lab.pack_context([[1]], 1, 1)["indices"], [])
        with self.assertRaises(ValueError):
            lab.pack_context([[1]], 1, 2)

    def test_14_vector_rank(self):
        result = lab.cosine_rank([1, 0], {"b": [2, 0], "a": [1, 0], "c": [0, 1]}, 2)
        self.assertEqual(result, [("a", 1.0), ("b", 1.0)])
        with self.assertRaises(ValueError):
            lab.cosine_rank([0, 0], {}, 1)
        with self.assertRaises(ValueError):
            lab.cosine_rank([1, 0], {"bad": [1]}, 1)

    def test_15_citation_is_not_entailment(self):
        docs = {"d1": "Synthetic role requires Python."}
        claims = [{"claim": "Python is mentioned", "source_id": "d1", "quote": "Python"}]
        self.assertEqual(
            lab.validate_citations(claims, docs)["status"], "quotes_found_entailment_unassessed"
        )
        self.assertEqual(lab.validate_citations([], docs)["status"], "abstain")
        with self.assertRaises(ValueError):
            lab.validate_citations([{**claims[0], "quote": "Visa sponsorship"}], docs)
        with self.assertRaises(ValueError):
            lab.validate_citations([{**claims[0], "quote": ""}], docs)

    def test_16_evaluation_denominators(self):
        result = lab.retrieval_eval({"q1": ["a", "b"], "q2": []}, {"q1": ["a"], "q2": []})
        self.assertEqual(
            result, {"cases": 2, "answerable": 1, "recall": 0.5, "abstention_accuracy": 1.0}
        )
        self.assertIsNone(lab.retrieval_eval({}, {})["recall"])
        with self.assertRaises(ValueError):
            lab.retrieval_eval({"q1": ["a"]}, {})
        with self.assertRaises(ValueError):
            lab.retrieval_eval({"q1": ["a"]}, {"q1": ["a", "a"]})

    def test_17_tool_boundary(self):
        call = {"name": "read_document", "arguments": {"id": "d1"}}
        self.assertEqual(
            lab.dispatch_read(call, {"d1": "untrusted instructions remain text"}),
            "untrusted instructions remain text",
        )
        for bad in (
            {**call, "name": "delete_all"},
            {**call, "arguments": {"id": "d1", "shell": "anything"}},
            {**call, "arguments": {"id": "private"}},
        ):
            with self.assertRaises(ValueError):
                lab.dispatch_read(bad, {"d1": "ok"})

    def test_18_bounded_retry(self):
        self.assertEqual([lab.retry_delay(i, 503) for i in (1, 2, 3, 4)], [5, 10, None, None])
        self.assertIsNone(lab.retry_delay(1, 400))
        self.assertIsNone(lab.retry_delay(1, 200))
        with self.assertRaises(ValueError):
            lab.retry_delay(0, 503)

    def test_19_same_eval_comparison(self):
        baseline = {"eval_version": "heldout-v1", "quality": 0.5, "cost": 0.1}
        candidate = {**baseline, "quality": 0.75, "cost": 0.2}
        self.assertTrue(lab.compare_candidate(baseline, candidate, 0.125, 0.25))
        self.assertFalse(lab.compare_candidate(baseline, candidate, 0.125, 0.15))
        with self.assertRaises(ValueError):
            lab.compare_candidate(baseline, {**candidate, "eval_version": "tuned-v2"}, 0.1, 1)

    def test_20_usage_cost(self):
        self.assertAlmostEqual(lab.request_cost(1000, 500, 2, 8), 0.006)
        self.assertEqual(lab.request_cost(0, 0, 2, 8), 0)
        for usage in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                lab.request_cost(usage, 0, 2, 8)

    def test_21_allowlist_logs(self):
        data = {"status": "failed", "duration_ms": 7, "token": "secret", "body": "private"}
        self.assertEqual(lab.safe_event(data), {"status": "failed", "duration_ms": 7})
        self.assertEqual(data["token"], "secret")
        with self.assertRaises(ValueError):
            lab.safe_event({"status": "private text", "duration_ms": 1})

    def test_22_observation_sample(self):
        events = [{"status": "ok", "duration_ms": n} for n in range(1, 21)]
        events[-1]["status"] = "failed"
        self.assertEqual(lab.service_summary(events), {"n": 20, "error_rate": 0.05, "p95_ms": 19})
        self.assertEqual(lab.service_summary([]), {"n": 0, "error_rate": None, "p95_ms": None})

    def test_23_decision_structure(self):
        self.assertEqual(
            lab.decision_gaps(
                {
                    "context": "one learner",
                    "decision": "monolith",
                    "alternative": "services",
                    "tradeoff": "shared runtime",
                    "evidence": "test link",
                    "rollback": "   ",
                }
            ),
            ["rollback"],
        )
        self.assertIn("evidence", lab.decision_gaps({}))

    def test_24_claim_provenance(self):
        claims = [{"text": "Built a small validation example", "evidence_id": "e1"}]
        evidence = {"e1": {"url": "https://example.com/artifact", "assistance": "assisted"}}
        result = lab.claim_inventory(claims, evidence)
        self.assertEqual(result[0]["status"], "linked_not_verified")
        self.assertEqual(result[0]["assistance"], "assisted")
        with self.assertRaises(ValueError):
            lab.claim_inventory(claims, {})


suite = unittest.TestSuite()
for name in unittest.defaultTestLoader.getTestCaseNames(AppliedChecks):
    if args.week is None or name.startswith(f"test_{args.week:02d}_"):
        suite.addTest(AppliedChecks(name))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
