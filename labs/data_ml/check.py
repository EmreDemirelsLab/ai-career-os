"""Local authored exercise checks; not an API code-execution service."""

import argparse
import importlib
import unittest

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--week", type=int, choices=[5, 6, 7, 8])
parser.add_argument("--reference", action="store_true")
args = parser.parse_args()
exercise = importlib.import_module("reference" if args.reference else "exercises")


def sample():
    return pd.DataFrame(
        dict(
            customer_id=["A", "A", "B", "C", "C"],
            value=[1.0, None, 3.0, 100.0, None],
            target=[0, 0, 1, 1, 0],
        )
    )


class Week5(unittest.TestCase):
    def test_missingness_and_empty_denominator(self):
        data = sample()
        before = data.copy(deep=True)
        self.assertEqual(
            exercise.summarize(data),
            dict(rows=5, missing_values=2, missing_rate=0.4, target_counts={"0": 3, "1": 2}),
        )
        pd.testing.assert_frame_equal(data, before)
        self.assertIsNone(exercise.summarize(data.iloc[:0])["missing_rate"])
        with self.assertRaises(ValueError):
            exercise.summarize(data.drop(columns="target"))


class Week6(unittest.TestCase):
    def test_groups_and_train_only_imputation(self):
        data = sample()
        before = data.copy(deep=True)
        train, test, mean = exercise.prepare_split(data, {"C"})
        self.assertEqual(mean, 2.0)
        self.assertEqual(train["value"].tolist(), [1.0, 2.0, 3.0])
        self.assertEqual(test["value"].tolist(), [100.0, 2.0])
        self.assertFalse(set(train["customer_id"]) & set(test["customer_id"]))
        pd.testing.assert_frame_equal(data, before)
        for groups in (set(), {"A", "B", "C"}, {"missing"}):
            with self.assertRaises(ValueError):
                exercise.prepare_split(data, groups)
        broken = data.copy()
        broken.loc[broken["customer_id"] != "C", "value"] = float("nan")
        with self.assertRaises(ValueError):
            exercise.prepare_split(broken, {"C"})


class Week7(unittest.TestCase):
    def test_majority_is_not_rare_class_recall(self):
        prediction = exercise.majority_predict([0, 0, 0, 1], 4)
        self.assertEqual(prediction, [0, 0, 0, 0])
        result = exercise.binary_metrics([0, 0, 0, 1], prediction)
        self.assertEqual(result["accuracy"], 0.75)
        self.assertEqual(result["recall"], 0.0)
        self.assertIsNone(result["precision"])
        self.assertEqual(exercise.majority_predict([1, 0], 2), [0, 0])

    def test_confusion_counts_and_invalid_lengths(self):
        result = exercise.binary_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(
            result, dict(tp=1, fp=1, fn=1, tn=1, accuracy=0.5, precision=0.5, recall=0.5, f1=0.5)
        )
        self.assertIsNone(exercise.binary_metrics([0], [0])["f1"])
        for truth, pred in (([], []), ([1], []), ([2], [1])):
            with self.assertRaises(ValueError):
                exercise.binary_metrics(truth, pred)


class Week8(unittest.TestCase):
    def test_threshold_boundary_and_slice_sizes(self):
        self.assertEqual(exercise.threshold_predict([0.1, 0.5, 0.9], 0.5), [0, 1, 1])
        for scores, threshold in (([float("nan")], 0.5), ([1.2], 0.5), ([0.2], -1)):
            with self.assertRaises(ValueError):
                exercise.threshold_predict(scores, threshold)
        data = pd.DataFrame(
            dict(slice=["A", "A", "B", None], target=[1, 0, 1, 0], prediction=[0, 1, 1, 0])
        )
        before = data.copy(deep=True)
        self.assertEqual(
            exercise.error_slices(data),
            {
                "A": dict(n=2, fp=1, fn=1, recall=0.0),
                "B": dict(n=1, fp=0, fn=0, recall=1.0),
                "unknown": dict(n=1, fp=0, fn=0, recall=None),
            },
        )
        pd.testing.assert_frame_equal(data, before)


suite = unittest.TestSuite()
for week, case in enumerate((Week5, Week6, Week7, Week8), 5):
    if args.week is None or args.week == week:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
