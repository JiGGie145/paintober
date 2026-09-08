"""Isolated correctness and benchmark exercise for merge_small_regions.

This module intentionally exercises only label-map inputs and outputs. It does
not call Django, run_pipeline, load images, or touch the filesystem.
"""

from __future__ import annotations

import time
import unittest
from unittest import mock
from typing import Dict, Tuple

import numpy as np
from scipy import ndimage

from .processor import _merge_small_regions_python, merge_small_regions

try:
    import paintober_native
except ImportError:
    paintober_native = None


Structure = np.ndarray


def reference_merge_small_regions(
    label_map: np.ndarray,
    min_region_pixels: int,
) -> np.ndarray:
    """Frozen copy of the pre-optimization implementation.

    Keep this implementation independent from the production function. It is
    the behavioral oracle for the coordinate-storage rewrite.
    """
    result = label_map.copy()
    structure = np.ones((3, 3), dtype=int)

    for _ in range(6):
        changed = False
        component_map = np.zeros_like(result, dtype=np.int64)
        component_sizes: Dict[int, int] = {}
        component_labels: Dict[int, int] = {}
        next_id = 1

        for label in np.unique(result):
            components, count = ndimage.label(result == label, structure=structure)
            label_mask = result == label
            component_map[label_mask] = (components + next_id - 1)[label_mask]
            for component_id in range(1, count + 1):
                global_id = component_id + next_id - 1
                component_sizes[global_id] = int(
                    np.sum(components == component_id)
                )
                component_labels[global_id] = int(label)
            next_id += count

        small_ids = sorted(
            (
                component_id
                for component_id, size in component_sizes.items()
                if size < min_region_pixels
            ),
            key=component_sizes.get,
        )
        if not small_ids:
            break

        for component_id in small_ids:
            mask = component_map == component_id
            if not mask.any():
                continue
            border = ndimage.binary_dilation(mask, structure=structure) & ~mask
            neighbours = component_map[border]
            neighbours = neighbours[neighbours != component_id]
            if neighbours.size == 0:
                continue
            values, counts = np.unique(neighbours, return_counts=True)
            winner = int(values[np.argmax(counts)])
            result[mask] = component_labels[winner]
            changed = True

        if not changed:
            break

    return result


def _assert_matches_oracle(
    testcase: unittest.TestCase,
    label_map: np.ndarray,
    min_region_pixels: int,
) -> None:
    original = label_map.copy()
    expected = reference_merge_small_regions(label_map, min_region_pixels)
    actual = merge_small_regions(label_map, min_region_pixels)

    testcase.assertTrue(np.array_equal(actual, expected))
    testcase.assertEqual(actual.shape, label_map.shape)
    testcase.assertEqual(actual.dtype, label_map.dtype)
    testcase.assertTrue(np.array_equal(label_map, original))


