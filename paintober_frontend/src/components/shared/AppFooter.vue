<template>
  <footer class="app-footer">
    <p class="footer-text">
      &copy; {{ year }} Paintober — turn any photo into a paint-by-numbers kit.
    </p>
    <p class="footer-note">
      Free tier: 3 jobs per day &bull; Max 50 MB &bull; JPG / PNG / WEBP
    </p>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style scoped>
.app-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xl) var(--space-xl);
  border-top: var(--border-sticker-indigo);
  text-align: center;
}

.footer-text {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  color: var(--color-snow);
  opacity: 0.7;
}

.footer-note {
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: var(--weight-normal);
  color: var(--color-lavender);
}
</style>
