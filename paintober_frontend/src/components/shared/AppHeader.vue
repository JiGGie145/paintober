<script setup>
import { RouterLink } from 'vue-router'
import LogoPng from '@/assets/Paintober-Logo.png'

const emit = defineEmits(['toggle-history'])
</script>

<template>
  <header class="app-header">
    <RouterLink to="/" class="logo-link" aria-label="Paintober home">
      <img class="logo-img" :src="LogoPng" alt="Paintober" />
    </RouterLink>

    <nav class="nav">
      <RouterLink to="/studio" class="nav-cta">
        <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <span class="nav-label">Start Creating →</span>
      </RouterLink>
    </nav>

    <button
      class="history-btn"
      aria-label="View job history"
      @click="emit('toggle-history')"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <span class="history-label">History</span>
    </button>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: var(--z-overlay);
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-md) var(--space-xl);
  background-color: var(--color-bg);
  border-bottom: var(--border-sticker-indigo);
}

/* Logo */
.logo-link {
  text-decoration: none;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.logo-img {
  height: 40px;
  width: auto;
  display: block;
}

/* Nav */
.nav {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.nav-cta {
  display: inline-block;
  padding: var(--space-sm) var(--space-lg);
  background-color: var(--color-lime);
  border: var(--border-sticker-bg);
  box-shadow: var(--shadow-sticker-sm);
  border-radius: var(--radius-badge);
  font-family: var(--font-display);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-bg);
  text-decoration: none;
  transition: transform var(--transition-fast);
}

.nav-cta:hover {
  transform: scale(1.05);
}

.nav-cta:active {
  transform: scale(0.97);
}

/* History button */
.history-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background-color: transparent;
  border: var(--border-sticker-snow);
  box-shadow: var(--shadow-sticker-sm);
  border-radius: var(--radius-badge);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
  cursor: pointer;
  transition: transform var(--transition-fast);
  flex-shrink: 0;
}

.history-btn:hover {
  transform: scale(1.05);
}

.history-btn:active {
  transform: scale(0.97);
}

/* ── Mobile: icon-only nav ──────────────────────────────────── */
.nav-icon {
  display: none;
}

@media (max-width: 640px) {
  .nav-label,
  .history-label {
    display: none;
  }

  .nav-icon {
    display: block;
  }

  .nav-cta {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    padding: 0;
  }

  .history-btn {
    width: 44px;
    height: 44px;
    padding: 0;
    justify-content: center;
  }
}
</style>