class MergeSmallRegionsTests(unittest.TestCase):
    def test_requires_multiple_merge_passes(self):
        label_map = np.array(
            [
                [4, 2, 3],
                [0, 4, 1],
                [3, 2, 2],
            ],
            dtype=np.int32,
        )

        expected_after_first_pass = np.array(
            [
                [4, 4, 1],
                [4, 4, 2],
                [0, 2, 2],
            ],
            dtype=np.int32,
        )
        expected_after_two_passes = np.array(
            [
                [4, 4, 4],
                [4, 4, 2],
                [4, 2, 2],
            ],
            dtype=np.int32,
        )

        _assert_matches_oracle(self, label_map, min_region_pixels=2)
        self.assertTrue(
            np.array_equal(
                reference_merge_small_regions(label_map, 2),
                expected_after_two_passes,
            )
        )
        self.assertFalse(
            np.array_equal(expected_after_first_pass, expected_after_two_passes)
        )

    def test_stops_after_six_passes(self):
        label_map = np.array(
            [
                [3, 1, 0],
                [4, 2, 4],
                [4, 2, 4],
            ],
            dtype=np.int32,
        )
        expected_after_six_passes = np.array(
            [
                [0, 1, 0],
                [4, 2, 4],
                [4, 2, 4],
            ],
            dtype=np.int32,
        )
        expected_after_seven_passes = np.array(
            [
                [1, 0, 1],
                [4, 2, 4],
                [4, 2, 4],
            ],
            dtype=np.int32,
        )

        _assert_matches_oracle(self, label_map, min_region_pixels=2)
        actual = reference_merge_small_regions(label_map, 2)
        self.assertTrue(np.array_equal(actual, expected_after_six_passes))
        self.assertFalse(np.array_equal(actual, expected_after_seven_passes))

    def test_single_label_map_is_unchanged(self):
        label_map = np.full((4, 5), 7, dtype=np.int32)

        _assert_matches_oracle(self, label_map, min_region_pixels=100)
        self.assertTrue(np.array_equal(merge_small_regions(label_map, 100), label_map))

    def test_already_stable_map_is_unchanged(self):
        label_map = np.array(
            [
                [0, 0, 0, 1, 1, 1],
                [0, 0, 0, 1, 1, 1],
                [0, 0, 0, 1, 1, 1],
            ],
            dtype=np.int32,
        )

        _assert_matches_oracle(self, label_map, min_region_pixels=3)
        self.assertTrue(np.array_equal(merge_small_regions(label_map, 3), label_map))

    def test_small_island_is_merged(self):
        label_map = np.zeros((8, 8), dtype=np.int32)
        label_map[3:5, 3:5] = 1

        _assert_matches_oracle(self, label_map, min_region_pixels=5)
        expected = np.zeros_like(label_map)
        self.assertTrue(np.array_equal(merge_small_regions(label_map, 5), expected))

    def test_diagonal_pixels_are_connected(self):
        label_map = np.zeros((5, 5), dtype=np.int32)
        label_map[1, 1] = 1
        label_map[2, 2] = 1

        _assert_matches_oracle(self, label_map, min_region_pixels=3)
        expected = np.zeros_like(label_map)
        self.assertTrue(np.array_equal(merge_small_regions(label_map, 3), expected))

    def test_component_at_threshold_is_not_merged(self):
        label_map = np.zeros((5, 5), dtype=np.int32)
        label_map[1:3, 1:3] = 1

        _assert_matches_oracle(self, label_map, min_region_pixels=4)
        self.assertTrue(np.array_equal(merge_small_regions(label_map, 4), label_map))

    def test_component_larger_than_threshold_is_not_merged(self):
        label_map = np.zeros((5, 5), dtype=np.int32)
        label_map[1:4, 1:4] = 1

        _assert_matches_oracle(self, label_map, min_region_pixels=4)
        self.assertTrue(np.array_equal(merge_small_regions(label_map, 4), label_map))

    def test_zero_and_negative_thresholds_are_no_ops(self):
        label_map = np.array(
            [[0, 1, 0], [1, 1, 0], [0, 0, 0]],
            dtype=np.int32,
        )

        for threshold in (0, -1):
            _assert_matches_oracle(self, label_map, threshold)
            self.assertTrue(
                np.array_equal(merge_small_regions(label_map, threshold), label_map)
            )

    def test_strongest_neighbour_wins(self):
        label_map = np.array(
            [
                [2, 2, 2, 2, 2, 2],
                [2, 1, 1, 1, 0, 0],
                [2, 1, 1, 1, 0, 0],
                [2, 2, 2, 2, 0, 0],
            ],
            dtype=np.int32,
        )

        _assert_matches_oracle(self, label_map, min_region_pixels=10)
        actual = merge_small_regions(label_map, 10)
        self.assertTrue(np.all(actual[1:3, 1:4] == 2))

    def test_equal_neighbour_votes_choose_smallest_component_id(self):
        label_map = np.array(
            [
                [2, 2, 1, 3, 3],
                [2, 2, 2, 3, 3],
                [2, 2, 1, 3, 3],
                [2, 2, 2, 3, 3],
                [2, 2, 2, 3, 3],
            ],
            dtype=np.int32,
        )

        _assert_matches_oracle(self, label_map, min_region_pixels=3)
        actual = merge_small_regions(label_map, 3)
        self.assertEqual(actual[0, 2], 2)
        self.assertEqual(actual[2, 2], 2)

    def test_non_contiguous_labels_match_oracle(self):
        label_map = np.array(
            [[10, 10, 25, 25], [10, 100, 100, 25], [10, 100, 100, 25]],
            dtype=np.int64,
        )
        _assert_matches_oracle(self, label_map, min_region_pixels=3)

    def test_isolated_component_is_unchanged(self):
        label_map = np.zeros((1, 1), dtype=np.int32)
        label_map[0, 0] = 42

        _assert_matches_oracle(self, label_map, min_region_pixels=2)
        self.assertEqual(merge_small_regions(label_map, 2)[0, 0], 42)

    def test_one_row_and_one_column_maps(self):
        for label_map in (
            np.array([[0, 1, 1, 0, 2]], dtype=np.int32),
            np.array([[0], [1], [1], [0], [2]], dtype=np.int32),
        ):
            _assert_matches_oracle(self, label_map, min_region_pixels=3)

    def test_empty_two_dimensional_maps_return_unchanged_copies(self):
        for label_map in (
            np.empty((0, 0), dtype=np.int32),
            np.empty((0, 4), dtype=np.int64),
            np.empty((4, 0), dtype=np.uint16),
        ):
            actual = merge_small_regions(label_map, 3)
            self.assertTrue(np.array_equal(actual, label_map))
            self.assertEqual(actual.shape, label_map.shape)
            self.assertEqual(actual.dtype, label_map.dtype)
            self.assertIsNot(actual, label_map)

    def test_integer_dtypes_preserve_dtype_and_match_oracle(self):
        values = np.array(
            [[0, 1, 1, 2], [0, 3, 1, 2], [4, 3, 3, 2]],
            dtype=np.int64,
        )

        for dtype in (
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
        ):
            with self.subTest(dtype=dtype):
                label_map = values.astype(dtype)
                _assert_matches_oracle(self, label_map, min_region_pixels=4)

    def test_threshold_larger_than_map_matches_oracle(self):
        label_map = np.array([[4, 4, 9]], dtype=np.int32)

        _assert_matches_oracle(self, label_map, min_region_pixels=100)

    def test_repeated_calls_are_deterministic(self):
        label_map = np.array(
            [[0, 1, 0, 2], [1, 1, 2, 2], [0, 3, 3, 0]],
            dtype=np.int32,
        )

        first = merge_small_regions(label_map, 4)
        second = merge_small_regions(label_map, 4)
        self.assertTrue(np.array_equal(first, second))
        _assert_matches_oracle(self, label_map, min_region_pixels=4)

    def test_seeded_random_maps_match_oracle(self):
        rng = np.random.default_rng(20260828)

        for _ in range(100):
            height = int(rng.integers(1, 16))
            width = int(rng.integers(1, 16))
            label_map = rng.choice(
                np.array([-7, 0, 3, 10, 25], dtype=np.int32),
                size=(height, width),
            )
            threshold = int(rng.integers(1, max(2, height * width + 2)))
            _assert_matches_oracle(self, label_map, threshold)


