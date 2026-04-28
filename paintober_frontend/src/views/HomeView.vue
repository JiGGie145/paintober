<script setup>
import HeroSection from '../components/hero/HeroSection.vue'
import { RouterLink } from 'vue-router'

const steps = [
  {
    number: '1',
    title: 'Upload',
    body: 'Choose your favourite photo from your device.',
    borderColor: 'var(--color-indigo)',
    badgeColor: 'var(--color-indigo)',
    badgeText: 'var(--color-snow)',
    rotate: '-2deg',
  },
  {
    number: '2',
    title: 'Customize',
    body: 'Adjust colours, complexity, and style settings.',
    borderColor: 'var(--color-lavender)',
    badgeColor: 'var(--color-lavender)',
    badgeText: 'var(--color-snow)',
    rotate: '1deg',
  },
  {
    number: '3',
    title: 'Download',
    body: 'Get your printable paint-by-numbers kit as PNG or ZIP.',
    borderColor: 'var(--color-lime)',
    badgeColor: 'var(--color-lime)',
    badgeText: 'var(--color-bg)',
    rotate: '-1deg',
  },
]

const features = [
  '🎨 Custom party activities',
  '🎉 Wedding favours & keepsakes',
  '👶 Baby shower entertainment',
  '🎂 Birthday party crafts',
  '💼 Team building exercises',
  '🏫 Classroom activities',
]
</script>

<template>
  <!-- ── Hero ───────────────────────────────────────────────── -->
  <HeroSection />

  <!-- ── How It Works ───────────────────────────────────────── -->
  <section class="section how-it-works">
    <h2 class="section-heading">How It Works</h2>
    <div class="steps-grid">
      <div
        v-for="step in steps"
        :key="step.number"
        class="step-card"
        :style="{
          borderColor: step.borderColor,
          transform: `rotate(${step.rotate})`,
        }"
      >
        <div
          class="step-number"
          :style="{
            backgroundColor: step.badgeColor,
            color: step.badgeText,
          }"
        >
          {{ step.number }}
        </div>
        <h3 class="step-title">{{ step.title }}</h3>
        <p class="step-body">{{ step.body }}</p>
      </div>
    </div>
  </section>

  <!-- ── Perfect for Event Hosts ────────────────────────────── -->
  <section class="section for-hosts">
    <h2 class="section-heading section-heading--dark">Perfect for Event Hosts</h2>
    <div class="features-grid">
      <div
        v-for="feature in features"
        :key="feature"
        class="feature-tag"
      >
        {{ feature }}
      </div>
    </div>
  </section>

  <!-- ── Final CTA ──────────────────────────────────────────── -->
  <section class="section cta-section">
    <h2 class="section-heading">Ready to Create?</h2>
    <RouterLink to="/studio" class="cta-link">
      <button class="cta-btn">Get Started Now →</button>
    </RouterLink>
  </section>
</template>

<style scoped>
/* ── Shared section layout ──────────────────────────────────── */
.section {
  padding: var(--space-2xl) var(--space-xl);
}

.section-heading {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: var(--weight-extrabold);
  color: var(--color-snow);
  text-shadow: 3px 3px 0 var(--color-midnight);
  text-align: center;
  margin-bottom: var(--space-2xl);
}

.section-heading--dark {
  text-shadow: 3px 3px 0 var(--color-bg);
}

/* ── How It Works ───────────────────────────────────────────── */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-xl);
  max-width: 72rem;
  margin: 0 auto;
}

.step-card {
  position: relative;
  padding: var(--space-xl);
  background-color: var(--color-snow);
  border-width: var(--border-width-sticker);
  border-style: solid;
  box-shadow: var(--shadow-sticker-md);
  border-radius: var(--radius-card);
}

.step-number {
  position: absolute;
  top: -1.25rem;
  left: -1.25rem;
  width: 3rem;
  height: 3rem;
  border-radius: var(--radius-circle);
  border: 3px solid var(--color-bg);
  box-shadow: var(--shadow-sticker-sm-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-black);
}

.step-title {
  font-family: var(--font-display);
  font-size: var(--text-subheading);
  font-weight: var(--weight-bold);
  color: var(--color-bg);
  margin-bottom: var(--space-sm);
}

.step-body {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-bg);
  line-height: var(--leading-normal);
}

/* ── For Hosts ──────────────────────────────────────────────── */
.for-hosts {
  background-color: var(--color-midnight);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-md);
  max-width: 56rem;
  margin: 0 auto;
}

.feature-tag {
  padding: var(--space-md) var(--space-lg);
  background-color: var(--color-snow);
  border: var(--border-sticker-indigo);
  box-shadow: 3px 3px 0 0 var(--color-bg);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
  color: var(--color-bg);
}

/* ── Final CTA ──────────────────────────────────────────────── */
.cta-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xl);
}

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
</style>
