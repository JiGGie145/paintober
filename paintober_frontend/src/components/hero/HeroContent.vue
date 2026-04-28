<!--
  HeroContent.vue
  ─────────────────────────────────────────────────────────────
  PURPOSE: foreground content layer for the hero section.

  RULES (enforced by architecture):
  • position: relative — sits above HeroBackground via z-index
  • z-index: var(--z-content)
  • NO background styling of any kind
  • NO decorative position:absolute elements
  • Only: layout, headings, copy, buttons, spacing
  ─────────────────────────────────────────────────────────────
-->
<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="hero-content">

    <!-- Logo badge -->
    <div class="logo-badge">
      <span class="logo-text">PAINTOBER</span>
    </div>

    <!-- Headline -->
    <h1 class="headline">
      Turn Any Photo Into a<br>
      <span class="headline--accent">Paint-by-Numbers</span> Masterpiece
    </h1>

    <!-- Subheading -->
    <p class="subheading">
      Upload your favourite photos and transform them into fun, printable
      paint-by-numbers templates. Perfect for events, parties, and creative gatherings.
    </p>

    <!-- Primary CTA -->
    <RouterLink to="/studio" class="cta-link">
      <button class="cta-btn">Upload Your Photo →</button>
    </RouterLink>

    <!-- Before / After mockup -->
    <div class="mockup-row">
      <div class="mockup-card mockup-card--before">
        <div class="mockup-card__inner mockup-card__inner--before" />
        <span class="mockup-badge mockup-badge--indigo">BEFORE</span>
      </div>

      <span class="mockup-arrow">→</span>

      <div class="mockup-card mockup-card--after">
        <div class="mockup-card__inner mockup-card__inner--after">
          <div
            v-for="n in 16"
            :key="n"
            class="mockup-swatch"
            :style="{ backgroundColor: swatchColors[(n - 1) % swatchColors.length] }"
          />
        </div>
        <span class="mockup-badge mockup-badge--lime">AFTER</span>
      </div>
    </div>

  </div>
</template>

<script>
// Swatch colours used purely for the illustrative Before/After mockup grid
const swatchColors = ['#FF6B9D', '#8D7EFF', '#CFFF04', '#B87EEE']
</script>

<style scoped>
/* ── Layout wrapper ─────────────────────────────────────────── */
.hero-content {
  position: relative;
  z-index: var(--z-content);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--space-lg);
  padding: var(--space-2xl) var(--space-xl);
  width: 100%;
}

/* ── Logo badge ─────────────────────────────────────────────── */
.logo-badge {
  display: inline-block;
  padding: var(--space-sm) var(--space-xl);
  background-color: var(--color-indigo);
  border: var(--border-sticker-snow);
  box-shadow: var(--shadow-sticker-lg);
  clip-path: var(--clip-octagon);
}

.logo-text {
  font-family: var(--font-display);
  font-size: var(--text-hero);
  font-weight: var(--weight-black);
  color: var(--color-snow);
  text-shadow: 4px 4px 0 var(--color-midnight);
  letter-spacing: 0.05em;
}

/* ── Headline ───────────────────────────────────────────────── */
.headline {
  font-family: var(--font-display);
  font-size: var(--text-hero);
  font-weight: var(--weight-extrabold);
  color: var(--color-snow);
  line-height: var(--leading-tight);
  text-shadow: 3px 3px 0 var(--color-midnight);
  max-width: 52rem;
}

.headline--accent {
  color: var(--color-lime);
}

/* ── Subheading ─────────────────────────────────────────────── */
.subheading {
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-medium);
  color: var(--color-snow);
  line-height: var(--leading-normal);
  max-width: 38rem;
}

/* ── CTA ────────────────────────────────────────────────────── */
.cta-link {
  text-decoration: none;
}

.cta-btn {
  padding: var(--space-lg) var(--space-2xl);
  background-color: var(--color-lime);
  border: 4px solid var(--color-bg);
  box-shadow: var(--shadow-sticker-lg);
  border-radius: var(--radius-button);
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-extrabold);
  color: var(--color-bg);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.cta-btn:hover  { transform: scale(1.05); }
.cta-btn:active { transform: scale(0.95); }

/* ── Before / After mockup ──────────────────────────────────── */
.mockup-row {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
  margin-top: var(--space-xl);
  flex-wrap: wrap;
  justify-content: center;
}

.mockup-card {
  position: relative;
  padding: var(--space-lg);
  background-color: var(--color-snow);
  border-radius: var(--radius-card);
  width: 200px;
  height: 200px;
}

.mockup-card--before {
  border: var(--border-sticker-indigo);
  box-shadow: var(--shadow-sticker-md);
  transform: rotate(-3deg);
}

.mockup-card--after {
  border: var(--border-sticker-lime);
  box-shadow: var(--shadow-sticker-lg);
  transform: rotate(2deg);
}

.mockup-card__inner {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-sm);
}

.mockup-card__inner--before {
  background: linear-gradient(135deg, #f9a8d4, #d8b4fe);
}

.mockup-card__inner--after {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-xs);
  padding: var(--space-xs);
  background-color: white;
}

.mockup-swatch {
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-bg);
}

.mockup-badge {
  position: absolute;
  top: -0.75rem;
  left: 50%;
  transform: translateX(-50%);
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--radius-badge);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
}

.mockup-badge--indigo {
  background-color: var(--color-indigo);
  border: 2px solid var(--color-snow);
  box-shadow: var(--shadow-sticker-sm-dark);
  color: var(--color-snow);
}

.mockup-badge--lime {
  background-color: var(--color-lime);
  border: 2px solid var(--color-bg);
  box-shadow: var(--shadow-sticker-sm-dark);
  color: var(--color-bg);
}

.mockup-arrow {
  font-family: var(--font-display);
  font-size: 3.5rem;
  font-weight: var(--weight-black);
  color: var(--color-lime);
  text-shadow: 3px 3px 0 var(--color-midnight);
  line-height: 1;
}
</style>
