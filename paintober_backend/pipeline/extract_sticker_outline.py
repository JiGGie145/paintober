import cv2
import numpy as np

def extract_filled_outlines(image_path, output_path, darkness_threshold=60):
    # 1. Load image
    img = cv2.imread(image_path)
    # 2. Convert to LAB color space (L channel handles lightness/perceived brightness)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, _, _ = cv2.split(lab)
    # 3. Threshold the L channel to isolate dark pixels (lines)
    # Adjust darkness_threshold (e.g., 40 to 80) depending on line intensity
    _, line_mask = cv2.threshold(l_channel, darkness_threshold, 255, cv2.THRESH_BINARY_INV)
    # 4. Clean up noise and close small gaps inside the filled lines
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned_mask = cv2.morphologyEx(line_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    # 5. Optional: Remove tiny speckles/artifacts
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned_mask)
    min_size = 20  # Minimum pixel area for valid line work
    filtered_mask = np.zeros_like(cleaned_mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_size:
            filtered_mask[labels == i] = 255
    # 6. Invert: White background with solid black line art
    final_output = cv2.bitwise_not(filtered_mask)
    # 7. Force outer background to pure white (cleans up any sticker border shadows)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    _, white_bg_mask = cv2.threshold(hsv[:, :, 2], 240, 255, cv2.THRESH_BINARY)
    final_output[white_bg_mask == 255] = 255
    cv2.imwrite(output_path, final_output)

# Usage
# extract_filled_outlines("sticker_output.png", "filled_lines.png", darkness_threshold=65)