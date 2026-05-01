<script setup>
import PresetGrid from './PresetGrid.vue'
import ByopSection from './ByopSection.vue'

const props = defineProps({
  params: {
    type: Object,
    required: true,
  },
  paletteMode: {
    type: String, // 'auto' | 'preset' | 'byop'
    required: true,
  },
  palettes: {
    type: Array,
    default: null,
  },
  palettesLoading: {
    type: Boolean,
    default: false,
  },
  selectedPresetId: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['update:paletteMode', 'update:params', 'select-preset'])

const tiles = [
  {
    id: 'auto',
    icon: '✨',
    title: 'Auto generate palette',
    body: "We'll pick the best colors from your photo automatically.",
    footer: 'Best for beginners',
    badge: 'Recommended',
  },
  {
    id: 'preset',
    icon: '🎨',
    title: 'Choose a paint set',
    body: 'Use colors from real paint kits and pencil packs.',
    footer: 'Perfect for events & classes',
    badge: null,
  },
  {
    id: 'byop',
    icon: '🧪',
    title: 'Use my own colors',
    body: 'Add the paints you already have at home.',
    footer: 'Advanced users',
    badge: null,
  },
]

function selectTile(id) {
  emit('update:paletteMode', id)
}
</script>

<template>
  <div class="palette-selector">
    <!-- Hint text on the dark page background, above the card -->
    <p class="palette-selector__hint">
      Using the same paints as your guests? Choose a preset paint set for best results.
    </p>

    <!-- Main snow card -->
    <div class="palette-selector__card">
      <h2 class="palette-selector__title">Choose your paint colors</h2>
      <p class="palette-selector__sub">Pick how Paintober selects colors</p>

      <!-- 3 choice tiles -->
      <div class="palette-selector__tiles" role="radiogroup" aria-label="Palette mode">
        <button
          v-for="tile in tiles"
          :key="tile.id"
          class="palette-tile"
          :class="{ 'palette-tile--active': paletteMode === tile.id }"
          role="radio"
          :aria-checked="paletteMode === tile.id"
          @click="selectTile(tile.id)"
        >
          <span v-if="tile.badge" class="palette-tile__badge">{{ tile.badge }}</span>
          <span class="palette-tile__icon" aria-hidden="true">{{ tile.icon }}</span>
          <span class="palette-tile__title">{{ tile.title }}</span>
          <span class="palette-tile__body">{{ tile.body }}</span>
          <span class="palette-tile__footer">{{ tile.footer }}</span>
        </button>
      </div>

      <!-- Expanded: preset grid -->
      <div v-if="paletteMode === 'preset'" class="palette-selector__expanded">
        <PresetGrid
          :palettes="palettes"
          :loading="palettesLoading"
          :selectedId="selectedPresetId"
          @select="emit('select-preset', $event)"
        />
        <p v-if="!palettesLoading && selectedPresetId === null" class="palette-selector__choose-prompt">
          Select a set above to continue.
        </p>
      </div>

      <!-- Expanded: BYOP builder -->
      <div v-else-if="paletteMode === 'byop'" class="palette-selector__expanded">
        <ByopSection :params="params" @update:params="emit('update:params', $event)" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.palette-selector {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* Hint — floats above the card on the dark page background */
.palette-selector__hint {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-snow);
  text-align: center;
  margin: 0;
  padding: 0;
  line-height: var(--leading-normal);
}

/* Main card — snow background, lime border, hard shadow */
.palette-selector__card {
  background-color: var(--color-snow);
  border: 3px solid var(--color-lime);
  box-shadow: 5px 5px 0 var(--color-midnight);
  border-radius: 24px;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.palette-selector__title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: var(--weight-extrabold);
  color: var(--color-bg);
  margin: 0;
}

.palette-selector__sub {
  font-family: var(--font-body);
  font-size: 0.95rem;
  font-weight: var(--weight-medium);
  color: #666;
  margin: calc(-1 * var(--space-sm)) 0 0;
}

/* Tiles row */
.palette-selector__tiles {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

@media (max-width: 600px) {
  .palette-selector__tiles {
    grid-template-columns: 1fr;
  }
}

/* Individual tile — light card on the snow container */
.palette-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-lg);
  background-color: #fff;
  border: 3px solid #ddd;
  box-shadow: 2px 2px 0 #ccc;
  border-radius: var(--radius-md);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s, background-color 0.15s, box-shadow 0.15s;
}

.palette-tile:hover {
  border-color: #bbb;
  transform: translateY(-2px);
  box-shadow: 4px 4px 0 #bbb;
}

.palette-tile--active {
  background-color: var(--color-lime);
  border: 3px solid var(--color-bg);
  box-shadow: var(--shadow-sticker-md-dark);
}

/* Tile badge — lavender pill, readable on both white and lime */
.palette-tile__badge {
  display: inline-block;
  align-self: flex-start;
  padding: 1px var(--space-sm);
  background-color: var(--color-indigo);
  color: var(--color-snow);
  font-family: var(--font-body);
  font-size: 0.65rem;
  font-weight: var(--weight-bold);
  border-radius: var(--radius-badge);
  border: 1px solid var(--color-bg);
  line-height: 1.6;
}

.palette-tile__icon {
  font-size: 2rem;
  line-height: 1;
  margin-bottom: var(--space-xs);
}

.palette-tile__title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: var(--weight-bold);
  color: var(--color-bg);
}

.palette-tile__body {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: #666;
  line-height: var(--leading-normal);
  flex: 1;
}

.palette-tile__footer {
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: var(--weight-bold);
  color: var(--color-indigo);
  margin-top: var(--space-xs);
}

/* Expanded panel */
.palette-selector__expanded {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  animation: expand-in 0.2s ease;
}

.palette-selector__choose-prompt {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  color: #888;
  text-align: center;
  margin: 0;
}

@keyframes expand-in {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
