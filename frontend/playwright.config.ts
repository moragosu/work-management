import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  reporter: 'list',
  projects: [
    {
      name: 'api',
      testMatch: 'api.spec.ts',
      use: { baseURL: 'http://localhost:8001' },
    },
    {
      name: 'absorb-promote',
      testMatch: 'absorb-promote.spec.ts',
      use: { baseURL: 'http://localhost:8001' },
    },
    {
      name: 'okr',
      testMatch: 'okr_tab_test.spec.ts',
      use: {
        baseURL: 'http://localhost:5174',
        browserName: 'chromium',
        headless: true,
        viewport: { width: 1280, height: 800 },
        launchOptions: {
          executablePath: '/home/chanje/.cache/ms-playwright/chromium-1148/chrome-linux/chrome',
        },
      },
    },
    {
      name: 'ui',
      testMatch: 'ui.spec.ts',
      use: {
        baseURL: 'http://localhost:5174',
        browserName: 'chromium',
        headless: true,
        viewport: { width: 1280, height: 800 },
        launchOptions: {
          executablePath: '/home/chanje/.cache/ms-playwright/chromium-1148/chrome-linux/chrome',
        },
      },
    },
  ],
})
