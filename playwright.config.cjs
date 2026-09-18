const {defineConfig} = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/browser',
  fullyParallel: true,
  workers: 2,
  use: {
    locale: 'fr-CA',
    headless: true,
    viewport: {width:1280, height:900},
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {browserName:'chromium', launchOptions:{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}},
    },
    // PDF generation is a Chromium API; print styles and events run in every engine.
    {name:'firefox', use:{browserName:'firefox'}, grepInvert:/@pdf/},
    {name:'webkit', use:{browserName:'webkit'}, grepInvert:/@pdf/},
  ],
});
