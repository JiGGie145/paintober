# Prompt — Add User Paint Palette Mapping

Extend the existing Paint-By-Numbers notebook with a new feature:

Users can provide their own paint palette, and the pipeline must map the generated colors to the closest colors in the user palette.

This simulates real-world paint kits where users only own a fixed set of paints.

---

# High Level Goal

We already generate:

* quantized image
* automatically generated palette (k-means colors)

We now want to:

1. Accept a **user paint palette**
2. Replace generated colors with the **closest available paint colors**
3. Rebuild the quantized image using the mapped palette
4. Update outline numbering and palette sheet

---

# User Palette Input Options

The notebook must support 3 ways of providing palette:

### Option 1 — Python list of RGB tuples

```python
USER_PALETTE = [
    (255, 255, 255),
    (0, 0, 0),
    (220, 20, 60),
    (65, 105, 225),
    (255, 215, 0),
]
```

### Option 2 — HEX list

```python
USER_PALETTE_HEX = ["#FFFFFF", "#000000", "#DC143C"]
```

### Option 3 — Palette image

User uploads an image containing color swatches.

Implement:

```python
def extract_palette_from_image(path: str) -> List[Tuple[int,int,int]]
```

Method:

* Resize image small (200px)
* Run k-means to extract ~12 dominant colors
* Return RGB list

---

# Color Matching Algorithm (CORE TASK)

We must map each generated color → nearest user color.

Create function:

```python
def map_palette_to_user_palette(
    generated_palette: np.ndarray,
    user_palette: List[Tuple[int,int,int]]
) -> Dict[int, Tuple[int,int,int]]
```

This function returns a mapping from generated color index → user color.

---

# IMPORTANT — Use Perceptual Color Distance

Do NOT use Euclidean RGB distance.

Convert colors to **LAB color space** and compute Delta-E distance.

Implement helpers:

```python
def rgb_to_lab(color_rgb: Tuple[int,int,int]) -> np.ndarray
def delta_e(c1_lab, c2_lab) -> float
```

Use OpenCV conversion:

* cv2.COLOR_RGB2LAB

For each generated color:

* compute distance to every user color
* choose smallest distance

Explain in markdown why LAB distance is better than RGB.

---

# Remap the Quantized Image

Create:

```python
def remap_image_to_user_palette(
    quantized_img: np.ndarray,
    palette: np.ndarray,
    mapping: Dict[int, Tuple[int,int,int]]
) -> np.ndarray
```

Steps:

1. For each pixel, find its palette index
2. Replace with mapped user color
3. Return new remapped image

Display:

* original quantized image
* remapped image side-by-side

---

# Handle Missing Colors (IMPORTANT)

User palette may be too small.

Add optional parameter:

```python
ALLOW_COLOR_REUSE = True
```

Behavior:

* Multiple generated colors may map to same user color.
* This is acceptable and must be documented.

Add markdown explaining this.

---

# Update Downstream Pipeline

After remapping, all later steps must use the **remapped image**:

* mask creation
* contour extraction
* outline drawing
* palette page generation

The palette page must now show **only user colors actually used**.

---

# Palette Usage Summary

Create function:

```python
def compute_palette_usage(remapped_img, user_palette)
```

Return:

* how many regions per color
* percentage coverage

Display bar chart using matplotlib.

---

# Notebook Demo Section

Add demo workflow:

1. Run pipeline normally (auto palette)
2. Run pipeline with user palette
3. Show visual comparison

---

# Expected Outcome

When user supplies a small paint set (e.g. 12 acrylic paints):

The generated paint-by-numbers template must use only those colors.

---

This feature will massively increase real-world usability and conversion for event hosts.
