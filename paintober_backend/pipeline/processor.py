"""
Paintober pipeline — standalone processor module.

Extracted from paintober_pipeline.ipynb. All Jupyter/display calls removed.
Entry point: run_pipeline(image_path, output_dir, params) -> dict
"""

import io
import logging
import math
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — no display required
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

logger = logging.getLogger("pipeline")

# ── Defaults (mirror notebook cell 3) ─────────────────────────────────────
DEFAULTS: Dict[str, Any] = {
    "k_colors": 12,
    "min_region_area": 200,
    "contour_epsilon": 0.002,
    "line_thickness": 1,
    "apply_gaussian": True,
    "min_label_spacing": 12,
    # BYOP
    "use_user_palette": False,
    "user_palette_mode": "hex",       # "rgb" | "hex"
    "user_palette_rgb": None,         # list of (R,G,B) tuples
    "user_palette_hex": None,         # list of hex strings
    "allow_color_reuse": True,
}

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}


# ─────────────────────────────────────────────────────────────────────────────
# Input helpers
# ─────────────────────────────────────────────────────────────────────────────

def normalise_upload(src: Path, dest: Path) -> None:
    """Convert uploaded file to PNG and write to dest.

    Accepts JPEG, PNG, WEBP. Raises ValueError for unsupported formats.
    """
    suffix = src.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported image format '{suffix}'. "
            f"Accepted: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )
    from PIL import Image
    with Image.open(src) as img:
        img = img.convert("RGB")
        dest.parent.mkdir(parents=True, exist_ok=True)
        img.save(dest, format="PNG")


# ─────────────────────────────────────────────────────────────────────────────
# Core pipeline helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_image(path: str) -> np.ndarray:
    bgr = cv2.imread(path)
    if bgr is None:
        raise FileNotFoundError(f"Could not load image: {path!r}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    if w > 1500:
        scale = 1500 / w
        rgb = cv2.resize(rgb, (1500, int(h * scale)), interpolation=cv2.INTER_AREA)
    return rgb


def preprocess_image(img: np.ndarray, apply_gaussian: bool = False) -> np.ndarray:
    smoothed = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    if apply_gaussian:
        smoothed = cv2.GaussianBlur(smoothed, (5, 5), 0)
    return smoothed


def quantize_colors(img: np.ndarray, k: int = 12) -> Tuple[np.ndarray, np.ndarray]:
    h, w = img.shape[:2]
    pixels = img.reshape(-1, 3).astype(np.float32)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    palette = kmeans.cluster_centers_.astype(np.uint8)
    quantized_img = palette[kmeans.labels_].reshape(h, w, 3)
    return quantized_img, palette


def create_color_masks(
    quantized_img: np.ndarray, palette: np.ndarray
) -> List[np.ndarray]:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    masks: List[np.ndarray] = []
    for color in palette:
        mask = np.all(quantized_img == color, axis=2).astype(np.uint8) * 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        masks.append(mask)
    return masks


def extract_contours(
    masks: List[np.ndarray], min_area: int = 200
) -> List[List[np.ndarray]]:
    contours_by_color: List[List[np.ndarray]] = []
    for mask in masks:
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered = [c for c in cnts if cv2.contourArea(c) >= min_area]
        contours_by_color.append(filtered)
    return contours_by_color


def simplify_contours(
    contours_by_color: List[List[np.ndarray]],
    epsilon_ratio: float = 0.002,
) -> List[List[np.ndarray]]:
    simplified: List[List[np.ndarray]] = []
    for contours in contours_by_color:
        simp_group: List[np.ndarray] = []
        for c in contours:
            eps = epsilon_ratio * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, eps, True)
            simp_group.append(approx)
        simplified.append(simp_group)
    return simplified


def _find_label_point(
    contour: np.ndarray, image_shape: Tuple[int, int]
) -> Tuple[int, int]:
    h, w = image_shape
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    _, _, _, max_loc = cv2.minMaxLoc(dist)
    return max_loc  # (x, y)


