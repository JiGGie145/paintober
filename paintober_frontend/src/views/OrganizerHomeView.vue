<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getCreditBalance, listOrganizerEvents } from '../api/events.js'
import { useAuthStore } from '../stores/authStore.js'
const router = useRouter(); const auth = useAuthStore(); const events = ref([]); const totalCredits = ref(0); const allocatedCredits = ref(0); const availableCredits = ref(0); const errorMessage = ref('')
onMounted(async () => { if (!auth.hydrated) await auth.hydrate(); if (!auth.isAuthenticated) return router.replace({ name: 'login' }); try { const [eventList, balance] = await Promise.all([listOrganizerEvents(), getCreditBalance()]); events.value = eventList; totalCredits.value = balance.total_credits; allocatedCredits.value = balance.allocated_credits; availableCredits.value = balance.available_credits } catch { errorMessage.value = 'Could not load your organizer dashboard.' } })
async function signOut() { await auth.signOut(); router.push({ name: 'home' }) }
</script>
<template>
    <section class="organizer-page">
        <div class="organizer-page__top">
            <div>
                <p class="eyebrow">ORGANIZER DESK</p>
                <h1>Hello{{ auth.organizer?.first_name ? `, ${auth.organizer.first_name}` : '' }}.</h1>
            </div><button class="quiet-button" @click="signOut">Sign out</button>
        </div>
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
        <div class="stats">
            <div class="stat"><span>Total credits</span><strong>{{ totalCredits }}</strong><small>Credits in your account, including those assigned to events.</small></div>
            <div class="stat"><span>Assigned to events</span><strong>{{ allocatedCredits }}</strong><small>Credits currently set aside across all your events.</small></div>
            <div class="stat stat--available"><span>Free to allocate</span><strong>{{ availableCredits }}</strong><small>Credits still available for new events.</small></div>
        </div>
        <div class="section-heading">
            <h2>Your events</h2><button class="primary-button" @click="router.push({ name: 'event-create' })">New event
                +</button>
        </div>
        <div v-if="events.length" class="event-list">
            <RouterLink v-for="event in events" :key="event.id"
                :to="{ name: 'organizer-event', params: { eventId: event.id } }" class="event-item">
                <div>
                    <h3>{{ event.name }}</h3>
                    <p>{{ event.event_date }} · {{ event.status }}</p>
                </div><span>View →</span>
            </RouterLink>
        </div>
        <div v-else class="empty-state">
            <p>No events yet.</p><button class="text-link" @click="router.push({ name: 'event-create' })">Create your
                first event</button>
        </div>
    </section>
</template>
<style scoped>
.organizer-page {
    width: min(1040px, calc(100% - 32px));
    margin: 0 auto;
    padding: var(--space-xl) 0;
}

.organizer-page__top,
.section-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: var(--space-md);
}

.eyebrow {
    color: var(--color-lime);
    font-size: var(--text-sm);
    font-weight: var(--weight-bold);
    letter-spacing: .12em;
}

.organizer-page h1 {
    margin: var(--space-sm) 0 var(--space-xl);
    font-size: clamp(2.8rem, 8vw, 5rem);
}

.organizer-page h2 {
    font-size: var(--text-subheading);
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-md);
    margin-bottom: var(--space-2xl);
}

.stat {
    padding: var(--space-lg);
    border: var(--border-sticker-indigo);
    background: var(--color-midnight);
    box-shadow: var(--shadow-sticker-md);
}

.stat span {
    display: block;
    color: var(--color-snow);
}

.stat strong {
    display: block;
    margin-top: var(--space-sm);
    color: var(--color-lime);
    font-size: 2.6rem;
}

.stat small {
    display: block;
    max-width: 24ch;
    margin-top: var(--space-sm);
    color: var(--color-lavender);
    line-height: 1.35;
}

.stat--available {
    border-color: var(--color-lime);
}

.primary-button,
.quiet-button {
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-button);
    font-weight: var(--weight-bold);
}

.primary-button {
    background: var(--color-lime);
    color: var(--color-bg);
    border: var(--border-sticker-bg);
    box-shadow: var(--shadow-sticker-sm);
}

.quiet-button {
    color: var(--color-snow);
    border: var(--border-sticker-snow);
}

.event-list {
    display: grid;
    gap: var(--space-md);
    margin-top: var(--space-lg);
}

.event-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-md);
    padding: var(--space-lg);
    background: var(--color-snow);
    color: var(--color-bg);
    border-left: 8px solid var(--color-indigo);
    box-shadow: var(--shadow-sticker-sm);
}

.event-item h3 {
    font-size: 1.35rem;
}

.event-item p {
    margin-top: var(--space-xs);
}

.event-item span {
    color: var(--color-midnight);
    font-weight: var(--weight-bold);
}

.empty-state {
    padding: var(--space-xl) 0;
    color: var(--color-snow);
}

.text-link {
    margin-top: var(--space-sm);
    color: var(--color-lime);
    text-decoration: underline;
}

.form-error {
    color: var(--color-pink);
    margin-bottom: var(--space-md);
}

@media (max-width: 560px) {

    .organizer-page__top,
    .section-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .stats {
        grid-template-columns: 1fr;
    }
}
</style>