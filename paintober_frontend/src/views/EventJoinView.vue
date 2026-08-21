<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventContextStore } from '../stores/eventContextStore.js'

const route = useRoute()
const router = useRouter()
const eventContext = useEventContextStore()
const phoneNumber = ref('')
const errorMessage = ref('')

onMounted(async () => {
  eventContext.clear()
  try { await eventContext.resolve(route.params.eventToken) } catch { errorMessage.value = 'This event link is unavailable.' }
})

async function enter() {
  errorMessage.value = ''
  try { await eventContext.enter(phoneNumber.value); router.push({ name: 'studio' }) } catch (error) { errorMessage.value = error.data?.detail ?? 'We could not enter this event.' }
}
</script>

<template>
  <section class="event-page">
    <div v-if="eventContext.loading && !eventContext.event" class="event-page__state">Loading event...</div>
    <div v-else-if="errorMessage && !eventContext.event" class="event-page__state event-page__state--error">
      <h1>Event unavailable</h1><p>{{ errorMessage }}</p><RouterLink class="event-page__link" to="/">Return home</RouterLink>
    </div>
    <div v-else-if="eventContext.event" class="event-page__content">
      <p class="eyebrow">YOU'RE INVITED</p>
      <h1>{{ eventContext.event.name }}</h1>
      <p class="event-page__date">{{ eventContext.event.event_date }}</p>
      <p class="event-page__intro">Bring a favourite photo and turn it into a paint-by-numbers kit for this event.</p>
      <form class="event-form" @submit.prevent="enter">
        <label for="phone">Mobile number</label>
        <input id="phone" v-model="phoneNumber" type="tel" autocomplete="tel" placeholder="+27 82 123 4567" required />
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
        <button class="primary-button" :disabled="eventContext.loading">{{ eventContext.loading ? 'Entering...' : 'Enter event' }}</button>
      </form>
    </div>
  </section>
</template>

<style scoped>
.event-page { min-height: calc(100dvh - 80px); display: grid; place-items: center; padding: var(--space-xl) var(--space-md); }
.event-page__content, .event-page__state { width: min(560px, 100%); animation: fade-in 300ms ease both; }
.event-page__content { padding: clamp(28px, 6vw, 64px); border: var(--border-sticker-indigo); box-shadow: var(--shadow-sticker-lg); background: var(--color-midnight); }
.eyebrow { color: var(--color-lime); font-size: var(--text-sm); font-weight: var(--weight-bold); letter-spacing: 0.12em; }
h1 { margin: var(--space-md) 0 var(--space-sm); font-size: clamp(2.4rem, 7vw, 4.8rem); color: var(--color-snow); }
.event-page__date, .event-page__intro { color: var(--color-snow); }
.event-page__intro { margin-top: var(--space-lg); font-size: var(--text-body); }
.event-form { display: grid; gap: var(--space-sm); margin-top: var(--space-xl); }
label { color: var(--color-lime); font-weight: var(--weight-bold); }
input { min-height: 52px; padding: 0 var(--space-md); border: var(--border-sticker-snow); border-radius: var(--radius-sm); background: var(--color-snow); color: var(--color-bg); font-size: var(--text-body); }
.primary-button { min-height: 54px; margin-top: var(--space-sm); background: var(--color-lime); color: var(--color-bg); border: var(--border-sticker-bg); box-shadow: var(--shadow-sticker-sm); border-radius: var(--radius-button); font-weight: var(--weight-extrabold); font-size: var(--text-body); }
.primary-button:disabled { opacity: 0.6; cursor: wait; }
.form-error, .event-page__state--error p { color: var(--color-pink); }
.event-page__state h1 { color: var(--color-pink); }
.event-page__link { display: inline-block; margin-top: var(--space-lg); color: var(--color-lime); font-weight: var(--weight-bold); }
</style>