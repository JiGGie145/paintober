

---

# 🎨 1) Beginner Acrylic Set (12 colors)

**id:** `beginner_acrylic_12`
**description:** Typical starter acrylic kit found in most art stores.

```python
[
("Titanium White", "#FFFFFF"),
("Mars Black", "#1C1C1C"),
("Cadmium Yellow", "#F6C700"),
("Lemon Yellow", "#F9E547"),
("Cadmium Orange", "#F47C2C"),
("Cadmium Red", "#D22B2B"),
("Crimson Red", "#9E1B32"),
("Burnt Sienna", "#A0522D"),
("Burnt Umber", "#6B4423"),
("Sap Green", "#507D2A"),
("Ultramarine Blue", "#3F51B5"),
("Sky Blue", "#6EC1E4"),
]
```

---

# 🎨 2) Acrylic Studio Set (24 colors)

**id:** `studio_acrylic_24`
**description:** Expanded acrylic palette for hobby painters and events.

```python
[
("Titanium White", "#FFFFFF"),
("Mars Black", "#1C1C1C"),
("Neutral Grey", "#8A8A8A"),
("Yellow Ochre", "#C79B3B"),
("Raw Sienna", "#C68642"),
("Burnt Sienna", "#A0522D"),
("Burnt Umber", "#6B4423"),
("Cadmium Yellow", "#F6C700"),
("Lemon Yellow", "#F9E547"),
("Cadmium Orange", "#F47C2C"),
("Cadmium Red", "#D22B2B"),
("Crimson Red", "#9E1B32"),
("Rose Pink", "#F29CA3"),
("Coral", "#FF6F61"),
("Light Flesh", "#E8B89C"),
("Deep Flesh", "#C68673"),
("Sap Green", "#507D2A"),
("Hookers Green", "#3B6B3B"),
("Olive Green", "#6B7D3A"),
("Ultramarine Blue", "#3F51B5"),
("Phthalo Blue", "#1F4E79"),
("Sky Blue", "#6EC1E4"),
("Dioxazine Purple", "#5B2C83"),
("Terracotta", "#C65D3B"),
]
```

---

# 🌸 3) Pastel Picnic Palette (12 colors)

**id:** `pastel_picnic`
**description:** Soft romantic tones perfect for picnics, weddings, couples events.

```python
[
("Cream White", "#FFF5E6"),
("Soft Peach", "#FFD6C9"),
("Blush Pink", "#F7A9A8"),
("Rose Quartz", "#F4C2C2"),
("Lavender", "#C7B8EA"),
("Lilac", "#D8C7FF"),
("Baby Blue", "#BFE3FF"),
("Powder Blue", "#D6ECFF"),
("Mint Green", "#CFF5D6"),
("Sage", "#B7D3C0"),
("Butter Yellow", "#FFF1A8"),
("Soft Coral", "#FFB4A2"),
]
```

---

# 🎉 4) Vibrant Party Palette (12 colors)

**id:** `vibrant_party`
**description:** Bright, punchy colors for sip-and-paint nights and group events.

```python
[
("Bright White", "#FFFFFF"),
("Jet Black", "#111111"),
("Sunshine Yellow", "#FFD400"),
("Neon Orange", "#FF6A00"),
("Fire Red", "#FF2B2B"),
("Hot Pink", "#FF4FA3"),
("Electric Purple", "#7B2EFF"),
("Royal Blue", "#2962FF"),
("Cyan", "#00C2FF"),
("Bright Green", "#2ECC40"),
("Lime", "#A4FF00"),
("Turquoise", "#00D1B2"),
]
```

---

# 🌿 5) Earthy Neutrals Palette (12 colors)

**id:** `earthy_neutrals`
**description:** Landscapes, portraits, and cozy natural scenes.

```python
[
("Ivory", "#F4F1E8"),
("Warm Grey", "#A89F91"),
("Cool Grey", "#8A8F98"),
("Taupe", "#8B6F5A"),
("Sand", "#D9C7A3"),
("Camel", "#C19A6B"),
("Terracotta", "#C65D3B"),
("Rust", "#8C3A2B"),
("Olive", "#6B7D3A"),
("Forest Green", "#355E3B"),
("Slate Blue", "#5A6C8C"),
("Charcoal", "#3B3B3B"),
]
```

---

**Staedtler Noris–style preset** will feel instantly familiar to a lot of people 🎨✏️

These are **approximate digital matches** to the typical Noris / school-pencil lineup.

---

# ✏️ Noris-Style Colouring Pencils (12)

**id:** `staedtler_noris_12`
**description:** Classic school colouring pencil palette inspired by Staedtler Noris sets.

```python
[
("White", "#FFFFFF"),
("Black", "#1C1C1C"),
("Brown", "#7A4A2C"),
("Red", "#C62828"),
("Orange", "#F57C00"),
("Yellow", "#FDD835"),
("Light Green", "#7CB342"),
("Dark Green", "#2E7D32"),
("Light Blue", "#4FC3F7"),
("Dark Blue", "#1E5AA8"),
("Violet", "#7E57C2"),
("Pink", "#F48FB1"),
]
```

