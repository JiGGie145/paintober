use std::collections::{BTreeSet, HashMap, VecDeque};

use ndarray::Array2;
use numpy::{Element, PyArrayDyn, PyArrayMethods, PyUntypedArrayMethods};
use pyo3::prelude::*;
use pyo3::exceptions::{PyTypeError, PyValueError};

/// Build/import smoke-test function for the native extension scaffold.
#[pyfunction]
fn module_name() -> &'static str {
    "paintober_native"
}

const NEIGHBOURS: [(isize, isize); 8] = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
];

fn merge_typed<'py, T>(
    py: Python<'py>,
    input: &Bound<'py, PyArrayDyn<T>>,
    min_region_pixels: i64,
) -> PyResult<Py<PyAny>>
where
    T: Element + Copy + Ord,
{
    let view = input.readonly();
    let shape = view.shape();
    let height = shape[0];
    let width = shape[1];
    let mut result: Vec<T> = view.as_array().iter().copied().collect();
    let labels: BTreeSet<T> = result.iter().copied().collect();
    let mut component_map = vec![0_i64; result.len()];
    let mut visited = vec![false; result.len()];
    let mut component_sizes: Vec<usize> = vec![0];
    let mut component_labels: Vec<T> = Vec::new();
    let mut component_pixels: Vec<Vec<usize>> = vec![Vec::new()];
    let mut next_id = 1_i64;

    for label in labels {
        for start in 0..result.len() {
            if visited[start] || result[start] != label {
                continue;
            }

            let component_id = next_id;
            next_id += 1;
            let mut queue = VecDeque::from([start]);
            let mut pixels = Vec::new();
            visited[start] = true;

            while let Some(index) = queue.pop_front() {
                component_map[index] = component_id;
                pixels.push(index);
                let y = index / width;
                let x = index % width;

                for (dy, dx) in NEIGHBOURS {
                    let neighbour_y = y as isize + dy;
                    let neighbour_x = x as isize + dx;
                    if neighbour_y < 0
                        || neighbour_x < 0
                        || neighbour_y >= height as isize
                        || neighbour_x >= width as isize
                    {
                        continue;
                    }
                    let neighbour = neighbour_y as usize * width + neighbour_x as usize;
                    if !visited[neighbour] && result[neighbour] == label {
                        visited[neighbour] = true;
                        queue.push_back(neighbour);
                    }
                }
            }

            component_sizes.push(pixels.len());
            component_labels.push(label);
            component_pixels.push(pixels);
        }
    }

    let mut small_ids: Vec<i64> = (1..next_id)
        .filter(|id| (component_sizes[*id as usize] as i64) < min_region_pixels)
        .collect();
    small_ids.sort_by_key(|id| (component_sizes[*id as usize], *id));

    for _ in 0..6 {
        if small_ids.is_empty() {
            break;
        }
        let mut changed = false;

        for component_id in &small_ids {
            let id = *component_id as usize;
            let mut votes: HashMap<i64, usize> = HashMap::new();
            let mut border = vec![false; result.len()];

            for index in &component_pixels[id] {
                let y = *index / width;
                let x = *index % width;
                for (dy, dx) in NEIGHBOURS {
                    let neighbour_y = y as isize + dy;
                    let neighbour_x = x as isize + dx;
                    if neighbour_y < 0
                        || neighbour_x < 0
                        || neighbour_y >= height as isize
                        || neighbour_x >= width as isize
                    {
                        continue;
                    }
                    let neighbour = neighbour_y as usize * width + neighbour_x as usize;
                    border[neighbour] = true;
                }
            }

            for (index, is_border) in border.iter().enumerate() {
                if *is_border {
                    let neighbour_id = component_map[index];
                    if neighbour_id != *component_id {
                        *votes.entry(neighbour_id).or_insert(0) += 1;
                    }
                }
            }

            let winner = votes
                .into_iter()
                .max_by(|(left_id, left_count), (right_id, right_count)| {
                    left_count.cmp(right_count).then_with(|| right_id.cmp(left_id))
                })
                .map(|(winner, _)| winner);

            if let Some(winner) = winner {
                let winner_label = component_labels[winner as usize - 1];
                for index in &component_pixels[id] {
                    result[*index] = winner_label;
                }
                changed = true;
            }
        }

        if !changed {
            break;
        }

        // Rebuild the component snapshot and candidate list for the next pass.
        // The current pass intentionally used the snapshot created above.
        component_map.fill(0);
        visited.fill(false);
        component_sizes.truncate(1);
        component_labels.clear();
        component_pixels.truncate(1);
        next_id = 1;

        for label in result.iter().copied().collect::<BTreeSet<_>>() {
            for start in 0..result.len() {
                if visited[start] || result[start] != label {
                    continue;
                }
                let component_id = next_id;
                next_id += 1;
                let mut queue = VecDeque::from([start]);
                let mut pixels = Vec::new();
                visited[start] = true;
                while let Some(index) = queue.pop_front() {
                    component_map[index] = component_id;
                    pixels.push(index);
                    let y = index / width;
                    let x = index % width;
                    for (dy, dx) in NEIGHBOURS {
                        let neighbour_y = y as isize + dy;
                        let neighbour_x = x as isize + dx;
                        if neighbour_y < 0
                            || neighbour_x < 0
                            || neighbour_y >= height as isize
                            || neighbour_x >= width as isize
                        {
                            continue;
                        }
                        let neighbour = neighbour_y as usize * width + neighbour_x as usize;
                        if !visited[neighbour] && result[neighbour] == label {
                            visited[neighbour] = true;
                            queue.push_back(neighbour);
                        }
                    }
                }
                component_sizes.push(pixels.len());
                component_labels.push(label);
                component_pixels.push(pixels);
            }
        }
        small_ids = (1..next_id)
            .filter(|id| (component_sizes[*id as usize] as i64) < min_region_pixels)
            .collect();
        small_ids.sort_by_key(|id| (component_sizes[*id as usize], *id));
    }

    let output = Array2::from_shape_vec((height, width), result)
        .map_err(|_| PyValueError::new_err("could not construct output array"))?
        .into_dyn();
    Ok(PyArrayDyn::from_owned_array(py, output).unbind().into_any())
}