@unittest.skipUnless(paintober_native, "paintober_native extension is not installed")
class NativeMergeSmallRegionsTests(unittest.TestCase):
    def test_native_matches_oracle_for_contract_fixtures(self):
        fixtures = (
            (np.array([[4, 2, 3], [0, 4, 1], [3, 2, 2]], dtype=np.int32), 2),
            (np.array([[3, 1, 0], [4, 2, 4], [4, 2, 4]], dtype=np.int32), 2),
            (np.array([[2, 2, 1, 3, 3], [2, 2, 2, 3, 3]], dtype=np.int32), 3),
        )

        for label_map, threshold in fixtures:
            original = label_map.copy()
            actual = paintober_native.merge_small_regions(label_map, threshold)
            expected = reference_merge_small_regions(label_map, threshold)
            self.assertTrue(np.array_equal(actual, expected))
            self.assertEqual(actual.shape, label_map.shape)
            self.assertEqual(actual.dtype, label_map.dtype)
            self.assertTrue(np.array_equal(label_map, original))

    def test_native_matches_oracle_for_random_integer_dtypes(self):
        rng = np.random.default_rng(20260902)
        dtypes = (
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
        )

        for dtype in dtypes:
            for _ in range(100):
                height = int(rng.integers(0, 16))
                width = int(rng.integers(0, 16))
                source = np.array([-7, 0, 3, 10, 25], dtype=np.int64)
                label_map = rng.choice(source, size=(height, width)).astype(dtype)
                threshold = int(rng.integers(-2, max(3, height * width + 3)))
                original = label_map.copy()

                actual = paintober_native.merge_small_regions(label_map, threshold)
                expected = reference_merge_small_regions(label_map, threshold)

                with self.subTest(dtype=dtype, shape=label_map.shape, threshold=threshold):
                    self.assertTrue(np.array_equal(actual, expected))
                    self.assertEqual(actual.shape, label_map.shape)
                    self.assertEqual(actual.dtype, label_map.dtype)
                    self.assertTrue(np.array_equal(label_map, original))

    def test_native_rejects_invalid_inputs(self):
        invalid_inputs = (
            np.zeros(3, dtype=np.int32),
            np.zeros((2, 2), dtype=np.float32),
            np.zeros((2, 2), dtype=bool),
        )

        for label_map in invalid_inputs:
            with self.subTest(dtype=label_map.dtype, ndim=label_map.ndim):
                with self.assertRaises((TypeError, ValueError)):
                    paintober_native.merge_small_regions(label_map, 2)

    def test_native_repeated_calls_are_deterministic(self):
        label_map = np.array(
            [[4, 2, 3], [0, 4, 1], [3, 2, 2]],
            dtype=np.int32,
        )

        first = paintober_native.merge_small_regions(label_map, 2)
        second = paintober_native.merge_small_regions(label_map, 2)

        self.assertTrue(np.array_equal(first, second))


