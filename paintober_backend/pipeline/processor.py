"""
Paintober pipeline — standalone processor module.

Extracted from paintober_pipeline.ipynb. All Jupyter/display calls removed.
Entry point: run_pipeline(image_path, output_dir, params) -> dict
"""

import io
import logging
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — no display required
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.color import delta_e as skimage_delta_e
from skimage.color import rgb2lab
from sklearn.cluster import KMeans

logger = logging.getLogger("pipeline")

# ── Defaults (mirror notebook cell 3) ─────────────────────────────────────
DEFAULTS: Dict[str, Any] = {
    "k_colors": 12,
    "line_thickness": 1,
    "smooth_method": "meanshift",
    "blur_sigma": 1.5,
    "min_region_pct": 0.03,
    "no_merge": False,
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


def preprocess_image(
    img: np.ndarray,
    smooth_method: str = "meanshift",
    blur_sigma: float = 1.5,
) -> np.ndarray:
    if smooth_method not in {"meanshift", "bilateral", "gaussian", "none"}:
        raise ValueError(
            f"Unsupported smooth_method: {smooth_method!r}. "
            "Use 'meanshift', 'bilateral', 'gaussian', or 'none'."
        )
    if blur_sigma < 0:
        raise ValueError("blur_sigma must be non-negative")
    if smooth_method == "none" or blur_sigma == 0:
        return img
    if smooth_method == "gaussian":
        return cv2.GaussianBlur(img, (0, 0), sigmaX=blur_sigma)
    if smooth_method == "meanshift":
        sp = max(2, int(blur_sigma * 7))
        sr = max(20, int(blur_sigma * 40))
        return cv2.pyrMeanShiftFiltering(img, sp=sp, sr=sr)

    sigma = max(10, blur_sigma * 40)
    smoothed = img.copy()
    for _ in range(3):
        smoothed = cv2.bilateralFilter(smoothed, d=9, sigmaColor=sigma, sigmaSpace=sigma)
    return smoothed


def quantize_colors(
    img: np.ndarray,
    k: int = 12,
    blur_sigma: float = 1.5,
    smooth_method: str = "meanshift",
) -> Tuple[np.ndarray, np.ndarray]:
    h, w = img.shape[:2]
    smoothed = preprocess_image(img, smooth_method, blur_sigma)
    pixels = smoothed.reshape(-1, 3).astype(np.float32)
    # Don't ask KMeans for more clusters than unique colors that exist.
    n_unique = len(np.unique(pixels.astype(np.uint8), axis=0))
    k_colours = max(1, min(k, n_unique))
    kmeans = KMeans(n_clusters=k_colours, random_state=42, n_init=4)
    label_map = kmeans.fit_predict(pixels).reshape(h, w)
    palette = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)
    return label_map, palette