#[pyfunction]
/// Merge small 8-connected regions in a copied 2-D integer NumPy array.
///
/// The implementation preserves the Python pipeline's deterministic component
/// ordering, pass-level snapshots, border-vote tie-breaking, and six-pass
/// limit. Boolean and non-integer arrays are rejected by the public wrapper.
fn merge_small_regions<'py>(
    py: Python<'py>,
    label_map: &Bound<'py, PyAny>,
    min_region_pixels: i64,
) -> PyResult<Py<PyAny>> {
    if !label_map.is_instance_of::<PyArrayDyn<i8>>()
        && !label_map.is_instance_of::<PyArrayDyn<i16>>()
        && !label_map.is_instance_of::<PyArrayDyn<i32>>()
        && !label_map.is_instance_of::<PyArrayDyn<i64>>()
        && !label_map.is_instance_of::<PyArrayDyn<u8>>()
        && !label_map.is_instance_of::<PyArrayDyn<u16>>()
        && !label_map.is_instance_of::<PyArrayDyn<u32>>()
        && !label_map.is_instance_of::<PyArrayDyn<u64>>()
    {
        return Err(PyTypeError::new_err(
            "label_map must be a 2-D NumPy integer array (bool is not supported)",
        ));
    }

    macro_rules! dispatch {
        ($type:ty) => {{
            let array = label_map.downcast::<PyArrayDyn<$type>>()?;
            if array.ndim() != 2 {
                return Err(PyValueError::new_err("label_map must be 2-D"));
            }
            return merge_typed(py, array, min_region_pixels);
        }};
    }

    if label_map.is_instance_of::<PyArrayDyn<i8>>() { dispatch!(i8); }
    if label_map.is_instance_of::<PyArrayDyn<i16>>() { dispatch!(i16); }
    if label_map.is_instance_of::<PyArrayDyn<i32>>() { dispatch!(i32); }
    if label_map.is_instance_of::<PyArrayDyn<i64>>() { dispatch!(i64); }
    if label_map.is_instance_of::<PyArrayDyn<u8>>() { dispatch!(u8); }
    if label_map.is_instance_of::<PyArrayDyn<u16>>() { dispatch!(u16); }
    if label_map.is_instance_of::<PyArrayDyn<u32>>() { dispatch!(u32); }
    dispatch!(u64);
}

#[pymodule]
fn paintober_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(module_name, m)?)?;
    m.add_function(wrap_pyfunction!(merge_small_regions, m)?)?;
    Ok(())
}
