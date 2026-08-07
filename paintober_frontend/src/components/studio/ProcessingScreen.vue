<script setup>
import { computed } from 'vue'
import { useJobStore } from '../../stores/jobStore.js'

const jobStore = useJobStore()

const statusText = computed(() =>
  jobStore.status === 'processing'
    ? 'Processing your image…'
    : 'Queued — starting soon…'
)
</script>

<template>
  <div class="processing">
    <!-- Spinning ring -->
    <!-- <div class="processing__ring" aria-hidden="true"> -->
      <!-- <div class="processing__spinner" /> -->
    <!-- </div> -->
    
    <!-- Status text -->
    <p class="processing__heading">Generating your paint-by-numbers kit</p>
    <p class="processing__status">{{ statusText }}</p>
    
    <!-- Loading Animation -->
    <span class="loader"></span>

    <!-- Job ID -->
    <p class="processing__id">Job ID: {{ jobStore.id }}</p>

    <!-- Decorative step hints -->
    <div class="processing__steps">
      <div class="processing__step">
        <span class="processing__step-dot processing__step-dot--done" />
        Uploaded
      </div>
      <div class="processing__step-divider" />
      <div class="processing__step">
        <span class="processing__step-dot processing__step-dot--active" />
        Processing
      </div>
      <div class="processing__step-divider" />
      <div class="processing__step">
        <span class="processing__step-dot" />
        Ready
      </div>
    </div>
  </div>
</template>

<style scoped>
.processing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  min-height: 70vh;
  padding: var(--space-2xl);
  text-align: center;
}

/* ── Ring ───────────────────────────────────────────────────── */
.processing__ring {
  position: relative;
  width: 96px;
  height: 96px;
}

.processing__spinner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 6px solid color-mix(in srgb, var(--color-indigo) 30%, transparent);
  border-top-color: var(--color-lime);
  animation: spin 1s linear infinite;
}

/* ── Text ───────────────────────────────────────────────────── */
.processing__heading {
  font-family: var(--font-display);
  font-size: var(--text-heading);
  font-weight: var(--weight-bold);
  color: var(--color-snow);
  max-width: 480px;
}

.processing__status {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-lavender);
}

.processing__id {
  font-family: var(--font-body);
  font-size: var(--text-small);
  color: color-mix(in srgb, var(--color-snow) 40%, transparent);
  letter-spacing: 0.05em;
}

/* ── Steps ──────────────────────────────────────────────────── */
.processing__steps {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-md);
}

.processing__step {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: var(--weight-bold);
  color: var(--color-lavender);
}

.processing__step-divider {
  width: 32px;
  height: 2px;
  background-color: color-mix(in srgb, var(--color-lavender) 40%, transparent);
}

.processing__step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: color-mix(in srgb, var(--color-lavender) 40%, transparent);
  border: 2px solid var(--color-lavender);
  flex-shrink: 0;
}

.processing__step-dot--done {
  background-color: var(--color-lime);
  border-color: var(--color-lime);
}

.processing__step-dot--active {
  background-color: transparent;
  border-color: var(--color-lime);
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-lime) 60%, transparent); }
  50%       { box-shadow: 0 0 0 6px transparent; }
}

/* Loading ANIMATION */


.loader {
    position: relative;
    width: 120px;
    height: 14px;
    border-radius: 0 0 15px 15px;
    background-color: #3e494d;
    box-shadow: 0 -1px 4px #5d6063 inset;
    animation: panex 0.5s linear alternate infinite;
    transform-origin: 170px 0;
    z-index: 10;
    perspective: 300px;
    margin: 50px 0 50px 0;

}
.loader::before {
  content: '';
  position: absolute;
  left: calc( 100% - 2px);
  top: 0;
  z-index: -2;
  height: 10px;
  width: 70px;
  border-radius: 0 4px 4px 0;
  background-repeat: no-repeat;
  background-image: linear-gradient(#6c4924, #4b2d21), linear-gradient(#4d5457 24px, transparent 0), linear-gradient(#9f9e9e 24px, transparent 0);
  background-size: 50px 10px , 4px 8px , 24px 4px;
  background-position: right center , 17px center , 0px center;
}
  .loader::after {
    content: '';
    position: absolute;
    left: 50%;
    top: 0;
    z-index: -2;
    transform: translate(-50% , -20px) rotate3d(75, -2, 3, 78deg);
    width: 55px;
    height: 53px;
    background: #fff;
    background-image:
    radial-gradient(circle 3px , #fff6 90%, transparent 10%),
    radial-gradient(circle 12px , #ffc400 90%, transparent 10%),
    radial-gradient(circle 12px , #ffae00 100%, transparent 0);
    background-repeat: no-repeat;
    background-position: -4px -6px , -2px -2px , -1px -1px;
    box-shadow: -2px -3px #0002 inset, 0 0 4px #0003 inset;
    border-radius: 47% 36% 50% 50% / 49% 45% 42% 44%;
    animation: eggRst 1s ease-out infinite;
  }

@keyframes eggRst {
  0% ,  100%{  transform: translate(-50%, -20px) rotate3d(90, 0, 0, 90deg); opacity: 0; }
  10% , 90% {  transform: translate(-50%, -30px) rotate3d(90, 0, 0, 90deg); opacity: 1; }
  25%  {transform:  translate(-50% , -40px) rotate3d(85, 17, 2, 70deg) }
  75% {transform:  translate(-50% , -40px) rotate3d(75, -3, 2, 70deg) }
  50% {transform:  translate(-55% , -50px) rotate3d(75, -8, 3, 50deg) }
}
@keyframes panex {
  0%{  transform: rotate(-5deg)  }
  100%{  transform: rotate(10deg)  }
}
  
</style>
