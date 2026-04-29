import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'https://66-228-41-226.ip.linodeusercontent.com',
        changeOrigin: true,
      },
    },
  },
})
