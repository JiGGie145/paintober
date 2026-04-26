# Plan: Paint-By-Numbers Pipeline Notebook

## TL;DR
Create `v0.1/paintober_pipeline.ipynb` — a single Jupyter notebook implementing a 9-step image-to-paint-by-numbers pipeline using OpenCV, NumPy, sklearn, and matplotlib. Clean, modular, runs end-to-end with "Run All".

---

## Decisions
- Location: `v0.1/paintober_pipeline.ipynb`
- Sample image: user provides path; notebook uses `IMAGE_PATH` placeholder in parameters cell
- ipywidgets bonus section: included at the end
- Outputs folder: `../outputs/` relative to notebook (project root level)
- `quantize_colors` returns a 2-tuple `(quantized_img, palette)` per spec; masks use exact color matching `np.all(img == palette[i], axis=2)` — safe because palette values are uint8 and quantized pixels are reconstructed from those exact values
- No global variables; all state flows through function return values and pipeline cell variables

---

## Notebook Cell Layout (in order)

### Preamble
1. **Markdown cell**: Title, description, pipeline overview diagram (text-based)
2. **Code cell — Imports**: `numpy as np`, `cv2`, `matplotlib.pyplot as plt`, `sklearn.cluster.KMeans`, `typing` (List, Tuple), `os`, `pathlib.Path`, `ipywidgets` (imported at bottom with try/except for bonus section)
3. **Code cell — Parameters**: `IMAGE_PATH`, `K_COLORS=12`, `MIN_REGION_AREA=200`, `CONTOUR_EPSILON=0.002`, `LINE_THICKNESS=2`, `OUTPUT_DIR = Path("../outputs")`

### Helper Functions (one code cell, all docstrings + type hints)
4. **Code cell**: All 8 pipeline functions defined here (see function specs below)

### Pipeline Steps (alternating markdown + code)
5. Step 1 markdown + code cell (load + display)
6. Step 2 markdown + code cell (preprocess + before/after)
7. Step 3 markdown + code cell (quantize + before/after)
8. Step 4 markdown + code cell (masks grid)
9. Step 5 markdown + code cell (contours overlaid on image)
10. Step 6 markdown + code cell (simplification before/after)
11. Step 7 markdown + code cell (outline image)
12. Step 8 markdown + code cell (palette swatches)

### Export
13. **Markdown + code**: Step 9 — mkdir outputs, imwrite with BGR conversion, print paths

### Bonus
14. **Markdown cell**: ipywidgets section header
15. **Code cell**: interactive widgets using `interact` or `interactive_output`

---

## Function Specifications

### `load_image(path: str) -> np.ndarray`
- `cv2.imread` → BGR→RGB via `cv2.cvtColor`
- Resize if width > 1500: `scale = 1500/w`, `cv2.resize` with `INTER_AREA`
- Display with `plt.imshow`; return RGB array

### `preprocess_image(img: np.ndarray) -> np.ndarray`
- `cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)`
- Optional Gaussian: `cv2.GaussianBlur(..., (5,5), 0)` — toggle via parameter
- Side-by-side matplotlib comparison; markdown explains bilateral preserves edges

### `quantize_colors(img: np.ndarray, k: int = 12) -> Tuple[np.ndarray, np.ndarray]`
- Reshape to `(-1, 3)` as `float32`
- `KMeans(n_clusters=k, random_state=42, n_init=10).fit(pixels)`
- `centers = kmeans.cluster_centers_.astype(np.uint8)` — palette
- Reconstruct: `centers[kmeans.labels_].reshape(h, w, 3)` — quantized
- Side-by-side original vs quantized; return `(quantized, palette)`

### `create_color_masks(quantized_img: np.ndarray, palette: np.ndarray) -> List[np.ndarray]`
- For each `color in palette`: `mask = np.all(quantized_img == color, axis=2).astype(np.uint8) * 255`
- Morphological opening then closing with 3×3 elliptical kernel (denoise, fill holes)
- Grid visualization with `plt.subplots` (rows × cols to fit K masks)

### `extract_contours(masks: List[np.ndarray], min_area: int = 200) -> List[List[np.ndarray]]`
- For each mask: `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`
- Filter: keep only contours with `cv2.contourArea(c) >= min_area`
- Visualize: draw all contours on copy of original, each color with distinct color
- Return `List[List[np.ndarray]]`

