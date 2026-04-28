import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './assets/main.css'
import App from './App.vue'

import HomeView from './views/HomeView.vue'
import StudioView from './views/StudioView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',                    name: 'home',   component: HomeView },
    { path: '/studio/:jobId?',      name: 'studio', component: StudioView },
  ],
})

const pinia = createPinia()

createApp(App)
  .use(router)
  .use(pinia)
  .mount('#app')
