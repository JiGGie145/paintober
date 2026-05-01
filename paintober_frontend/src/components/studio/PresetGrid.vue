<script setup>
import PresetCard from './PresetCard.vue'

defineProps({
  palettes: {
    type: Array,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  selectedId: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['select'])
</script>

<template>
  <div class="preset-grid-scroll">
    <div class="preset-grid">
      <!-- Loading skeletons -->
      <template v-if="loading">
        <div v-for="n in 6" :key="n" class="preset-grid__skeleton" aria-hidden="true" />
      </template>

      <!-- Cards -->
      <template v-else-if="palettes">
        <PresetCard
          v-for="paintSet in palettes"
          :key="paintSet.id"
          :paintSet="paintSet"
          :selected="paintSet.id === selectedId"
          @select="emit('select', $event)"
        />
      </template>
    </div>
  </div>
</template>

<style scoped>
/* Scroll container — light panel matching Figma inner gray area */
.preset-grid-scroll {
  background-color: #f8f8f8;
  border: 2px solid #ddd;
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  max-height: 24rem;
  overflow-y: auto;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

@media (max-width: 700px) {
  .preset-grid-scroll {
    max-height: none;
    overflow-y: visible;
    padding: var(--space-md);
  }

  .preset-grid {
    display: flex;
    flex-direction: row;
    overflow-x: auto;
    gap: var(--space-md);
    padding-bottom: var(--space-sm);
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
  }

  .preset-grid :deep(.preset-card) {
    min-width: 220px;
    scroll-snap-align: start;
  }
}

/* Skeleton — light grays on the #f8f8f8 container */
.preset-grid__skeleton {
  height: 130px;
  border-radius: 12px;
  background: linear-gradient(
    90deg,
    #ebebeb 25%,
    #f0f0f0 50%,
    #ebebeb 75%
  );
  background-size: 200% 100%;
  animation: skeleton-sweep 1.4s ease-in-out infinite;
}

@keyframes skeleton-sweep {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
