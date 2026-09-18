const {test,expect} = require('@playwright/test');
const {pathToFileURL} = require('node:url');
const path = require('node:path');
const fs = require('node:fs');
const url=pathToFileURL(path.resolve('fish-screen-tool.html')).href;

test.beforeEach(async({page})=>{
  page.on('pageerror',error=>{throw error;});
  await page.goto(url);
});

async function checkPrintView(page, testInfo, name, state, value) {
  // emulateMedia alone does not dispatch the browser's print lifecycle events.
  await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
  await page.emulateMedia({media:'print'});
  try {
    await expect(page.locator('#rollup .badge-row')).toContainText(state);
    await expect(page.locator('.print-value').filter({hasText:value})).toBeVisible();
    await expect(page.locator('[data-act=flowVal]').first()).toBeHidden();
    await page.screenshot({path:testInfo.outputPath(`${name}-print.png`),fullPage:true});
  } finally {
    await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
    await page.emulateMedia({media:'screen'});
  }
  await expect(page.locator('[data-act=flowVal]').first()).toBeVisible();
  await expect(page.locator('#rollup .badge-row')).toContainText(state);
}

test('fresh state, confirmation, invalid inputs and live field errors',async({page})=>{
  const card=page.locator('.intake-card');
  await expect(card.getByRole('heading',{name:'Intake 1',exact:true})).toBeVisible();
  await expect(page.locator('#rollup .badge-row')).toContainText('UNASSESSED');
  await card.getByLabel('I have checked').check();
  await expect(page.locator('#rollup .badge-row')).toContainText('SIZING PASS');
  await card.getByLabel('Diverted flow Q').fill('50oops');
  await expect(card.getByLabel('Diverted flow Q')).toHaveAttribute('aria-invalid','true');
  await expect(page.locator('#assessment_status')).toContainText('CHECK INPUTS');
  await card.getByLabel('Diverted flow Q').fill('50');
  await expect(page.locator('#rollup .badge-row')).toContainText('UNASSESSED');
});

test('keyboard focus survives selections, duplicate, remove and undo',async({page})=>{
  const first=page.locator('.intake-card').first();
  const geometry=first.getByLabel('Geometry',{exact:true});
  await geometry.focus();await page.keyboard.press('ArrowUp');
  await expect(geometry).toBeFocused();
  await first.getByRole('button',{name:'Duplicate Intake 1',exact:true}).click();
  const copy=page.locator('.intake-card').nth(1);
  await expect(copy.getByLabel('Rename Intake 1 (copy)',{exact:true})).toBeFocused();
  await copy.getByRole('button',{name:'Remove Intake 1 (copy)',exact:true}).click();
  await expect(first.getByLabel('Rename Intake 1',{exact:true})).toBeFocused();
  await page.getByRole('button',{name:'Undo deletion'}).click();
  await expect(page.locator('.intake-card')).toHaveCount(2);
  await page.getByRole('button',{name:'+ Add intake',exact:true}).click();
  await expect(page.locator('.intake-card').last().locator('[data-act=name]')).toBeFocused();
});

test('flow units convert and SPOT evidence gates the verdict',async({page})=>{
  const card=page.locator('.intake-card');
  await card.getByLabel('Flow units').selectOption('cfs');
  await expect(card.getByLabel('Q (canonical)')).toHaveValue('0.05000');
  await card.getByLabel('Design approach velocity source').selectOption('spot');
  await card.getByLabel('SPOT velocity (m/s)',{exact:true}).fill('0.5');
  await expect(page.locator('#rollup .badge-row')).toContainText('NEEDS REVIEW');
  await page.locator('#site_species').fill('Documented fish group');
  await card.getByLabel('SPOT source / design basis').fill('Calculation reference 17');
  await card.getByLabel('QEP has reviewed').check();
  await card.getByLabel('I have checked').check();
  await expect(page.locator('#rollup .badge-row')).toContainText('SIZING PASS');
});

