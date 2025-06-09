import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: 'index.html',
        historyRecorder: 'src/contentScripts/historyRecorder.ts',
      },
      output: {
        entryFileNames: chunk =>
          chunk.name === 'historyRecorder'
            ? 'contentScripts/[name].js'
            : '[name].js',
      },
    },
  },
})
