# `merge_small_regions` Optimization and Benchmark Plan

## Objective

Optimize `merge_small_regions` in Python by storing component coordinates during labeling and reusing them later, while preserving a 1-for-1 match with the current implementation.

The exercise is intentionally isolated from Django and the rest of the image-processing pipeline.

## Definition of Equivalence

The optimized implementation must:

- [x] Produce exactly the same output as the current implementation for every test case.
- [x] Match using `np.array_equal`, not approximate numerical comparison.
- [x] Preserve the output shape.
- [x] Preserve the output dtype.
- [x] Leave the input array unchanged.
- [x] Produce deterministic output across repeated calls.
- [x] Preserve the existing public signature:
  ```python
  merge_small_regions(label_map: np.ndarray, min_region_pixels: int) -> np.ndarray
  ```

The current implementation in `paintober_backend/pipeline/processor.py` is the behavioral oracle for this exercise.

---

## Phase 1 — Define the Isolated Contract

- [x] Treat the current `merge_small_regions` implementation as the frozen reference implementation.
- [x] Document that the input is a 2-D integer NumPy label map.
- [x] Document that the function copies the input before modifying it.
- [x] Document that connected components use 8-connectivity.
- [x] Document that only components with size strictly less than `min_region_pixels` are merged.
- [x] Document that components are processed in ascending component-size order.
- [x] Document that the strongest neighboring component is selected by border frequency.
- [x] Document that equal-frequency ties select the smallest component ID.
- [x] Document that the function performs at most six merge passes.
- [x] Keep `min_region_pixels` as a direct function input.
- [x] Exclude `run_pipeline`, `min_region_pct`, palette mapping, image loading, file I/O, and Django setup from the isolated exercise.

---

## Phase 2 — Create the Focused Test Module

Create:

`paintober_backend/pipeline/test_merge_small_regions.py`

- [x] Use the standard-library `unittest` framework, matching the repository's existing test style.
- [x] Import only the function and dependencies needed for the isolated exercise.
- [x] Add a clearly named frozen oracle, such as `reference_merge_small_regions`.
- [x] Ensure the optimized implementation is never compared against a copy of itself.
- [x] Keep benchmark code separate from general Django tests.
- [x] Make the focused test module runnable without initializing Django.

Recommended command from the backend directory:

```text
python -m unittest pipeline.test_merge_small_regions
```

---

## Phase 3 — Add Deterministic Correctness Scenarios

Add explicit expected-output tests for the following cases:

### Basic behavior

- [x] Merge a small island into its surrounding region.
- [x] Leave a component unchanged when its size equals the threshold.
- [x] Leave a component unchanged when its size is greater than the threshold.
- [x] Handle a map containing only one label.
- [x] Handle an already-stable map with no small components.
- [x] Handle a single-pixel map.
- [x] Handle a one-row map.
- [x] Handle a one-column map.

### Connectivity and neighborhood behavior

- [x] Confirm diagonal contact counts as connected under 8-connectivity.
- [x] Confirm a component with no neighboring component is not changed.
- [x] Confirm the most frequent neighboring component wins.
- [x] Confirm equal neighbor counts use the same tie-breaking behavior as the current implementation.
- [x] Confirm neighboring component IDs, rather than only neighboring labels, determine the vote.

### Ordering and convergence behavior

- [x] Test multiple small components processed from smallest to largest.
- [x] Test a case where an earlier merge changes the neighborhood used by a later component.
- [x] Test a case requiring more than one merge pass.
- [x] Test the six-pass maximum behavior.
- [x] Confirm the function stops early when no small components remain.
- [x] Confirm the function stops early when no component can be changed.

### Input and label variations

- [x] Use non-contiguous labels such as `10`, `25`, and `100`.
- [x] Use negative labels where supported by the existing implementation.
- [x] Test multiple NumPy integer dtypes used by the project.
- [x] Confirm output shape is unchanged.
- [x] Confirm output dtype is unchanged.
- [x] Confirm the original input array is unchanged.
- [x] Confirm repeated calls produce identical output.

---

## Phase 4 — Add Differential Tests

- [x] Generate small deterministic label maps using a fixed random seed.
- [x] Generate thresholds covering values below, equal to, and above component sizes.
- [x] Compare the oracle and optimized outputs with `np.array_equal`.
- [x] Include all-one-label maps.
- [x] Include highly fragmented maps.
- [x] Include maps with many disconnected components sharing the same label.
- [x] Include maps with arbitrary label values.
- [x] Include one-dimensional-shaped maps such as `(1, n)` and `(n, 1)`.
- [x] Include repeated calls using the same generated input.
- [x] Make failures print the input map, threshold, oracle output, and optimized output.
- [x] Stop optimization work if any differential case fails.

A mismatch should provide enough information to reproduce the failure without running the entire pipeline.

---

## Phase 5 — Implement Coordinate Storage

Update the implementation while retaining the existing public API.

