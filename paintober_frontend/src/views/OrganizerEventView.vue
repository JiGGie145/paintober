<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrganizerEvent, getOrganizerEventKits, updateOrganizerEvent } from '../api/events.js'
import { renameJob } from '../api/jobs.js'
import { useAuthStore } from '../stores/authStore.js'
const route = useRoute(); const router = useRouter(); const auth = useAuthStore(); const event = ref(null); const kits = ref([]); const errorMessage = ref(''); const copied = ref(false); const kitsLoading = ref(false); const kitsError = ref('')
const shareOrigin = window.location.origin
onMounted(async () => { if (!auth.hydrated) await auth.hydrate(); if (!auth.isAuthenticated) return router.replace({ name: 'login' }); try { event.value = await getOrganizerEvent(route.params.eventId); await loadKits() } catch { errorMessage.value = 'Could not load this event.' } })
async function loadKits() { kitsLoading.value = true; kitsError.value = ''; try { kits.value = await getOrganizerEventKits(route.params.eventId) } catch { kitsError.value = 'Could not load event kits.' } finally { kitsLoading.value = false } }
async function renameKit(kit) { const nextName = window.prompt('Kit name (optional)', kit.kit_name ?? ''); if (nextName === null) return; try { await renameJob(kit.id, nextName); kit.kit_name = nextName.trim() || null } catch { kitsError.value = 'Could not rename this kit.' } }
function openKit(kit) { router.push({ name: 'studio', params: { jobId: kit.id } }) }
function formatDate(iso) { if (!iso) return ''; return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }
async function toggleStatus() { const status = event.value.status === 'active' ? 'disabled' : 'active'; if (!window.confirm(`${status === 'disabled' ? 'Disable' : 'Enable'} this event?`)) return; event.value = await updateOrganizerEvent(event.value.id, { status }) }
async function copyLink() { await navigator.clipboard.writeText(`${window.location.origin}/join/${event.value.token}`); copied.value = true; setTimeout(() => { copied.value = false }, 1800) }
</script>
<template>
    <section class="event-detail">
        <RouterLink class="back-link" to="/organizer">← Dashboard</RouterLink>
        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
        <div v-if="event">
            <div class="detail-heading">
                <div>
                    <p class="eyebrow">EVENT CONTROL</p>
                    <h1>{{ event.name }}</h1>
                    <p>{{ event.event_date }} · {{ event.status }}</p>
                </div>
                <div class="heading-actions">
                    <RouterLink class="primary-button" :to="{ name: 'studio', query: { eventId: event.id } }">Create kit
                    </RouterLink><button class="quiet-button" @click="toggleStatus">{{ event.status === 'active' ?
                        'Disable event' : 'Enable event' }}</button>
                </div>
            </div>
            <div class="metrics">
                <div><span>Available</span><strong>{{ event.available_credits }}</strong></div>
                <div><span>Reserved</span><strong>{{ event.reserved_credits }}</strong></div>
                <div><span>Consumed</span><strong>{{ event.consumed_credits }}</strong></div>
                <div><span>Attendees</span><strong>{{ event.attendee_count }}</strong></div>
            </div>
            <div class="share-block">
                <p class="eyebrow-dark">SHARE LINK</p><code>{{ shareOrigin }}/join/{{ event.token }}</code><button
                    class="primary-button" @click="copyLink">{{ copied ? 'Copied' : 'Copy link' }}</button>
            </div>
            <section class="kits-section">
                <div class="kits-heading">
                    <div>
                        <p class="eyebrow">EVENT KITS</p>
                        <h2>Submitted kits</h2>
                    </div><span>{{ kits.length }}</span>
                </div>
                <p v-if="kitsError" class="form-error">{{ kitsError }}</p>
                <p v-else-if="kitsLoading">Loading kits...</p>
                <div v-else class="kit-grid">
                    <article v-for="kit in kits" :key="kit.id" class="kit-card" role="button" tabindex="0"
                        @click="openKit(kit)" @keydown.enter="openKit(kit)" @keydown.space.prevent="openKit(kit)">
                        <div class="kit-thumbnail"><img v-if="kit.thumbnail_url" :src="kit.thumbnail_url" alt="" /><span
                                v-else>{{ kit.status }}</span></div>
                        <div class="kit-card__body"><strong>{{ kit.kit_name || 'Untitled kit' }}</strong><small>{{
                            formatDate(kit.created_at) }}</small>
                            <div class="kit-card__actions">
                                <a v-if="kit.download_url" class="quiet-button"
                                    :href="kit.download_url" download="paintober-kit.zip" aria-label="Download kit"
                                    title="Download kit" @click.stop>⬇️</a>
                                <button class="quiet-button" @click.stop="renameKit(kit)">Rename</button>
                            </div>
                        </div>
                    </article>
                </div>
            </section>
        </div>
    </section>