class MergeBackendDispatchTests(unittest.TestCase):
    def setUp(self):
        self.label_map = np.array(
            [[4, 2, 3], [0, 4, 1], [3, 2, 2]],
            dtype=np.int32,
        )

    def test_python_backend_uses_python_implementation(self):
        with mock.patch.dict("os.environ", {"PAINTOBER_MERGE_BACKEND": "python"}):
            with mock.patch(
                "pipeline.processor._merge_small_regions_python",
                wraps=_merge_small_regions_python,
            ) as python_merge:
                actual = merge_small_regions(self.label_map, 2)

        python_merge.assert_called_once()
        self.assertTrue(
            np.array_equal(actual, reference_merge_small_regions(self.label_map, 2))
        )

    def test_invalid_backend_is_rejected(self):
        with mock.patch.dict("os.environ", {"PAINTOBER_MERGE_BACKEND": "invalid"}):
            with self.assertRaises(ValueError):
                merge_small_regions(self.label_map, 2)

    def test_native_backend_requires_installed_extension(self):
        with mock.patch.dict("os.environ", {"PAINTOBER_MERGE_BACKEND": "native"}):
            with mock.patch.dict("sys.modules", {"paintober_native": None}):
                with self.assertRaises(RuntimeError):
                    merge_small_regions(self.label_map, 2)



def _benchmark_fixtures() -> Tuple[Tuple[str, np.ndarray, int], ...]:
    fixtures = []

    for name, shape in (("small", (80, 80)), ("medium", (240, 240)), ("large", (600, 600))):
        label_map = np.zeros(shape, dtype=np.int32)
        for y in range(2, shape[0] - 2, 12):
            for x in range(2, shape[1] - 2, 12):
                label_map[y : y + 3, x : x + 3] = 1
        fixtures.append((f"sparse_islands_{name}", label_map, 20))

    fragmented = np.indices((240, 240)).sum(axis=0) % 8
    fixtures.append(("fragmented", fragmented.astype(np.int32), 20))

    checkerboard = np.indices((240, 240)).sum(axis=0) % 2
    fixtures.append(("checkerboard", checkerboard.astype(np.int32), 20))

    return tuple(fixtures)


def _time_calls(function, label_map: np.ndarray, threshold: int, repeats: int) -> float:
    for _ in range(2):
        function(label_map, threshold)

    elapsed = []
    for _ in range(repeats):
        started = time.perf_counter()
        function(label_map, threshold)
        elapsed.append(time.perf_counter() - started)

    return float(np.median(elapsed))


def run_benchmark() -> None:
    """Run the isolated benchmark with ``python -m ...``."""
    import sys

    print(f"Python executable: {sys.executable}")
    print("All benchmark outputs are checked against the frozen oracle first.")

    for name, label_map, threshold in _benchmark_fixtures():
        expected = reference_merge_small_regions(label_map, threshold)
        actual = merge_small_regions(label_map, threshold)
        if not np.array_equal(actual, expected):
            raise AssertionError(f"Correctness mismatch in fixture {name!r}")

        repeats = 3 if label_map.size >= 240 * 240 else 10
        reference_time = _time_calls(
            reference_merge_small_regions, label_map, threshold, repeats
        )
        optimized_time = _time_calls(merge_small_regions, label_map, threshold, repeats)
        speedup = reference_time / optimized_time if optimized_time else float("inf")

        print(
            f"{name}: shape={label_map.shape} labels={len(np.unique(label_map))} "
            f"threshold={threshold} repeats={repeats} "
            f"reference_median={reference_time:.6f}s "
            f"optimized_median={optimized_time:.6f}s "
            f"speedup={speedup:.2f}x"
        )


if __name__ == "__main__":
    run_benchmark()
