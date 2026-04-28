<script setup>
import { computed } from 'vue'
import { useJobStore } from '../../stores/jobStore.js'

const emit = defineEmits(['start-over'])

const jobStore = useJobStore()

const urls = computed(() => jobStore.downloadUrls)

const previews = computed(() => [
  {
    key: 'outline',
    label: 'Outline',
    badge: 'Step 1',
    badgeColor: 'var(--color-indigo)',
    badgeText: 'var(--color-snow)',
    rotate: '-2deg',
    url: urls.value?.outline ?? null,
  },
  {
    key: 'color',
    label: 'Colour Fill',
    badge: 'Step 2',
    badgeColor: 'var(--color-lavender)',
    badgeText: 'var(--color-snow)',
    rotate: '0deg',
    url: urls.value?.color ?? null,
  },
  {
    key: 'palette',
    label: 'Palette Sheet',
    badge: 'Step 3',
    badgeColor: 'var(--color-lime)',
    badgeText: 'var(--color-bg)',
    rotate: '2deg',
    url: urls.value?.palette ?? null,
  },
])
</script>

<template>
  <div class="results">

    <!-- Heading -->
    <div class="results__header">
      <h1 class="results__heading">Your Kit is Ready! 🎨</h1>
      <p class="results__sub">Download your files below. Links expire in 1 hour.</p>
    </div>

    <!-- Preview cards -->
    <div class="results__cards">
      <div
        v-for="preview in previews"
        :key="preview.key"
        class="results__card"
        :style="{ transform: `rotate(${preview.rotate})` }"
      >
        <!-- Badge -->
        <div
          class="results__card-badge"
          :style="{ backgroundColor: preview.badgeColor, color: preview.badgeText }"
        >
          {{ preview.badge }}
        </div>

        <!-- Image preview -->
        <div class="results__card-img-wrap">
          <img
            v-if="preview.url"
            :src="preview.url"
            :alt="preview.label"
            class="results__card-img"
            loading="lazy"
          />
          <div v-else class="results__card-placeholder" aria-hidden="true" />
        </div>

        <!-- Label + individual download -->
        <div class="results__card-footer">
          <span class="results__card-label">{{ preview.label }}</span>
          <a
            v-if="preview.url"
            :href="preview.url"
            :download="`paintober-${preview.key}.png`"
            class="results__card-dl"
          >↓ PNG</a>
        </div>
      </div>
    </div>

    <!-- Primary ZIP download -->
    <a
      v-if="urls?.zip"
      :href="urls.zip"
      :download="`paintober-kit.zip`"
      class="results__zip-btn"
    >
      ↓ Download Full Kit (.zip)
    </a>

    <!-- Expiry notice -->
    <p class="results__expiry">⏱ Download links expire 1 hour after job completion.</p>

    <!-- Start over -->
    <button class="results__reset-btn" @click="emit('start-over')">
      Create Another Kit →
    </button>

  </div>
</template>

<style scoped>
.results {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-2xl) var(--space-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xl);
}

/* ── Header ─────────────────────────────────────────────────── */
.results__header {
  text-align: center;
}

.results__heading {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: var(--weight-black);
  color: var(--color-lime);
  text-shadow: 3px 3px 0 var(--color-midnight);
  margin-bottom: var(--space-sm);
}

.results__sub {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-lavender);
}

/* ── Preview cards ──────────────────────────────────────────── */
.results__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-xl);
  width: 100%;
}

.results__card {
  position: relative;
  background-color: var(--color-snow);
  border: var(--border-width-sticker) solid var(--color-bg);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-sticker-md);
  overflow: visible;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

/* ── Badge ──────────────────────────────────────────────────── */
.results__card-badge {
  position: absolute;
  top: -14px;
  left: var(--space-md);
  padding: 2px var(--space-sm);
  border: 3px solid var(--color-bg);
  border-radius: 999px;
  font-family: var(--font-display);
  font-size: var(--text-small);
  font-weight: var(--weight-extrabold);
  box-shadow: var(--shadow-sticker-sm);
}

/* ── Image ──────────────────────────────────────────────────── */
.results__card-img-wrap {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 2px solid var(--color-bg);
  background-color: color-mix(in srgb, var(--color-bg) 10%, var(--color-snow));
}

.results__card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.results__card-placeholder {
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    45deg,
    color-mix(in srgb, var(--color-lavender) 15%, transparent),
    color-mix(in srgb, var(--color-lavender) 15%, transparent) 10px,
    transparent 10px,
    transparent 20px
  );
}

/* ── Card footer ────────────────────────────────────────────── */
.results__card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.results__card-label {
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-bg);
}

.results__card-dl {
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-indigo);
  text-decoration: none;
  padding: 2px var(--space-sm);
  border: 2px solid var(--color-indigo);
  border-radius: var(--radius-button);
  transition: transform var(--transition-fast);
}

.results__card-dl:hover { transform: scale(1.05); }

/* ── ZIP button ─────────────────────────────────────────────── */
.results__zip-btn {
  display: inline-block;
  padding: var(--space-md) var(--space-2xl);
  background-color: var(--color-lime);
  border: 4px solid var(--color-bg);
  box-shadow: var(--shadow-sticker-lg);
  border-radius: var(--radius-button);
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-extrabold);
  color: var(--color-bg);
  text-decoration: none;
  transition: transform var(--transition-fast);
}

.results__zip-btn:hover  { transform: scale(1.05); }
.results__zip-btn:active { transform: scale(0.95); }

/* ── Expiry ─────────────────────────────────────────────────── */
.results__expiry {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: var(--color-lavender);
}

/* ── Reset ──────────────────────────────────────────────────── */
.results__reset-btn {
  padding: var(--space-sm) var(--space-xl);
  background-color: transparent;
  border: 3px solid var(--color-indigo);
  box-shadow: var(--shadow-sticker-sm);
  border-radius: var(--radius-button);
  font-family: var(--font-display);
  font-size: var(--text-body);
  font-weight: var(--weight-extrabold);
  color: var(--color-snow);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.results__reset-btn:hover  { transform: scale(1.05); }
.results__reset-btn:active { transform: scale(0.95); }
</style>
