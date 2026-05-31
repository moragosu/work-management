import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:8001',
  },
  // API 테스트 전용 — 브라우저 불필요
  projects: [{ name: 'api' }],
})