def draw_outline(
    contours_by_color: List[List[np.ndarray]],
    image_shape: Tuple[int, int],
    thickness: int = 2,
    min_label_area: int = 200,
    min_label_spacing: int = 12,
) -> np.ndarray:
    h, w = image_shape
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 255

    for contours in contours_by_color:
        cv2.drawContours(canvas, contours, -1, (0, 0, 0), thickness)

    placed: List[Tuple[int, int]] = []

    for color_idx, contours in enumerate(contours_by_color):
        label = str(color_idx + 1)
        for c in contours:
            area = cv2.contourArea(c)
            if area < min_label_area:
                continue
            lx, ly = _find_label_point(c, (h, w))
            too_close = any(
                math.hypot(lx - px, ly - py) < min_label_spacing
                for px, py in placed
            )
            if too_close:
                continue
            font_scale = max(0.25, min(0.55, math.sqrt(area) / 200))
            cv2.putText(
                canvas, label, (lx, ly),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                (60, 60, 60), 1, cv2.LINE_AA,
            )
            placed.append((lx, ly))

    return canvas


def create_palette_image(palette: np.ndarray) -> np.ndarray:
    k = len(palette)
    fig, axes = plt.subplots(1, k, figsize=(max(k * 1.5, 6), 2.5))
    if k == 1:
        axes = [axes]
    for i, (ax, color) in enumerate(zip(axes, palette)):
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        ax.set_facecolor(tuple(c / 255 for c in (r, g, b)))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"#{i + 1}", fontsize=9, pad=3)
        luminance = r * 0.299 + g * 0.587 + b * 0.114
        text_color = "white" if luminance < 128 else "black"
        ax.text(
            0.5, 0.62,
            f"RGB\n({r},{g},{b})",
            ha="center", va="center",
            fontsize=6.5, color=text_color,
            transform=ax.transAxes,
        )
        ax.text(
            0.5, 0.22,
            f"Mix approx\nRGB({r},{g},{b})",
            ha="center", va="center",
            fontsize=5.5, color=text_color,
            transform=ax.transAxes,
        )
    fig.suptitle("Color Palette", fontsize=11, y=1.02)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    arr = np.frombuffer(buf.read(), dtype=np.uint8)
    palette_img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    palette_img = cv2.cvtColor(palette_img, cv2.COLOR_BGR2RGB)
    buf.close()
    return palette_img


def export_assets(
    quantized_img: np.ndarray,
    outline: np.ndarray,
    palette_img: np.ndarray,
    output_dir: Path,
) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    assets = {
        "quantized_color.png": cv2.cvtColor(quantized_img, cv2.COLOR_RGB2BGR),
        "outline.png": cv2.cvtColor(outline, cv2.COLOR_RGB2BGR),
        "palette.png": cv2.cvtColor(palette_img, cv2.COLOR_RGB2BGR),
    }
    paths: Dict[str, Path] = {}
    for filename, img_bgr in assets.items():
        out_path = output_dir / filename
        cv2.imwrite(str(out_path), img_bgr)
        paths[filename] = out_path
        logger.debug("Saved asset: %s", out_path)
    return paths


def create_zip(output_dir: Path, asset_paths: Dict[str, Path]) -> Path:
    zip_path = output_dir / "results.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, path in asset_paths.items():
            zf.write(path, arcname=filename)
    logger.debug("Created zip: %s", zip_path)
    return zip_path


# ─────────────────────────────────────────────────────────────────────────────
# BYOP helpers
# ─────────────────────────────────────────────────────────────────────────────

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_lab(color_rgb: Tuple[int, int, int]) -> np.ndarray:
    pixel = np.uint8([[[color_rgb[0], color_rgb[1], color_rgb[2]]]])
    lab = cv2.cvtColor(pixel, cv2.COLOR_RGB2LAB)
    return lab[0, 0].astype(np.float32)


def delta_e(c1_lab: np.ndarray, c2_lab: np.ndarray) -> float:
    return float(np.linalg.norm(c1_lab.astype(float) - c2_lab.astype(float)))