</template>
<style scoped>
.event-detail {
    width: min(1040px, calc(100% - 32px));
    margin: 0 auto;
    padding: var(--space-xl) 0;
}

.back-link {
    color: var(--color-lime);
    font-weight: var(--weight-bold);
}

.detail-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: var(--space-md);
    margin: var(--space-xl) 0;
}

.heading-actions {
    display: flex;
    gap: var(--space-sm);
    align-items: center;
}

.eyebrow {
    color: var(--color-lime);
    font-size: var(--text-sm);
    font-weight: var(--weight-bold);
    letter-spacing: .12em;
}

.eyebrow-dark {
    color: var(--color-midnight);
    font-size: var(--text-sm);
    font-weight: var(--weight-bold);
    letter-spacing: .12em;
}

.detail-heading h1 {
    margin: var(--space-sm) 0;
    font-size: clamp(2.8rem, 8vw, 5rem);
}

.quiet-button,
.primary-button {
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-button);
    font-weight: var(--weight-bold);
}

.quiet-button {
    color: var(--color-snow);
    border: var(--border-sticker-snow);
}

.primary-button {
    background: var(--color-lime);
    color: var(--color-bg);
    border: var(--border-sticker-bg);
    box-shadow: var(--shadow-sticker-sm);
    text-decoration: none;
}

.metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-md);
}

.metrics>div {
    padding: var(--space-lg);
    background: var(--color-midnight);
    border-top: 6px solid var(--color-indigo);
}

.metrics span {
    color: var(--color-snow);
}

.metrics strong {
    display: block;
    margin-top: var(--space-sm);
    color: var(--color-lime);
    font-size: 2.4rem;
}

.share-block {
    display: grid;
    gap: var(--space-md);
    margin-top: var(--space-2xl);
    padding: var(--space-lg);
    background: var(--color-snow);
    color: var(--color-bg);
}

.share-block code {
    overflow-wrap: anywhere;
}

.kits-section {
    margin-top: var(--space-2xl);
}

.kits-heading {
    display: flex;
    justify-content: space-between;
    align-items: end;
}

.kits-heading h2 {
    margin: var(--space-sm) 0 var(--space-lg);
}

.kits-heading>span {
    color: var(--color-lime);
    font-size: 2rem;
    font-weight: var(--weight-bold);
}

.kit-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-md);
}

.kit-card {
    min-height: 96px;
    height: 96px;
    display: flex;
    align-items: stretch;
    overflow: hidden;
    background: var(--color-midnight);
    border: var(--border-sticker-snow);
    border-radius: var(--radius-card);
    box-shadow: var(--shadow-sticker-sm);
    cursor: pointer;
}

.kit-card:focus-visible {
    outline: 3px solid var(--color-lime);
    outline-offset: 3px;
}

.kit-thumbnail {
    width: 88px;
    height: 100%;
    flex: 0 0 88px;
    display: grid;
    place-items: center;
    background: var(--color-indigo);
    color: var(--color-snow);
    font-size: var(--text-sm);
    text-transform: capitalize;
}

.kit-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.kit-card__body {
    min-width: 0;
    flex: 1;
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-rows: auto auto;
    align-content: center;
    gap: var(--space-xs) var(--space-sm);
    padding: var(--space-sm) var(--space-md);
}

.kit-card__body strong {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--color-snow);
}

.kit-card__body small {
    min-width: 0;
    color: var(--color-lavender);
    white-space: nowrap;
}

.kit-card__body .quiet-button {
    align-self: center;
    padding: var(--space-xs) var(--space-sm);
    font-size: var(--text-sm);
    white-space: nowrap;
}

.kit-card__actions {
    grid-column: 2;
    grid-row: 1 / span 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-xs);
}

.form-error {
    color: var(--color-pink);
}

@media (max-width: 700px) {
    .detail-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .heading-actions {
        flex-wrap: wrap;
    }

    .metrics {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 380px) {
    .kit-grid {
        grid-template-columns: 1fr;
    }

    .kit-card {
        height: 88px;
        min-height: 88px;
    }

    .kit-thumbnail {
        width: 72px;
        flex-basis: 72px;
    }

    .kit-card__body {
        padding-inline: var(--space-sm);
    }

    .kit-card__body .quiet-button {
        padding-inline: var(--space-xs);
    }
}
</style>