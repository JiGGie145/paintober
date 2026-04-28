<!--
  HeroBackground.vue
  ─────────────────────────────────────────────────────────────
  PURPOSE: purely decorative background layer for the hero section.

  RULES (enforced by architecture):
  • position: absolute — fills parent HeroSection entirely
  • z-index: var(--z-background) — always behind HeroContent
  • pointer-events: none — never intercepts user interaction
  • NO text nodes of any kind
  • NO layout logic (no flex/grid to position content)
  • Only: shapes, colours, animations
  ─────────────────────────────────────────────────────────────
-->
<template>
  <div class="hero-bg" aria-hidden="true">

    <!-- 🎨 Palette — lime — top left -->
    <div class="icon-badge icon--palette icon--lime icon--lg">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/>
        <circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/>
        <circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/>
        <circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/>
        <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>
      </svg>
    </div>

    <!-- 🖌️ Paintbrush — indigo — top right -->
    <div class="icon-badge icon--brush icon--indigo icon--md">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18.37 2.63 14 7l-1.59-1.59a2 2 0 0 0-2.82 0L8 7l9 9 1.59-1.59a2 2 0 0 0 0-2.82L17 10l4.37-4.37a2.12 2.12 0 1 0-3-3z"/>
        <path d="M9 8c-2 3-4 3.5-7 4l8 8c1-.5 3.5-2 4-7"/>
        <path d="M14.5 17.5 4.5 15"/>
      </svg>
    </div>

    <!-- ✨ Sparkles — pink — top center-right -->
    <div class="icon-badge icon--sparkles icon--pink icon--sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
        <path d="M20 3v4"/>
        <path d="M22 5h-4"/>
        <path d="M4 17v2"/>
        <path d="M5 18H3"/>
      </svg>
    </div>

    <!-- 🖼️ Image frame — lavender — bottom left -->
    <div class="icon-badge icon--image icon--lavender icon--lg">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect width="18" height="18" x="3" y="3" rx="2" ry="2"/>
        <circle cx="9" cy="9" r="2"/>
        <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
      </svg>
    </div>

    <!-- 🪄 Wand — lime — left middle -->
    <div class="icon-badge icon--wand icon--lime icon--sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M15 4V2"/>
        <path d="M15 16v-2"/>
        <path d="M8 9h2"/>
        <path d="M20 9h2"/>
        <path d="M17.8 11.8 19 13"/>
        <path d="M15 9h.01"/>
        <path d="M17.8 6.2 19 5"/>
        <path d="m3 21 9-9"/>
        <path d="M12.2 6.2 11 5"/>
      </svg>
    </div>

    <!-- ✂️ Scissors — indigo — bottom right -->
    <div class="icon-badge icon--scissors icon--indigo icon--md">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="6" cy="6" r="3"/>
        <path d="M8.12 8.12 12 12"/>
        <path d="M20 4 8.12 15.88"/>
        <circle cx="6" cy="18" r="3"/>
        <path d="M14.8 14.8 20 20"/>
      </svg>
    </div>

    <!-- 📌 Pushpin — pink — bottom center -->
    <div class="icon-badge icon--pin icon--pink icon--lg">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" x2="12" y1="17" y2="22"/>
        <path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24z"/>
      </svg>
    </div>

    <!-- 🌟 Star/Pencil — lavender — top far right -->
    <div class="icon-badge icon--pencil icon--lavender icon--sm">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
        <path d="m15 5 4 4"/>
      </svg>
    </div>

  </div>
</template>

<style scoped>
/* ── Container ──────────────────────────────────────────────── */
.hero-bg {
  position: absolute;
  inset: 0;
  z-index: var(--z-background);
  pointer-events: none;
  overflow: hidden;
}

/* ── Shared icon badge base ─────────────────────────────────── */
.icon-badge {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-circle);
  border-width: var(--border-width-sticker);
  border-style: solid;
  border-color: var(--color-snow);
  box-shadow: var(--shadow-sticker-sm);
}

.icon-badge svg {
  display: block;
}

/* ── Sizes ──────────────────────────────────────────────────── */
.icon--sm  { width: 52px;  height: 52px; }
.icon--sm svg { width: 24px; height: 24px; }

.icon--md  { width: 64px;  height: 64px; }
.icon--md svg { width: 30px; height: 30px; }

.icon--lg  { width: 76px;  height: 76px; }
.icon--lg svg { width: 36px; height: 36px; }

/* ── Colour schemes ─────────────────────────────────────────── */
.icon--lime {
  background-color: var(--color-lime);
  color: var(--color-bg);
}

.icon--indigo {
  background-color: var(--color-indigo);
  color: var(--color-snow);
}

.icon--pink {
  background-color: var(--color-pink);
  color: var(--color-snow);
}

.icon--lavender {
  background-color: var(--color-lavender);
  color: var(--color-snow);
}

/* ── Positions + animations ─────────────────────────────────── */

/* Palette — top left */
.icon--palette {
  top: 6rem;
  left: 8%;
  animation: float 6s ease-in-out 0s infinite;
}

/* Paintbrush — top right */
.icon--brush {
  top: 9rem;
  right: 12%;
  animation: float 8s ease-in-out 0.5s infinite;
}

/* Sparkles — top center-right */
.icon--sparkles {
  top: 3.5rem;
  right: 30%;
  animation: float 7s ease-in-out 1s infinite;
}

/* Image frame — bottom left */
.icon--image {
  bottom: 9rem;
  left: 16%;
  animation: float 9s ease-in-out 1.5s infinite;
}

/* Wand — left middle */
.icon--wand {
  top: 45%;
  left: 3%;
  animation: float 6.5s ease-in-out 2s infinite;
}

/* Scissors — bottom right */
.icon--scissors {
  bottom: 7rem;
  right: 10%;
  animation: float 7.5s ease-in-out 2.5s infinite;
}

/* Pushpin — bottom center */
.icon--pin {
  bottom: 13rem;
  left: 42%;
  animation: float 8.5s ease-in-out 3s infinite;
}

/* Pencil — top far right */
.icon--pencil {
  top: 18rem;
  right: 4%;
  animation: float 6s ease-in-out 3.5s infinite;
}
</style>