def map_palette_to_user_palette(
    generated_palette: np.ndarray,
    user_palette: List[Tuple[int, int, int]],
    allow_reuse: bool = True,
) -> dict:
    gen_labs = [rgb_to_lab(tuple(int(v) for v in c)) for c in generated_palette]
    user_labs = [rgb_to_lab(c) for c in user_palette]

    if allow_reuse:
        mapping: dict = {}
        for i, g_lab in enumerate(gen_labs):
            dists = [delta_e(g_lab, u_lab) for u_lab in user_labs]
            best = int(np.argmin(dists))
            mapping[i] = user_palette[best]
        return mapping

    all_pairs = sorted(
        [
            (i, j, delta_e(gen_labs[i], user_labs[j]))
            for i in range(len(generated_palette))
            for j in range(len(user_palette))
        ],
        key=lambda x: x[2],
    )
    claimed_gen: set = set()
    claimed_user: set = set()
    mapping = {}
    for i, j, _ in all_pairs:
        if i not in claimed_gen and j not in claimed_user:
            mapping[i] = user_palette[j]
            claimed_gen.add(i)
            claimed_user.add(j)
    for i in range(len(generated_palette)):
        if i not in mapping:
            dists = [delta_e(gen_labs[i], u_lab) for u_lab in user_labs]
            mapping[i] = user_palette[int(np.argmin(dists))]
    return mapping


def remap_image_to_user_palette(
    quantized_img: np.ndarray,
    palette: np.ndarray,
    mapping: dict,
) -> np.ndarray:
    result = quantized_img.copy()
    for i, color in enumerate(palette):
        mask = np.all(quantized_img == color, axis=2)
        result[mask] = mapping[i]
    return result


def _parse_user_palette(params: Dict[str, Any]) -> Optional[List[Tuple[int, int, int]]]:
    mode = params.get("user_palette_mode", "hex")
    if mode == "rgb":
        raw = params.get("user_palette_rgb") or []
        return [tuple(int(v) for v in c) for c in raw]
    elif mode == "hex":
        raw = params.get("user_palette_hex") or []
        return [hex_to_rgb(h) for h in raw]
    else:
        raise ValueError(f"Unsupported user_palette_mode: {mode!r}. Use 'rgb' or 'hex'.")


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline(image_path: str, output_dir: Path, params: Dict[str, Any]) -> Dict[str, str]:
    """Run the full paint-by-numbers pipeline.

    Parameters
    ----------
    image_path : str
        Absolute path to the input image (PNG expected after normalise_upload).
    output_dir : Path
        Directory to write output files into (created if absent).
    params : dict
        Pipeline parameters. Missing keys fall back to DEFAULTS.

    Returns
    -------
    dict
        Mapping of output keys to relative paths (relative to MEDIA_ROOT):
        'output_outline', 'output_color', 'output_palette', 'output_zip'
    """
    p = {**DEFAULTS, **params}

    logger.info("Pipeline start | image=%s k=%s", image_path, p["k_colors"])

    # Stage 1 — Load
    img = load_image(image_path)

    # Stage 2 — Preprocess
    preprocessed = preprocess_image(img, apply_gaussian=p["apply_gaussian"])

    # Stage 3a — Quantize
    quantized, palette = quantize_colors(preprocessed, k=p["k_colors"])

    # Stage 3b — BYOP (optional)
    if p["use_user_palette"]:
        user_palette_rgb = _parse_user_palette(p)
        if user_palette_rgb:
            mapping = map_palette_to_user_palette(
                palette, user_palette_rgb, allow_reuse=p["allow_color_reuse"]
            )
            quantized = remap_image_to_user_palette(quantized, palette, mapping)
            palette = np.unique(quantized.reshape(-1, 3), axis=0).astype(np.uint8)
            logger.debug("BYOP remapping done, unique colours: %d", len(palette))

    # Stage 4 — Masks
    masks = create_color_masks(quantized, palette)

    # Stage 5 — Contours
    contours_by_color = extract_contours(masks, min_area=p["min_region_area"])

    # Stage 6 — Simplify
    simplified = simplify_contours(contours_by_color, epsilon_ratio=p["contour_epsilon"])

    # Stage 7 — Outline
    h_img, w_img = quantized.shape[:2]
    outline = draw_outline(
        simplified,
        (h_img, w_img),
        thickness=p["line_thickness"],
        min_label_area=p["min_region_area"],
        min_label_spacing=p["min_label_spacing"],
    )

    # Stage 8 — Palette image
    palette_img = create_palette_image(palette)

    # Stage 9 — Export
    asset_paths = export_assets(quantized, outline, palette_img, output_dir)
    zip_path = create_zip(output_dir, asset_paths)

    logger.info("Pipeline complete | output_dir=%s", output_dir)

    return {
        "output_outline": str(asset_paths["outline.png"]),
        "output_color": str(asset_paths["quantized_color.png"]),
        "output_palette": str(asset_paths["palette.png"]),
        "output_zip": str(zip_path),
    }