def merge_small_regions(
    label_map: np.ndarray,
    min_region_pixels: int,
) -> np.ndarray:
    """Merge small connected components into their strongest neighbours."""
    label_map = label_map.copy()
    structure = np.ones((3, 3), dtype=int)

    for _ in range(6):
        changed = False
        component_map = np.zeros_like(label_map, dtype=np.int64)
        component_sizes: Dict[int, int] = {}
        component_labels: Dict[int, int] = {}
        next_id = 1

        for label in np.unique(label_map):
            components, count = ndimage.label(label_map == label, structure=structure)
            label_mask = label_map == label
            component_map[label_mask] = (components + next_id - 1)[label_mask]
            for component_id in range(1, count + 1):
                global_id = component_id + next_id - 1
                component_sizes[global_id] = int(np.sum(components == component_id))
                component_labels[global_id] = int(label)
            next_id += count

        small_ids = sorted(
            (component_id for component_id, size in component_sizes.items()
             if size < min_region_pixels),
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
            label_map[mask] = component_labels[winner]
            changed = True

        if not changed:
            break

    return label_map


def relabel_contiguous(
    label_map: np.ndarray,
    palette: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    used = np.unique(label_map)
    used_palette = palette[used]
    luminance = (
        0.299 * used_palette[:, 0]
        + 0.587 * used_palette[:, 1]
        + 0.114 * used_palette[:, 2]
    )
    order = np.argsort(luminance)[::-1]
    old_labels = used[order]
    sorted_palette = used_palette[order]
    remap = {int(old): new for new, old in enumerate(old_labels)}
    relabeled = np.vectorize(remap.__getitem__)(label_map).astype(np.int32)
    return relabeled, sorted_palette


def _find_font_path() -> Optional[str]:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    return next((path for path in candidates if Path(path).exists()), None)


def build_outline_image(
    label_map: np.ndarray,
    min_region_for_number: int,
    line_thickness: int = 1,
) -> np.ndarray:
    h, w = label_map.shape
    border = np.zeros((h, w), dtype=bool)
    border[:, :-1] |= label_map[:, :-1] != label_map[:, 1:]
    border[:-1, :] |= label_map[:-1, :] != label_map[1:, :]
    if line_thickness > 1:
        border = cv2.dilate(border.astype(np.uint8), np.ones((line_thickness, line_thickness), np.uint8)) > 0

    canvas = np.full((h, w, 3), 255, dtype=np.uint8)
    canvas[border] = (0, 0, 0)
    image = Image.fromarray(canvas)
    draw = ImageDraw.Draw(image)
    font_path = _find_font_path()
    structure = np.ones((3, 3), dtype=int)

    for label in np.unique(label_map):
        components, count = ndimage.label(label_map == label, structure=structure)
        for component_id in range(1, count + 1):
            component_mask = components == component_id
            area = int(np.sum(component_mask))
            if area < min_region_for_number:
                continue
            distance = ndimage.distance_transform_edt(component_mask)
            cy, cx = np.unravel_index(np.argmax(distance), distance.shape)
            max_distance = distance[cy, cx]
            font_size = int(np.clip(max_distance * 1.1, 8, 28))
            font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
            text = str(int(label) + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_width > max_distance * 2.2 or text_height > max_distance * 2.2:
                continue
            draw.text(
                (cx - text_width / 2 - bbox[0], cy - text_height / 2 - bbox[1]),
                text,
                fill=(0, 0, 0),
                font=font,
            )

    return np.asarray(image)


def build_colored_image(label_map: np.ndarray, palette: np.ndarray) -> np.ndarray:
    return palette[label_map]


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
    pixel = np.asarray(color_rgb, dtype=np.float64).reshape(1, 1, 3) / 255.0
    return rgb2lab(pixel)[0, 0].astype(np.float64)


def rgb_to_lch(color_rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    lab = rgb_to_lab(color_rgb)
    a_channel = float(lab[1])
    b_channel = float(lab[2])
    chroma = float(np.hypot(a_channel, b_channel))
    hue = float(np.degrees(np.arctan2(b_channel, a_channel)) % 360.0)
    return (float(lab[0]), chroma, hue)


def delta_e(c1_lab: np.ndarray, c2_lab: np.ndarray) -> float:
    return float(
        skimage_delta_e.deltaE_ciede2000(
            c1_lab.astype(np.float64), c2_lab.astype(np.float64)
        )
    )


def circular_hue_distance(hue_1: float, hue_2: float) -> float:
    difference = abs(float(hue_1) - float(hue_2)) % 360.0
    return min(difference, 360.0 - difference)


def _palette_match_cost(
    generated_lab: np.ndarray,
    generated_lch: Tuple[float, float, float],
    user_lab: np.ndarray,
    user_lch: Tuple[float, float, float],
    hue_weight: float,
) -> float:
    hue_penalty = 0.0
    if generated_lch[1] >= 10.0 and user_lch[1] >= 10.0:
        hue_penalty = hue_weight * circular_hue_distance(
            generated_lch[2], user_lch[2]
        )
    return delta_e(generated_lab, user_lab) #+ hue_penalty


def map_palette_to_user_palette(
    generated_palette: np.ndarray,
    user_palette: List[Tuple[int, int, int]],
    allow_reuse: bool = True,
    hue_weight: float = 2.0,
) -> dict:
    if hue_weight < 0:
        raise ValueError("hue_weight must be non-negative")

    gen_labs = [rgb_to_lab(tuple(int(v) for v in c)) for c in generated_palette]
    user_labs = [rgb_to_lab(c) for c in user_palette]
    gen_lchs = [rgb_to_lch(tuple(int(v) for v in c)) for c in generated_palette]
    user_lchs = [rgb_to_lch(c) for c in user_palette]

    if allow_reuse:
        mapping: dict = {}
        for i, g_lab in enumerate(gen_labs):
            costs = [
                _palette_match_cost(
                    g_lab, gen_lchs[i], user_lab, user_lchs[j], hue_weight
                )
                for j, user_lab in enumerate(user_labs)
            ]
            best = int(np.argmin(costs))
            mapping[i] = user_palette[best]
        return mapping

    all_pairs = sorted(
        [
            (
                i,
                j,
                _palette_match_cost(
                    gen_labs[i], gen_lchs[i], user_labs[j], user_lchs[j], hue_weight
                ),
            )
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
            costs = [
                _palette_match_cost(
                    gen_labs[i], gen_lchs[i], user_lab, user_lchs[j], hue_weight
                )
                for j, user_lab in enumerate(user_labs)
            ]
            mapping[i] = user_palette[int(np.argmin(costs))]
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

    # Stage 2 — Quantize after pbn_v2-style smoothing
    label_map, palette = quantize_colors(
        img,
        k=p["k_colors"],
        blur_sigma=p["blur_sigma"],
        smooth_method=p["smooth_method"],
    )

    # Stage 3b — BYOP (optional)
    if p["use_user_palette"]:
        user_palette_rgb = _parse_user_palette(p)
        if user_palette_rgb:
            mapping = map_palette_to_user_palette(
                palette, user_palette_rgb, allow_reuse=p["allow_color_reuse"]
            )
            palette = np.asarray(
                [mapping[index] for index in range(len(palette))],
                dtype=np.uint8,
            )
            logger.debug("BYOP remapping done, palette colours: %d", len(palette))

    # Stage 4 — Merge small connected regions
    total_pixels = label_map.shape[0] * label_map.shape[1]
    min_region_pixels = max(20, int(total_pixels * (p["min_region_pct"] / 100.0)))
    if not p["no_merge"]:
        label_map = merge_small_regions(label_map, min_region_pixels)

    # Stage 5 — Relabel and render
    label_map, palette = relabel_contiguous(label_map, palette)
    min_region_for_number = max(40, int(total_pixels * 0.0008))
    outline = build_outline_image(
        label_map,
        min_region_for_number=min_region_for_number,
        line_thickness=p["line_thickness"],
    )
    quantized = build_colored_image(label_map, palette)

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