---

# ✏️ Noris-Style Colouring Pencils (24)

**id:** `staedtler_noris_24`
**description:** Expanded Noris-style palette with extra shades and skin tones.

```python
[
("White", "#FFFFFF"),
("Black", "#1C1C1C"),
("Light Grey", "#BDBDBD"),
("Dark Grey", "#757575"),

("Dark Brown", "#5D4037"),
("Brown", "#7A4A2C"),
("Light Brown", "#A47551"),
("Beige", "#D7B899"),
("Peach", "#F2B8A0"),

("Pink", "#F48FB1"),
("Magenta", "#D81B60"),
("Red", "#C62828"),
("Dark Red", "#8E0000"),

("Orange", "#F57C00"),
("Light Orange", "#FFB74D"),

("Yellow", "#FDD835"),
("Lemon Yellow", "#FFF176"),

("Light Green", "#9CCC65"),
("Green", "#43A047"),
("Dark Green", "#2E7D32"),

("Light Blue", "#4FC3F7"),
("Blue", "#1E5AA8"),
("Dark Blue", "#0D47A1"),

("Violet", "#7E57C2"),
]
```

This preset will feel super recognizable for:

* Schools
* Kids parties
* Parents
* Teachers

If you want, next we can group all presets into a clean Django fixture structure.

---

Below is a **ready-to-load Django fixture** assuming two models:

```python
class PaintSet(models.Model):
    id = models.SlugField(primary_key=True)
    name = models.CharField(max_length=120)
    description = models.TextField()
    paint_type = models.CharField(max_length=50)
    tube_count = models.IntegerField()

class PaintColor(models.Model):
    paint_set = models.ForeignKey(PaintSet, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=80)
    hex = models.CharField(max_length=7)
```

---

# fixtures/paint_sets.json

You can run later:

```bash
python manage.py loaddata paint_sets.json
```

---

## 🧩 FULL FIXTURE

```json
[
  {
    "model": "yourapp.paintset",
    "pk": "beginner_acrylic_12",
    "fields": {
      "name": "Beginner Acrylic Set (12)",
      "description": "Typical starter acrylic kit found in most art stores.",
      "paint_type": "acrylic",
      "tube_count": 12
    }
  },

  {
    "model": "yourapp.paintset",
    "pk": "studio_acrylic_24",
    "fields": {
      "name": "Acrylic Studio Set (24)",
      "description": "Expanded acrylic palette for hobby painters and events.",
      "paint_type": "acrylic",
      "tube_count": 24
    }
  },

  {
    "model": "yourapp.paintset",
    "pk": "pastel_picnic",
    "fields": {
      "name": "Pastel Picnic Palette",
      "description": "Soft romantic tones perfect for picnics and weddings.",
      "paint_type": "acrylic",
      "tube_count": 12
    }
  },

  {
    "model": "yourapp.paintset",
    "pk": "vibrant_party",
    "fields": {
      "name": "Vibrant Party Palette",
      "description": "Bright punchy colours for sip-and-paint nights.",
      "paint_type": "acrylic",
      "tube_count": 12
    }
  },

  {
    "model": "yourapp.paintset",
    "pk": "earthy_neutrals",
    "fields": {
      "name": "Earthy Neutrals",
      "description": "Perfect for landscapes and portraits.",
      "paint_type": "acrylic",
      "tube_count": 12
    }
  },

  {
    "model": "yourapp.paintset",
    "pk": "staedtler_noris_12",
    "fields": {
      "name": "Noris-Style Colouring Pencils (12)",
      "description": "Inspired by classic school Noris pencils.",
      "paint_type": "pencil",
      "tube_count": 12
    }
  },

  {
    "model": "yourapp.paintset",
    "pk": "staedtler_noris_24",
    "fields": {
      "name": "Noris-Style Colouring Pencils (24)",
      "description": "Expanded Noris-style palette with skin tones.",
      "paint_type": "pencil",
      "tube_count": 24
    }
  }
]
```

---

## 🎨 COLOR FIXTURE

Create second file:

# fixtures/paint_colors.json

```json
[
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Titanium White", "hex": "#FFFFFF" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Mars Black", "hex": "#1C1C1C" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Cadmium Yellow", "hex": "#F6C700" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Lemon Yellow", "hex": "#F9E547" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Cadmium Orange", "hex": "#F47C2C" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Cadmium Red", "hex": "#D22B2B" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Crimson Red", "hex": "#9E1B32" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Burnt Sienna", "hex": "#A0522D" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Burnt Umber", "hex": "#6B4423" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Sap Green", "hex": "#507D2A" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Ultramarine Blue", "hex": "#3F51B5" }},
  { "model": "yourapp.paintcolor", "fields": { "paint_set": "beginner_acrylic_12", "name": "Sky Blue", "hex": "#6EC1E4" }}

  // 👉 STOP HERE FOR NOW
]
```

---

### Why split fixtures?

Because this file will get long fast.
You can safely append more paint sets later.

---

If you want, next we can add a Django admin preview so you can visually inspect palettes 🎨

