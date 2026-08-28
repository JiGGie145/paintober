"""Isolated correctness and benchmark exercise for merge_small_regions.

This module intentionally exercises only label-map inputs and outputs. It does
not call Django, run_pipeline, load images, or touch the filesystem.
"""

from __future__ import annotations

import time
import unittest
from typing import Dict, Tuple

import numpy as np
from scipy import ndimage

from .processor import merge_small_regions


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