### `simplify_contours(contours_by_color: List[List[np.ndarray]], epsilon_ratio: float = 0.002) -> List[List[np.ndarray]]`
- For each contour: `eps = epsilon_ratio * cv2.arcLength(c, True)`, then `cv2.approxPolyDP(c, eps, True)`
- Markdown: explain epsilon as fraction of perimeter (adaptive), why simplification reduces point count for paint-friendliness
- Before/after: draw unsimplified vs simplified on side-by-side canvas; show point count reduction

### `draw_outline(contours_by_color: List[List[np.ndarray]], image_shape: Tuple, thickness: int = 2) -> np.ndarray`
- White canvas: `np.ones((h, w, 3), dtype=np.uint8) * 255`
- For color_index, contours_for_color in enumerate(contours_by_color):
  - `cv2.drawContours(canvas, contours_for_color, -1, (0,0,0), thickness)`
  - For each contour with area > MIN_REGION_AREA:
    - `M = cv2.moments(c)` → centroid `cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])`
    - Guard: skip if `M['m00'] == 0`
    - `cv2.putText(canvas, str(color_index+1), (cx,cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (50,50,50), 1)`
- Return outline image; display with plt.imshow

### `create_palette_image(palette: np.ndarray) -> np.ndarray`
- `fig, axes = plt.subplots(1, k, figsize=(k*1.5, 2))`
- Each ax: filled color patch, number label, "RGB(r,g,b)" text, "Mix approx RGB(r,g,b)" text
- Convert fig to numpy: save to BytesIO, reload, or use `fig.canvas.buffer_rgba()`
- Return as numpy image; also display inline

### `export_assets(quantized_img, outline, palette_img, output_dir)`
- `output_dir.mkdir(parents=True, exist_ok=True)`
- `cv2.imwrite(output_dir/"quantized_color.png", cv2.cvtColor(quantized_img, cv2.COLOR_RGB2BGR))`
- `cv2.imwrite(output_dir/"outline.png", outline)` — outline is already grayscale-ish (white+black), no conversion needed
- `cv2.imwrite(output_dir/"palette.png", cv2.cvtColor(palette_img, cv2.COLOR_RGB2BGR))`
- Print confirmation with file paths

---

## Label Collision Fix Plan

### Root Causes
1. Centroid can land outside a concave/crescent contour → number appears in wrong region
2. Multiple contours (different colors) whose centroids are within a few px of each other → numbers stack
3. Very thin/elongated regions → centroid near/on the contour line itself

### Fix Strategy
1. **Guaranteed-inside point**: Use `cv2.pointPolygonTest` to verify centroid is inside; if not, find the nearest interior point via distance transform on the contour mask
2. **Global label placement grid / occupancy map**: Track placed label positions in a set; before drawing each label, check all prior positions — skip if any is within `MIN_LABEL_SPACING` pixels (configurable, e.g. 12 px)
3. **Label sizing by area**: Scale font size by `sqrt(area)` so tiny regions get tiny (or no) labels

### New parameter
```
MIN_LABEL_SPACING = 12  # minimum pixel distance between any two label centres
```

### Modified function signature
draw_outline gains no new public API — fix is internal, plus new parameter in parameters cell.

---

## ipywidgets Bonus Section
- `@interact(k=(4,24,2), min_area=(50,500,50), epsilon=(0.001,0.01,0.001))`
- Full pipeline re-run inside widget callback
- Note performance: add `%%time` or warning that re-run takes a few seconds

---

## Verification Steps
1. Set IMAGE_PATH to any JPEG, run "Run All" — all cells execute without error
2. Verify `outputs/` folder is created with 3 PNG files
3. Inspect outline.png: should show black lines on white background with numbers 1–K visible
4. Vary K_COLORS (e.g., 6, 12, 24) and re-run — quantized image should show fewer/more colors
5. Check palette_img shows K swatches numbered 1–K with RGB text
6. ipywidgets bonus: drag K slider, verify live re-render

---

## Dependencies (note in a markdown cell)
- `opencv-python`, `numpy`, `scikit-learn`, `matplotlib`, `ipywidgets`
- Install: `pip install opencv-python numpy scikit-learn matplotlib ipywidgets`