test('save/download and load preserve checklist; failed load leaves session intact',async({page})=>{
  await page.getByLabel('Project name',{exact:true}).fill('Browser test site');
  await page.locator('[data-check="2"]').check();
  const download=page.waitForEvent('download');
  await page.getByRole('button',{name:'Save site (JSON)',exact:false}).click();
  const saved=JSON.parse(fs.readFileSync(await (await download).path(),'utf8'));
  expect(saved.checklist[2]).toBe(true);
  await page.locator('[data-check="2"]').uncheck();
  page.on('dialog',dialog=>dialog.accept());
  await page.locator('#load_json_file').setInputFiles({name:'site.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))});
  await expect(page.locator('#io_status')).toContainText('Loaded site.json');
  await expect(page.locator('[data-check="2"]')).toBeChecked();
  const broken=structuredClone(saved);broken.site.site_project='Damaged';broken.intakes=[null];
  await page.locator('#load_json_file').setInputFiles({name:'broken.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(broken))});
  await expect(page.locator('#io_status')).toContainText('Load failed');
  await expect(page.getByLabel('Project name',{exact:true})).toHaveValue('Browser test site');
  await expect(page.locator('.intake-card')).toHaveCount(1);
});

test('CSV import reports mixed environments and keeps matching rows',async({page})=>{
  await page.locator('#import_csv_file').setInputFiles({name:'mixed.csv',mimeType:'text/csv',buffer:Buffer.from('name,flow_m3s,water_type\nPond,0.05,waterbody\nRiver,0.05,watercourse')});
  await expect(page.locator('#io_status')).toContainText('Imported 1 intake(s); skipped 1');
  await expect(page.locator('#site_env')).toHaveValue('waterbody');
  await expect(page.locator('.intake-card')).toHaveCount(2);
});

for(const width of [320,390,640]) test(`all controls labelled and mobile content reachable at ${width}px`,async({page},testInfo)=>{
  await page.setViewportSize({width,height:900});
  await page.locator('[data-act=optToggle]').click();
  const issues=await page.evaluate(()=>{
    const inputs=[...document.querySelectorAll('input:not([type=file]),select')];
    return inputs.filter(n=>!n.labels?.length && !n.getAttribute('aria-label')).map(n=>n.outerHTML);
  });
  expect(issues).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  const button=page.getByRole('button',{name:'Duplicate Intake 1',exact:true});
  const bounds=await button.boundingBox();
  expect(bounds.x+bounds.width).toBeLessThanOrEqual(width);
  await page.screenshot({path:testInfo.outputPath(`mobile-${width}.png`),fullPage:true});
});

test('optimizer respects full checks, applies declared changes, and print has readable values',async({page},testInfo)=>{
  await page.locator('#site_env').selectOption('watercourse');
  const card=page.locator('.intake-card');
  await card.getByLabel('Screen-face angle').fill('60');
  await card.locator('[data-act=optToggle]').click();
  await expect(card.locator('[data-act=optApply]')).toBeDisabled();
  await card.getByLabel('Screen-face angle').fill('0');
  await card.locator('[data-act=optApply]').click();
  await expect(card.getByLabel('Diameter D (m)',{exact:true})).toHaveValue('0.3');
  await card.getByLabel('I have checked').check();
  await expect(page.locator('#rollup .badge-row')).toContainText('SIZING PASS');
  await checkPrintView(page,testInfo,'assessed','SIZING PASS',/^50$/);
});

test('product snapshots survive library edits and deletion undo',async({page})=>{
  const card=page.locator('.intake-card');
  await card.locator('[data-act=productIdx]').selectOption('1');
  await page.getByLabel('Product 2 opening_mm',{exact:true}).fill('1.5');
  await expect(card.getByLabel('Opening size (mm)',{exact:true})).toHaveValue('2');
  await expect(card.locator('[data-act=productIdx]')).toHaveValue('-1');
  await page.locator('[data-pdel="1"]').click();
  await expect(page.locator('#product_table [data-pdel]')).toHaveCount(5);
  await page.getByRole('button',{name:'Undo deletion'}).click();
  await expect(page.locator('#product_table [data-pdel]')).toHaveCount(6);
  await expect(page.getByLabel('Product 2 opening_mm',{exact:true})).toHaveValue('1.5');
  await expect(card.getByLabel('Opening size (mm)',{exact:true})).toHaveValue('2');
});

test('200 percent zoom retains reachable actions and SPOT controls',async({page})=>{
  await page.evaluate(()=>{document.body.style.zoom='2';});
  await page.locator('[data-act=velSource]').selectOption('spot');
  await page.locator('[data-act=spotVel]').fill('0.5');
  await expect(page.locator('[data-act=spotReviewed]')).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  const bounds=await page.locator('[data-act=dup]').boundingBox();
  expect(bounds.x+bounds.width).toBeLessThanOrEqual(1280);
});

test('keyboard sizing and save, French locale uses period decimals',async({page})=>{
  const input=page.locator('[data-act=flowVal]');
  await input.focus();await page.keyboard.press('ControlOrMeta+A');await page.keyboard.type('25');
  await page.keyboard.press('Tab');
  await expect(page.locator('[data-act=flowUnit]')).toBeFocused();
  await page.locator('[data-act=assessmentConfirmed]').focus();await page.keyboard.press('Space');
  await expect(page.locator('#rollup .badge-row')).toContainText('SIZING PASS');
  await page.locator('#save_json_btn').focus();
  const saved=page.waitForEvent('download');await page.keyboard.press('Enter');await saved;
  expect(await page.evaluate(()=>fmt(0.035,3))).toBe('0.035');
});

test('default and multi-intake print preserve assessment state and complete values',async({page},testInfo)=>{
  await checkPrintView(page,testInfo,'default','UNASSESSED',/^50$/);
  await page.locator('[data-act=dup]').click();
  await page.locator('.intake-card').first().locator('[data-act=assessmentConfirmed]').check();
  await page.locator('.intake-card').nth(1).locator('[data-act=flowVal]').fill('50oops');
  await checkPrintView(page,testInfo,'multi','CHECK INPUTS',/^50oops$/);
});

test('PDF export exercises native print events for default, assessed and multi-intake reports', {tag:'@pdf'}, async({page},testInfo)=>{
  for (const [name,state] of [['default','UNASSESSED'],['assessed','SIZING PASS'],['multi','CHECK INPUTS']]) {
    if (name==='assessed') await page.locator('[data-act=assessmentConfirmed]').check();
    if (name==='multi') {
      await page.locator('[data-act=dup]').click();
      await page.locator('.intake-card').nth(1).locator('[data-act=flowVal]').fill('50oops');
    }
    const pdf=await page.pdf({path:testInfo.outputPath(`${name}.pdf`),format:'Letter',printBackground:true});
    expect(pdf.subarray(0,5).toString()).toBe('%PDF-');
    await expect(page.locator('#rollup .badge-row')).toContainText(state);
    await expect(page.locator('.print-value').filter({hasText:name==='multi'?/^50oops$/:/^50$/})).toHaveCount(1);
  }
});