- [x] Store each connected component's pixel coordinates during component discovery.
- [x] Store each component's size.
- [x] Store each component's original label.
- [x] Preserve component ID allocation order.
- [x] Preserve sorted label iteration order.
- [x] Preserve the row-major component ordering produced by `scipy.ndimage.label`.
- [x] Preserve the shared `component_map` used for neighbor identification.
- [x] Replace repeated full-image component mask creation with direct coordinate access.
- [x] Reassign component pixels using the stored coordinates.
- [x] Preserve the existing pass-level snapshot behavior.
- [x] Discover all components before processing any small component in a pass.
- [x] Preserve ascending component-size processing.
- [x] Preserve strict `< min_region_pixels` behavior.
- [x] Preserve 8-connectivity.
- [x] Preserve neighbor voting behavior.
- [x] Preserve tie-breaking behavior.
- [x] Preserve the six-pass maximum.
- [x] Keep the first implementation limited to NumPy and SciPy.
- [x] Do not add Numba, Rust, Mojo, multiprocessing, or pipeline changes yet.

The initial optimization should change internal storage only, not the algorithm's semantics.

---

## Phase 6 — Isolated Benchmark Design

Create either a benchmark section in the focused module or:

`paintober_backend/pipeline/bench_merge_small_regions.py`

- [x] Benchmark only the oracle and optimized merge functions.
- [x] Use NumPy arrays directly as inputs.
- [x] Exclude Django startup.
- [x] Exclude image loading and image processing.
- [x] Exclude file I/O.
- [x] Exclude fixture generation from timed sections.
- [x] Warm up both implementations before timing.
- [x] Use `time.perf_counter()` or `timeit`.
- [x] Run both implementations in the same process.
- [x] Use identical input arrays for each comparison.
- [x] Verify correctness before timing each fixture.
- [x] Stop or clearly report if the outputs differ.
- [x] Use enough repetitions to reduce timing noise.
- [x] Report median or minimum per-call timing.

### Benchmark fixtures

- [x] Add a small mostly-uniform map with sparse small islands.
- [x] Add a medium mostly-uniform map with sparse small islands.
- [x] Add a large mostly-uniform map with sparse small islands.
- [x] Add a fragmented map with many connected components.
- [x] Add a checkerboard or high-fragmentation stress map.
- [x] Add a map with several labels and disconnected components per label.
- [x] Add a case that requires multiple merge passes.

### Benchmark metadata

For every fixture, report:

- [x] Fixture name.
- [x] Array shape.
- [x] Number of distinct labels.
- [x] `min_region_pixels`.
- [x] Number of repetitions.
- [x] Python executable path.
- [x] Oracle timing.
- [x] Optimized timing.
- [x] Speedup.

Do not hard-code machine-specific performance thresholds during this phase.

---

## Phase 7 — Verification and Acceptance

- [ ] Run the focused correctness suite directly from `paintober_backend`.
- [ ] Confirm all hand-built scenarios pass.
- [ ] Confirm all fixed-seed differential scenarios pass.
- [ ] Confirm input immutability checks pass.
- [ ] Confirm shape and dtype checks pass.
- [ ] Confirm deterministic repeated-call checks pass.
- [ ] Run the isolated benchmark only after correctness passes.
- [ ] Record baseline and optimized timings separately.
- [ ] Compare performance without treating a specific speedup as a correctness requirement.
- [ ] Optionally run the existing processor tests as a regression check.

Optional regression command:

```text
python -m unittest pipeline.tests
```

---

## Mismatch Debugging Procedure

If the optimized implementation differs from the oracle:

- [ ] Record the random seed, if applicable.
- [ ] Record the input label map.
- [ ] Record `min_region_pixels`.
- [ ] Record the oracle output.
- [ ] Record the optimized output.
- [ ] Identify the first differing coordinate.
- [ ] Identify the pass where the difference first appears.
- [ ] Compare component IDs, component sizes, and original labels for that pass.
- [ ] Compare neighbor counts and selected winners.
- [ ] Fix semantics before attempting further optimization.

---

## Future Optimization Stages

These are explicitly deferred until the coordinate-storage rewrite is proven equivalent:

- [ ] Profile the optimized Python implementation.
- [ ] Reduce Python-level per-pixel neighbor loops.
- [ ] Investigate vectorized border counting.
- [ ] Evaluate Numba.
- [ ] Evaluate a direct-buffer Mojo implementation.
- [ ] Evaluate a Rust/PyO3 implementation.
- [ ] Compare conversion overhead when crossing Python/native boundaries.
- [ ] Re-run the same equivalence suite for every later implementation.

## Decisions

- [ ] The current implementation is the authoritative oracle for this optimization phase.
- [ ] “1-for-1 match” means exact `np.array_equal` output.
- [ ] Internal coordinate storage may change; algorithmic behavior may not.
- [ ] The public function signature must remain unchanged.
- [ ] The exercise is isolated from Django and the image-processing pipeline.
- [ ] Benchmark results are measurements, not fixed pass/fail performance claims.
