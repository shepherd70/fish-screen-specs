const {defineConfig} = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests/browser',
  fullyParallel: true,
  workers: 2,
  use: {browserName:'chromium', locale:'fr-CA', headless:true, launchOptions:{executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE}, viewport:{width:1280,height:900}},
});
