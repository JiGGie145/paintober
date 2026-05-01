<script setup>
const props = defineProps({
  params: {
    type: Object,
    required: true,
  },
  paletteMode: {
    type: String,
    default: 'auto',
  },
})

const emit = defineEmits(['update:params'])

function update(key, value) {
  emit('update:params', { ...props.params, [key]: value })
}
</script>

<template>
  <div class="basic-params">

    <!-- k_colors — hidden when a preset is active (color count is fixed) -->
    <div v-if="paletteMode !== 'preset'" class="param-row">
      <label class="param-label" :for="'k_colors'">
        Colours
        <span class="param-value">{{ params.k_colors }}</span>
      </label>
      <input
        id="k_colors"
        type="range"
        :value="params.k_colors"
        min="2"
        max="32"
        step="1"
        class="param-range"
        @input="update('k_colors', Number($event.target.value))"
      />
      <div class="param-range-labels">
        <span>2</span><span>32</span>
      </div>
    </div>

    <!-- line_thickness -->
    <div class="param-row">
      <label class="param-label" :for="'line_thickness'">
        Line Thickness
        <span class="param-value">{{ params.line_thickness }}</span>
      </label>
      <input
        id="line_thickness"
        type="range"
        :value="params.line_thickness"
        min="1"
        max="10"
        step="1"
        class="param-range"
        @input="update('line_thickness', Number($event.target.value))"
      />
      <div class="param-range-labels">
        <span>1</span><span>10</span>
      </div>
    </div>

    <!-- min_region_area -->
    <div class="param-row">
      <label class="param-label" :for="'min_region_area'">
        Min Region Area
        <span class="param-value">{{ params.min_region_area }} px²</span>
      </label>
      <input
        id="min_region_area"
        type="range"
        :value="params.min_region_area"
        min="0"
        max="1000"
        step="10"
        class="param-range"
        @input="update('min_region_area', Number($event.target.value))"
      />
      <div class="param-range-labels">
        <span>0</span><span>1000</span>
      </div>
    </div>

    <!-- contour_epsilon -->
    <div class="param-row">
      <label class="param-label" :for="'contour_epsilon'">
        Contour Smoothing
        <span class="param-value">{{ params.contour_epsilon }}</span>
      </label>
      <input
        id="contour_epsilon"
        type="number"
        :value="params.contour_epsilon"
        min="0.0"
        max="0.02"
        step="0.001"
        class="param-number"
        @input="update('contour_epsilon', Number($event.target.value))"
      />
    </div>

    <!-- apply_gaussian -->
    <div class="param-row param-row--toggle">
      <label class="param-label param-label--toggle" :for="'apply_gaussian'">
        Smooth edges (Gaussian blur)
      </label>
      <button
        id="apply_gaussian"
        class="toggle"
        :class="{ 'toggle--on': params.apply_gaussian }"
        role="switch"
        :aria-checked="params.apply_gaussian"
        @click="update('apply_gaussian', !params.apply_gaussian)"
      >
        <span class="toggle__thumb" />
      </button>
    </div>

  </div>
</template>

<style scoped>
.basic-params {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* ── Row ────────────────────────────────────────────────────── */
.param-row {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.param-row--toggle {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

/* ── Labels ─────────────────────────────────────────────────── */
.param-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
}

.param-label--toggle {
  justify-content: flex-start;
}

.param-value {
  font-family: var(--font-display);
  font-size: var(--text-small);
  font-weight: var(--weight-extrabold);
  color: var(--color-lime);
}

/* ── Range inputs ───────────────────────────────────────────── */
.param-range {
  width: 100%;
  accent-color: var(--color-lime);
  cursor: pointer;
  height: 6px;
}

.param-range-labels {
  display: flex;
  justify-content: space-between;
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--color-lavender);
}

/* ── Number input ───────────────────────────────────────────── */
.param-number {
  width: 100px;
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--color-bg);
  border: 2px solid var(--color-indigo);
  border-radius: var(--radius-sm);
  color: var(--color-snow);
  font-family: var(--font-body);
  font-size: var(--text-body);
}

.param-number:focus {
  outline: none;
  border-color: var(--color-lime);
}

/* ── Toggle ─────────────────────────────────────────────────── */
.toggle {
  position: relative;
  width: 52px;
  height: 28px;
  background-color: var(--color-lavender);
  border: 3px solid var(--color-snow);
  border-radius: 999px;
  box-shadow: var(--shadow-sticker-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  flex-shrink: 0;
}

.toggle--on {
  background-color: var(--color-lime);
}

.toggle__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background-color: var(--color-snow);
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: 1px 1px 0 var(--color-midnight);
}

.toggle--on .toggle__thumb {
  transform: translateX(24px);
}
</style>
