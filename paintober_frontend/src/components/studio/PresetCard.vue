<script setup>
const props = defineProps({
  paintSet: {
    type: Object,
    required: true,
  },
  selected: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['select'])
</script>

<template>
  <button
    class="preset-card"
    :class="{ 'preset-card--selected': selected }"
    @click="emit('select', paintSet.id)"
    :aria-pressed="selected"
  >
    <!-- Tag badge -->
    <span v-if="paintSet.tag" class="preset-card__tag">{{ paintSet.tag }}</span>

    <!-- Name -->
    <p class="preset-card__name">{{ paintSet.name }}</p>

    <!-- Swatch row -->
    <div class="preset-card__swatches" aria-hidden="true">
      <span
        v-for="color in paintSet.colors"
        :key="color.hex"
        class="preset-card__swatch"
        :style="{ backgroundColor: color.hex }"
      />
    </div>

    <!-- Description -->
    <p class="preset-card__desc">{{ paintSet.description }}</p>

    <!-- Selected checkmark -->
    <span v-if="selected" class="preset-card__check" aria-hidden="true">✓</span>
  </button>
</template>

<style scoped>
.preset-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  padding: var(--space-md);
  background-color: #fff;
  border: 2px solid #ddd;
  box-shadow: 1px 1px 0 #ccc;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s, background-color 0.15s;
  width: 100%;
}

.preset-card:hover {
  border-color: #bbb;
  transform: translateY(-2px);
  box-shadow: 4px 4px 0 #bbb;
}

.preset-card--selected {
  border-color: var(--color-lime);
  background-color: color-mix(in srgb, var(--color-lime) 12%, #fff);
  box-shadow: var(--shadow-sticker-sm);
}

/* Tag */
.preset-card__tag {
  display: inline-block;
  align-self: flex-start;
  padding: 2px var(--space-sm);
  background-color: var(--color-indigo);
  color: var(--color-snow);
  font-family: var(--font-body);
  font-size: 0.65rem;
  font-weight: var(--weight-bold);
  border-radius: var(--radius-badge);
  border: 1px solid var(--color-bg);
  line-height: 1.6;
}

/* Name */
.preset-card__name {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: var(--weight-bold);
  color: var(--color-bg);
  margin: 0;
}

/* Swatches */
.preset-card__swatches {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.preset-card__swatch {
  display: block;
  width: 16px;
  height: 16px;
  border-radius: var(--radius-circle);
  border: 1px solid var(--color-bg);
  flex-shrink: 0;
}

/* Description */
.preset-card__desc {
  font-family: var(--font-body);
  font-size: 0.8rem;
  color: #666;
  margin: 0;
  line-height: var(--leading-normal);
}

/* Checkmark */
.preset-card__check {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  width: 20px;
  height: 20px;
  background-color: var(--color-lime);
  color: var(--color-bg);
  border-radius: var(--radius-circle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: var(--weight-black);
  line-height: 1;
}
</style>
