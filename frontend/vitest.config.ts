import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'happy-dom',
    include: ['**/*.test.ts'],
    exclude: ['node_modules', '.nuxt', '.output', 'tests/e2e/**'],
    coverage: {
      reporter: ['text', 'lcov'],
      include: ['features/editor/services/**/*.ts'],
    },
  },
})

