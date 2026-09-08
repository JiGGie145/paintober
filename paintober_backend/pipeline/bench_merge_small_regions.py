"""Benchmark Python and native merge_small_regions implementations.

Run from ``paintober_backend`` with::

    python -m pipeline.bench_merge_small_regions

Every fixture is checked against the frozen oracle before timing. Timings are
informational and depend on the local machine and Python/Rust build.
"""

from __future__ import annotations

import platform
import os
import sys
import time
from typing import Callable, Iterable

import numpy as np

from .processor import _merge_small_regions_python, merge_small_regions
from .test_merge_small_regions import reference_merge_small_regions

try:
    import paintober_native
except ImportError:
    paintober_native = None


Fixture = tuple[str, np.ndarray, int]
MergeFunction = Callable[[np.ndarray, int], np.ndarray]


def _fixtures() -> Iterable[Fixture]:
    for name, shape in (("small", (80, 80)), ("medium", (240, 240)), ("large", (600, 600))):
        label_map = np.zeros(shape, dtype=np.int32)
        for y in range(2, shape[0] - 2, 12):
            for x in range(2, shape[1] - 2, 12):
                label_map[y : y + 3, x : x + 3] = 1
        yield f"sparse_islands_{name}", label_map, 20

    indices = np.indices((240, 240))
    yield "fragmented", (indices.sum(axis=0) % 8).astype(np.int32), 20
    yield "checkerboard", (indices.sum(axis=0) % 2).astype(np.int32), 20

    disconnected = np.zeros((120, 120), dtype=np.int32)
    disconnected[::10, ::10] = 1
    disconnected[5::10, 5::10] = 2
    yield "disconnected_multi_label", disconnected, 20

    yield (
        "multi_pass",
        np.array([[4, 2, 3], [0, 4, 1], [3, 2, 2]], dtype=np.int32),
        2,
    )


def _median_time(function: MergeFunction, label_map: np.ndarray, threshold: int, repeats: int) -> float:
    for _ in range(2):
        function(label_map, threshold)

    timings = []
    for _ in range(repeats):
        started = time.perf_counter()
        function(label_map, threshold)
        timings.append(time.perf_counter() - started)
    return float(np.median(timings))


def _check(function: MergeFunction, label_map: np.ndarray, threshold: int) -> None:
    expected = reference_merge_small_regions(label_map, threshold)
    actual = function(label_map, threshold)
    if not np.array_equal(actual, expected):
        raise AssertionError(
            f"correctness mismatch: shape={label_map.shape}, "
            f"threshold={threshold}, dtype={label_map.dtype}"
        )


def _wrapper_call(label_map: np.ndarray, threshold: int, backend: str) -> np.ndarray:
    previous = os.environ.get("PAINTOBER_MERGE_BACKEND")
    os.environ["PAINTOBER_MERGE_BACKEND"] = backend
    try:
        return merge_small_regions(label_map, threshold)
    finally:
        if previous is None:
            os.environ.pop("PAINTOBER_MERGE_BACKEND", None)
        else:
            os.environ["PAINTOBER_MERGE_BACKEND"] = previous


def main() -> None:
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Native extension available: {paintober_native is not None}")

    for name, label_map, threshold in _fixtures():
        repeats = 3 if label_map.size >= 240 * 240 else 10
        functions: list[tuple[str, MergeFunction]] = [
            ("python", _merge_small_regions_python),
        ]
        if paintober_native is not None:
            functions.append(("native_direct", paintober_native.merge_small_regions))

        for function_name, function in functions:
            _check(function, label_map, threshold)

        python_time = _median_time(_merge_small_regions_python, label_map, threshold, repeats)
        native_time = None
        wrapper_time = None
        if paintober_native is not None:
            native_time = _median_time(
                paintober_native.merge_small_regions, label_map, threshold, repeats
            )
            _check(
                lambda values, limit: _wrapper_call(values, limit, "native"),
                label_map,
                threshold,
            )
            wrapper_time = _median_time(
                lambda values, limit: _wrapper_call(values, limit, "native"),
                label_map,
                threshold,
                repeats,
            )

        native_text = f" native_direct={native_time:.6f}s" if native_time is not None else ""
        speedup_text = (
            f" speedup={python_time / native_time:.2f}x" if native_time else ""
        )
        print(
            f"{name}: shape={label_map.shape} labels={len(np.unique(label_map))} "
            f"threshold={threshold} repeats={repeats} "
            f"python={python_time:.6f}s{native_text}"
            f" wrapper_python={wrapper_time:.6f}s{speedup_text}"
        )


if __name__ == "__main__":
    main()
