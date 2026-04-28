<!--
  HeroSection.vue
  ─────────────────────────────────────────────────────────────
  PURPOSE: structural compositor — stacks HeroBackground (z:0)
  beneath HeroContent (z:1). Contains no decorative rules.

  Layer order:
    [HeroBackground] absolute, inset:0, z:0  — decorative only
    [HeroContent]    relative,         z:1  — text + CTA only
  ─────────────────────────────────────────────────────────────
-->
<script setup>
import HeroBackground from './HeroBackground.vue'
import HeroContent from './HeroContent.vue'
</script>

<template>
  <section class="hero-section">
    <HeroBackground />
    <HeroContent />
  </section>
</template>

<style scoped>
.hero-section {
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
