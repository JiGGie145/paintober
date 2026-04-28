<script setup>
import { ref } from 'vue'
import AppHeader from './components/shared/AppHeader.vue'
import AppFooter from './components/shared/AppFooter.vue'
import HistoryPanel from './components/shared/HistoryPanel.vue'

const historyOpen = ref(false)
</script>

<template>
  <AppHeader @toggle-history="historyOpen = !historyOpen" />
  <main>
    <RouterView />
  </main>
  <AppFooter />
  <HistoryPanel :open="historyOpen" @close="historyOpen = false" />
</template>

<style scoped>
main {
  min-height: calc(100dvh - 64px);
}
</style>
