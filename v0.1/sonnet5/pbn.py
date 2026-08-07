#!/usr/bin/env python3
"""
Paint by Numbers Generator
===========================

Takes an input photo and produces a full paint-by-numbers pack:
  1. <name>_outline.png  - white canvas with black region outlines + numbers
  2. <name>_colored.png  - the "finished painting" preview (posterized image)
  3. <name>_palette.png  - a legend mapping each number to its RGB/hex color

Usage:
    python pbn.py input.jpg
    python pbn.py input.jpg --colors 18 --output-dir out --width 1200
    python pbn.py input.jpg --min-region-pct 0.05 --no-merge

Dependencies: numpy, pillow, scipy, scikit-learn, opencv-python
"""

import argparse
import os
import sys

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from sklearn.cluster import KMeans

FONT_PATH_CANDIDATES = [
    "/Users/monahengramokhoro/projects/python/paintober/v0.1/sonnet5/DejaVu_Sans/DejaVuSans-Bold.ttf",
    "/Users/monahengramokhoro/projects/python/paintober/v0.1/sonnet5/DejaVu_Sans/DejaVuSans-Bold.ttf",
]


def find_font():
    for path in FONT_PATH_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def load_image(path, max_width):
    """Load an image, convert to RGB, and downscale if wider than max_width."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if w > max_width:
        new_h = int(h * (max_width / w))
        img = img.resize((max_width, new_h), Image.LANCZOS)
    return np.array(img)


def quantize_colors(img_arr, n_colors, blur_sigma):
    """
    Reduce the image to at most n_colors using KMeans clustering in RGB space.
    Returns:
        label_map: (H, W) int array of cluster indices
        centers: (k, 3) uint8 array of cluster RGB colors
    """
    h, w, _ = img_arr.shape

    # Light blur first so quantization isn't dominated by pixel-level noise.
    if blur_sigma > 0:
        smoothed = cv2.GaussianBlur(img_arr, (0, 0), sigmaX=blur_sigma)
    else:
        smoothed = img_arr

    pixels = smoothed.reshape(-1, 3).astype(np.float32)

    # Don't ask KMeans for more clusters than unique colors that exist.
    n_unique = len(np.unique(pixels.astype(np.uint8), axis=0))
    k = max(1, min(n_colors, n_unique))

    kmeans = KMeans(n_clusters=k, n_init=4, random_state=42)
    labels = kmeans.fit_predict(pixels)
    centers = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)

    label_map = labels.reshape(h, w)
    return label_map, centers


def merge_small_regions(label_map, min_region_pixels):
    """
    Find connected components per label; any component smaller than
    min_region_pixels gets reassigned to whichever neighboring label
    borders it most. Repeats until stable (small slivers can border
    other small slivers).
    """
    label_map = label_map.copy()
    structure = np.ones((3, 3), dtype=int)  # 8-connectivity

    for _ in range(6):  # a handful of passes is enough to converge in practice
        changed = False
        unique_labels = np.unique(label_map)

        # Build one connected-component map across all labels at once by
        # offsetting each label's component ids into a shared id space.
        comp_map = np.zeros_like(label_map, dtype=np.int64)
        next_id = 1
        comp_sizes = {}
        comp_label_of = {}

        for lbl in unique_labels:
            mask = label_map == lbl
            comp, n = ndimage.label(mask, structure=structure)
            comp_ids = comp[mask] + next_id - 1
            comp_map[mask] = comp[mask] + (next_id - 1)
            for cid in range(1, n + 1):
                gid = cid + next_id - 1
                size = int(np.sum(comp == cid))
                comp_sizes[gid] = size
                comp_label_of[gid] = lbl
            next_id += n

        small_ids = [gid for gid, sz in comp_sizes.items() if sz < min_region_pixels]
        if not small_ids:
            break

        # Process smallest components first so merges cascade sensibly.
        small_ids.sort(key=lambda g: comp_sizes[g])

        for gid in small_ids:
            mask = comp_map == gid
            if not mask.any():
                continue
            # Look at the dilated boundary to find neighboring component ids.
            dilated = ndimage.binary_dilation(mask, structure=structure)
            border = dilated & ~mask
            neighbor_ids = comp_map[border]
            neighbor_ids = neighbor_ids[neighbor_ids != gid]
            if neighbor_ids.size == 0:
                continue
            # Vote by area: pick the neighboring label with the most bordering pixels.
            vals, counts = np.unique(neighbor_ids, return_counts=True)
            winner_gid = vals[np.argmax(counts)]
            winner_label = comp_label_of.get(int(winner_gid))
            if winner_label is None:
                continue
            label_map[mask] = winner_label
            changed = True

        if not changed:
            break

    return label_map


def relabel_contiguous(label_map, centers):
    """Remap whatever labels survive to 0..N-1, sorted darkest->lightest
    for a more natural numbering order, and drop unused colors."""
    used = np.unique(label_map)
    used_centers = centers[used]

    # Sort by luminance so numbering feels intentional rather than random.
    luminance = 0.299 * used_centers[:, 0] + 0.587 * used_centers[:, 1] + 0.114 * used_centers[:, 2]
    order = np.argsort(luminance)[::-1]  # lightest first tends to read better on canvas
    sorted_old_labels = used[order]
    sorted_centers = used_centers[order]

    remap = {int(old): new for new, old in enumerate(sorted_old_labels)}
    new_label_map = np.vectorize(remap.get)(label_map).astype(np.int32)

    return new_label_map, sorted_centers


def build_outline_image(label_map, min_region_for_number, font_path):
    """White canvas, black borders between regions, numbers in each
    sufficiently large connected region."""
    h, w = label_map.shape
    canvas = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(canvas)

    # Borders: any pixel whose right or bottom neighbor has a different label.
    border = np.zeros((h, w), dtype=bool)
    border[:, :-1] |= label_map[:, :-1] != label_map[:, 1:]
    border[:-1, :] |= label_map[:-1, :] != label_map[1:, :]

    canvas_arr = np.array(canvas)
    canvas_arr[border] = (0, 0, 0)
    canvas = Image.fromarray(canvas_arr)
    draw = ImageDraw.Draw(canvas)

    structure = np.ones((3, 3), dtype=int)
    unique_labels = np.unique(label_map)

    for lbl in unique_labels:
        mask = label_map == lbl
        comp, n = ndimage.label(mask, structure=structure)
        for cid in range(1, n + 1):
            comp_mask = comp == cid
            area = int(np.sum(comp_mask))
            if area < min_region_for_number:
                continue

            ys, xs = np.where(comp_mask)
            # Use the point farthest from the region's edge as the label
            # position, so numbers land inside the shape, not on a border.
            dist = ndimage.distance_transform_edt(comp_mask)
            cy, cx = np.unravel_index(np.argmax(dist), dist.shape)
            max_dist = dist[cy, cx]

            # Scale font size to how much room we actually have, within reason.
            font_size = int(np.clip(max_dist * 1.1, 8, 28))
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()

            text = str(lbl + 1)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            if tw > max_dist * 2.2 or th > max_dist * 2.2:
                # Not actually enough room once we measure the real glyph size.
                continue

            draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), text, fill=(0, 0, 0), font=font)

    return canvas


def build_colored_image(label_map, centers):
    h, w = label_map.shape
    flat_colors = centers[label_map.reshape(-1)]
    img = flat_colors.reshape(h, w, 3).astype(np.uint8)
    return Image.fromarray(img)


def build_palette_image(centers, font_path, swatch=90, cols=4):
    n = len(centers)
    cols = min(cols, n)
    rows = int(np.ceil(n / cols))

    pad = 16
    label_h = 34
    cell_w = swatch + pad
    cell_h = swatch + label_h + pad

    img_w = cols * cell_w + pad
    img_h = rows * cell_h + pad

    canvas = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(canvas)

    title_font = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
    label_font = ImageFont.truetype(font_path, 16) if font_path else ImageFont.load_default()

    for i, color in enumerate(centers):
        r, c = divmod(i, cols)
        x0 = pad + c * cell_w
        y0 = pad + r * cell_h
        color_tuple = tuple(int(v) for v in color)

        draw.rectangle([x0, y0, x0 + swatch, y0 + swatch], fill=color_tuple, outline=(0, 0, 0), width=2)

        # Contrast-aware number drawn on the swatch itself.
        luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        text_color = (0, 0, 0) if luminance > 140 else (255, 255, 255)
        text = str(i + 1)
        bbox = draw.textbbox((0, 0), text, font=title_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (x0 + swatch / 2 - tw / 2 - bbox[0], y0 + swatch / 2 - th / 2 - bbox[1]),
            text, fill=text_color, font=title_font,
        )

        hex_code = "#{:02X}{:02X}{:02X}".format(*color_tuple)
        label_text = f"{hex_code}"
        rgb_text = f"RGB {color_tuple[0]},{color_tuple[1]},{color_tuple[2]}"
        draw.text((x0, y0 + swatch + 4), label_text, fill=(0, 0, 0), font=label_font)
        draw.text((x0, y0 + swatch + 4 + 16), rgb_text, fill=(80, 80, 80), font=label_font)

    return canvas


def main():
    parser = argparse.ArgumentParser(description="Generate a paint-by-numbers pack from an image.")
    parser.add_argument("input", help="Path to the input image")
    parser.add_argument("--colors", type=int, default=24, help="Max number of colors (<=24). Default 24.")
    parser.add_argument("--output-dir", default=None, help="Directory to write outputs. Defaults to input's directory.")
    parser.add_argument("--width", type=int, default=1400, help="Max output width in pixels (downscales larger images). Default 1400.")
    parser.add_argument("--min-region-pct", type=float, default=0.03,
                         help="Regions smaller than this %% of image area get merged into neighbors. Default 0.03 (i.e. 0.03%%).")
    parser.add_argument("--no-merge", action="store_true", help="Disable small-region merging.")
    parser.add_argument("--blur", type=float, default=1.5, help="Gaussian blur sigma applied before quantization. Default 1.5.")
    args = parser.parse_args()

    if args.colors < 1 or args.colors > 24:
        parser.error("--colors must be between 1 and 24")

    if not os.path.exists(args.input):
        parser.error(f"Input file not found: {args.input}")

    base_name = os.path.splitext(os.path.basename(args.input))[0]
    out_dir = args.output_dir or os.path.dirname(os.path.abspath(args.input))
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading {args.input} ...")
    img_arr = load_image(args.input, args.width)
    h, w = img_arr.shape[:2]
    total_px = h * w
    print(f"Working size: {w}x{h}")

    print(f"Quantizing to at most {args.colors} colors ...")
    label_map, centers = quantize_colors(img_arr, args.colors, args.blur)
    print(f"  -> {len(centers)} colors found")

    if not args.no_merge:
        min_region_pixels = max(20, int(total_px * (args.min_region_pct / 100.0)))
        print(f"Merging regions smaller than {min_region_pixels} px ...")
        label_map = merge_small_regions(label_map, min_region_pixels)

    label_map, centers = relabel_contiguous(label_map, centers)
    print(f"Final palette size: {len(centers)} colors")

    font_path = find_font()
    if not font_path:
        print("Warning: no TTF font found, falling back to a small default font.")

    min_region_for_number = max(40, int(total_px * 0.0008))

    print("Building outline image ...")
    outline_img = build_outline_image(label_map, min_region_for_number, font_path)

    print("Building colored preview ...")
    colored_img = build_colored_image(label_map, centers)

    print("Building palette legend ...")
    palette_img = build_palette_image(centers, font_path)

    outline_path = os.path.join(out_dir, f"{base_name}_outline.png")
    colored_path = os.path.join(out_dir, f"{base_name}_colored.png")
    palette_path = os.path.join(out_dir, f"{base_name}_palette.png")

    outline_img.save(outline_path)
    colored_img.save(colored_path)
    palette_img.save(palette_path)

    print("\nDone! Files written:")
    print(f"  {outline_path}")
    print(f"  {colored_path}")
    print(f"  {palette_path}")


if __name__ == "__main__":
    main()
