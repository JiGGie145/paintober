import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './assets/main.css'
import App from './App.vue'
import { initCsrf } from './api/jobs.js'

import HomeView from './views/HomeView.vue'
import StudioView from './views/StudioView.vue'
import EventJoinView from './views/EventJoinView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import OrganizerHomeView from './views/OrganizerHomeView.vue'
import EventCreateView from './views/EventCreateView.vue'
import OrganizerEventView from './views/OrganizerEventView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',                    name: 'home',   component: HomeView },
    { path: '/studio/:jobId?',      name: 'studio', component: StudioView },
    { path: '/join/:eventToken',    name: 'event-join', component: EventJoinView },
    { path: '/login',               name: 'login', component: LoginView },
    { path: '/register',            name: 'register', component: RegisterView },
    { path: '/organizer',           name: 'organizer-home', component: OrganizerHomeView },
    { path: '/organizer/events/new', name: 'event-create', component: EventCreateView },
    { path: '/organizer/events/:eventId', name: 'organizer-event', component: OrganizerEventView },
  ],
})

const pinia = createPinia()

initCsrf().finally(() => {
  createApp(App)
    .use(router)
    .use(pinia)
    .mount('#app')
})
