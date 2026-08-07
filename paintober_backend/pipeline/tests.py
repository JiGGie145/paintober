import unittest

import numpy as np

from .processor import (
    build_outline_image,
    circular_hue_distance,
    map_palette_to_user_palette,
    merge_small_regions,
    preprocess_image,
    relabel_contiguous,
    rgb_to_lch,
)


class ProcessorTests(unittest.TestCase):
    def test_preprocess_supports_all_smoothing_methods(self):
        image = np.zeros((12, 12, 3), dtype=np.uint8)
        image[4:8, 4:8] = (255, 80, 20)

        for method in ("meanshift", "bilateral", "gaussian", "none"):
            result = preprocess_image(image, method, 1.5)
            self.assertEqual(result.shape, image.shape)
            self.assertEqual(result.dtype, image.dtype)

    def test_merge_small_regions_reassigns_component(self):
        label_map = np.zeros((8, 8), dtype=np.int32)
        label_map[3:5, 3:5] = 1

        merged = merge_small_regions(label_map, min_region_pixels=5)

        self.assertTrue(np.array_equal(merged, np.zeros_like(label_map)))

    def test_relabel_contiguous_sorts_palette_by_luminance(self):
        label_map = np.array([[0, 1], [1, 0]], dtype=np.int32)
        palette = np.array([(10, 10, 10), (240, 240, 240)], dtype=np.uint8)

        relabeled, sorted_palette = relabel_contiguous(label_map, palette)

        self.assertTrue(np.array_equal(sorted_palette[0], palette[1]))
        self.assertTrue(np.array_equal(relabeled, np.array([[1, 0], [0, 1]])))

    def test_byop_mapping_returns_user_palette_colors(self):
        generated = np.array([(0, 0, 0), (255, 255, 255)], dtype=np.uint8)
        user_palette = [(20, 30, 40), (220, 230, 240)]

        mapping = map_palette_to_user_palette(generated, user_palette, allow_reuse=False)

        self.assertEqual(set(mapping.values()), set(user_palette))

    def test_hue_distance_wraps_around_zero(self):
        self.assertEqual(circular_hue_distance(359.0, 1.0), 2.0)

    def test_low_chroma_colors_do_not_depend_on_hue(self):
        self.assertLess(rgb_to_lch((128, 128, 128))[1], 10.0)

        generated = np.array([(128, 128, 128)], dtype=np.uint8)
        user_palette = [(120, 120, 120), (140, 140, 140)]

        mapping = map_palette_to_user_palette(
            generated, user_palette, hue_weight=100.0
        )

        self.assertEqual(mapping[0], user_palette[0])

    def test_hue_weight_prefers_matching_color_family(self):
        generated = np.array([(40, 100, 220)], dtype=np.uint8)
        user_palette = [(220, 60, 40), (35, 95, 210)]

        for allow_reuse in (True, False):
            mapping = map_palette_to_user_palette(
                generated, user_palette, allow_reuse=allow_reuse
            )
            self.assertEqual(mapping[0], user_palette[1])

    def test_hue_weight_zero_preserves_lab_only_matching(self):
        generated = np.array([(40, 100, 220)], dtype=np.uint8)
        user_palette = [(220, 60, 40), (35, 95, 210)]

        mapping = map_palette_to_user_palette(
            generated, user_palette, hue_weight=0.0
        )

        self.assertIn(mapping[0], user_palette)

    def test_outline_has_expected_shape(self):
        label_map = np.array([[0, 0, 1], [0, 1, 1]], dtype=np.int32)

        outline = build_outline_image(label_map, min_region_for_number=1)

        self.assertEqual(outline.shape, (2, 3, 3))
        self.assertEqual(outline.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
