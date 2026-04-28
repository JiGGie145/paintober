<script setup>
defineProps({
  message: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['dismiss'])
</script>

<template>
  <div class="error-banner" role="alert" aria-live="assertive">
    <span class="error-banner__message">{{ message }}</span>
    <button
      class="error-banner__dismiss"
      aria-label="Dismiss error"
      @click="emit('dismiss')"
    >✕</button>
  </div>
</template>

<style scoped>
.error-banner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-snow);
  border-left: 4px solid var(--color-pink);
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sticker-sm);
}

.error-banner__message {
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  color: var(--color-bg);
  flex: 1;
}

.error-banner__dismiss {
  flex-shrink: 0;
  background: transparent;
  border: 2px solid var(--color-pink);
  border-radius: var(--radius-badge);
  color: var(--color-pink);
  font-size: var(--text-sm);
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--transition-fast);
}
.error-banner__dismiss:hover { transform: scale(1.1); }
</style>
