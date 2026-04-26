# Prompt — Paint-By-Numbers Pipeline Notebook

Create a **well-structured Python Jupyter notebook** that implements a full image-to-paint-by-numbers pipeline using OpenCV, NumPy, scikit-learn and matplotlib.

The notebook must be clean, educational, and modular so it can later be converted into a reusable Python package.

The goal is to take an input photo and output:

1. a simplified paint-by-numbers color image
2. a numbered outline image (black lines + numbers inside regions)
3. a color palette with paint mixing info

---

# High Level Pipeline

Implement the following pipeline step-by-step with markdown explanations and visualization after every stage:

1. Load image
2. Preprocess / smooth image
3. Reduce color count (color quantization)
4. Convert quantized image into regions
5. Extract contours for each region
6. Simplify shapes (reduce noise)
7. Generate numbered outline image
8. Generate color palette
9. Export final assets

---

# Notebook Requirements

The notebook must be divided into sections:

* Imports
* Helper functions
* Pipeline steps (each with plots)
* Final export section

Use matplotlib to display intermediate results.

---

# Step 1 — Load Image

Create a function:

```python
def load_image(path: str) -> np.ndarray:
```

Requirements:

* Load using OpenCV
* Convert BGR → RGB
* Resize if width > 1500px (keep aspect ratio)
* Display original image

---

# Step 2 — Pre-processing

Goal: remove noise while keeping edges.

Implement:

```python
def preprocess_image(img: np.ndarray) -> np.ndarray:
```

Must include:

* bilateral filter (edge preserving)
* optional Gaussian blur
* show before/after comparison

Explain why bilateral filtering is used for edge-preserving smoothing.

---

# Step 3 — Color Quantization (CORE STEP)

Use **K-Means clustering** to reduce colors.

Color quantization reduces the number of colors by clustering pixels into K clusters and replacing them with centroid colors. ([GeeksforGeeks][1])

Create:

```python
def quantize_colors(img: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
```

Requirements:

* Reshape image to (num_pixels, 3)
* Use sklearn KMeans
* Return:

  * quantized image
  * array of cluster centers (palette)
* Show comparison original vs quantized

Allow adjustable `k` (default = 12).

---

# Step 4 — Convert to Regions

We want a labeled mask per color cluster.

Create:

```python
def create_color_masks(quantized_img, palette) -> List[np.ndarray]:
```

For each palette color:

* create binary mask using color matching
* clean mask using morphological operations:

  * opening
  * closing

Visualize masks grid.

---

# Step 5 — Find Contours per Region

Contours represent paintable areas.

Create:

```python
def extract_contours(masks: List[np.ndarray]) -> List[List[np.ndarray]]:
```

Requirements:

* use cv2.findContours
* filter small areas (noise removal)
* minimum area threshold parameter

Visualize contours overlayed on image.

---

# Step 6 — Simplify Contours (VERY IMPORTANT)

Paint-by-numbers requires smooth simple shapes.

Implement polygon simplification:

```python
def simplify_contours(contours, epsilon_ratio=0.002):
```

Use:

* cv2.approxPolyDP

Explain epsilon and why simplification is needed.

Show before vs after comparison.

---

# Step 7 — Create Outline Image

Generate a white canvas and draw:

* Black contour lines
* Region numbers inside each shape

Functions:

```python
def draw_outline(contours_by_color, image_shape) -> np.ndarray
```

Requirements:

* white background
* black contour lines
* line thickness adjustable
* place numbers using centroid of contour
* use cv2.putText
* skip tiny contours

Display result.

---

# Step 8 — Generate Color Palette

Create palette visualization:

```python
def create_palette_image(palette) -> np.ndarray
```

Requirements:

* show color swatches
* number each color
* display RGB values

Bonus:
Add placeholder paint mixing text:
"Mix approx RGB(r,g,b)"

---

# Step 9 — Export Assets

Save outputs to `/outputs/` folder:

* quantized_color.png
* outline.png
* palette.png

Use cv2.imwrite (convert RGB→BGR).

---

# Parameters Cell

Create a top cell with tweakable parameters:

```python
K_COLORS = 12
MIN_REGION_AREA = 200
CONTOUR_EPSILON = 0.002
LINE_THICKNESS = 2
```

---

# Quality Requirements

The notebook must:

* run end-to-end with one “Run All”
* include plots after each step
* be clean and production-ready
* avoid global variables
* use type hints everywhere
* include docstrings for every function

---

# Optional Bonus Section (if time allows)

Add sliders using ipywidgets:

* number of colors
* contour simplification
* minimum area

---

# Expected Outcome

Running the notebook with a portrait or landscape photo should produce a recognizable paint-by-numbers template.
