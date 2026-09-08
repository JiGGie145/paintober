<script setup>
const props = defineProps({
  style: {
    type: String,
    required: true,
  },
  canUseCartoonish: {
    type: Boolean,
    default: false,
  },
  cartoonishDisabledReason: {
    type: String,
    default: 'Only registered event hosts with credits can use this feature.',
  },
})

const emit = defineEmits(['update:style'])

const styles = [
  {
    id: 'realistic',
    title: 'Realistic',
    body: 'Keep the photo details and create a paint-by-numbers kit.',
  },
  {
    id: 'cartoonish',
    title: 'Cartoonish',
    body: 'Turn the photo into clean outline art for coloring.',
  },
]
</script>

<template>
  <section class="style-selector" aria-labelledby="style-selector-title">
    <div class="style-selector__heading">
      <h2 id="style-selector-title">Choose a style</h2>
      <p>Pick the look for your finished kit.</p>
    </div>

    <div class="style-selector__options" role="radiogroup" aria-label="Image style">
      <button
        v-for="option in styles"
        :key="option.id"
        class="style-option"
        :class="{ 'style-option--active': props.style === option.id, 'style-option--disabled': option.id === 'cartoonish' && !props.canUseCartoonish }"
        role="radio"
        :aria-checked="props.style === option.id"
        :disabled="option.id === 'cartoonish' && !props.canUseCartoonish"
        :title="option.id === 'cartoonish' && !props.canUseCartoonish ? props.cartoonishDisabledReason : undefined"
        type="button"
        @click="option.id !== 'cartoonish' || props.canUseCartoonish ? emit('update:style', option.id) : null"
      >
        <span class="style-option__title">{{ option.title }}</span>
        <span class="style-option__body">{{ option.body }}</span>
      </button>
    </div>
  </section>
</template>

<style scoped>
.style-selector {
  max-width: 620px;
  width: 100%;
  margin: 0 auto;
  display: grid;
  gap: var(--space-md);
}

.style-selector__heading h2 {
  margin: 0;
  color: var(--color-snow);
  font-family: var(--font-display);
  font-size: var(--text-subheading);
}

.style-selector__heading p {
  margin: var(--space-xs) 0 0;
  color: var(--color-lavender);
  font-size: var(--text-sm);
}

.style-selector__options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-md);
}

.style-option {
  min-height: 112px;
  padding: var(--space-md);
  display: grid;
  align-content: center;
  gap: var(--space-xs);
  text-align: left;
  background: color-mix(in srgb, var(--color-snow) 8%, transparent);
  border: var(--border-sticker-indigo);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-sticker-sm);
  color: var(--color-snow);
  cursor: pointer;
  transition: transform var(--transition-fast), background-color var(--transition-fast);
}

.style-option:hover {
  transform: translateY(-2px);
}

.style-option--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.style-option--disabled:hover {
  transform: none;
}

.style-option--active {
  background: var(--color-indigo);
  border-color: var(--color-lime);
  box-shadow: var(--shadow-sticker-md);
}

.style-option__title {
  font-family: var(--font-display);
  font-size: var(--text-body);
  font-weight: var(--weight-bold);
}

.style-option__body {
  color: var(--color-lavender);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

.style-option--active .style-option__body {
  color: var(--color-snow);
}

@media (max-width: 600px) {
  .style-selector__options {
    grid-template-columns: 1fr;
  }
}
</style>
