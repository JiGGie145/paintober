### Task
Refactor the color mapping implementation to incorporate a continuous Hue Angular Penalty using CIELCH (or HSV) hue angles, ensuring colors map primarily to candidates within the same hue family (e.g., blue maps to blue).

### Inputs / Context
Original snippet provided in the codebase:
- `hex_to_rgb`
- `rgb_to_lab`
- `delta_e`
- `map_palette_to_user_palette`

### Technical Requirements

1. **Hue Angle Extraction:**
   - Add a helper function `rgb_to_lch(color_rgb: Tuple[int, int, int]) -> Tuple[float, float, float]` (or standard conversion to extract Lightness, Chroma, and Hue angle in degrees $0^\circ \text{ to } 360^\circ$).
   - Note: For low-chroma / desaturated colors (e.g., grays, blacks, whites where Chroma $< 10$), hue angle becomes unstable. Dampen or ignore the hue penalty when either source or target color is desaturated.

2. **Shortest Angular Distance Calculation:**
   - Implement shortest angular distance for hue angles ($0^\circ \text{ to } 180^\circ$):
     $$\Delta h = \min(|h_1 - h_2|, 360 - |h_1 - h_2|)$$

3. **Modified Cost Metric:**
   - Define a combined distance function:
     $$\text{Cost} = \Delta E(\text{LAB}_1, \text{LAB}_2) + (w_{\text{hue}} \cdot \Delta h)$$
   - Add a default parameter `hue_weight: float = 2.0` (or configurable weight parameter) to `map_palette_to_user_palette`.

4. **Refactor `map_palette_to_user_palette`:**
   - Update distance calculations in both branches (`allow_reuse=True` and `allow_reuse=False`).
   - For `allow_reuse=True`: Compute the combined cost for each user color candidate and pick the minimum.
   - For `allow_reuse=False`: Build the pairwise distance list/matrix using the combined cost score, then greedily or Hungarian-pair lowest-cost matches first before running the fallback loop.

5. **Interface Compatibility:**
   - Preserve existing function signatures, input formats (RGB tuples), and return types (`dict` / `Dict[int, Tuple[int, int, int]]`).