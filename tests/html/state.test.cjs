const {test} = require('node:test');
const assert = require('node:assert/strict');
const {app} = require('./harness.cjs');
function session() {
  const run=app();
  run('renderProducts=()=>{};renderChecklist=()=>{};renderAll=()=>{};intakes=[newIntake()];el("site_project").value="Original project";var saved=serializeState();');
  return run;
}
for(const [label,change] of [
  ['null intake','saved.intakes=[null]'],
  ['geometry','saved.intakes[0].geometry="unknown"'],
  ['prototype geometry','saved.intakes[0].geometry="toString"'],
  ['flow unit','saved.intakes[0].flowUnit="unknown"'],
  ['velocity source','saved.intakes[0].velSource="unknown"'],
  ['solve dimension','saved.intakes[0].solveFor="r"'],
  ['product index','saved.intakes[0].productIdx=500'],
  ['boolean','saved.intakes[0].assessmentConfirmed="false"'],
  ['dimensions','saved.intakes[0].dims=null'],
  ['optimizer','saved.intakes[0].opt.freeDim="r"'],
  ['checklist','saved.checklist=["true"]'],
  ['site environment','saved.site.site_env="other"'],
  ['null product','saved.products=[null]'],
]) test(`rejected JSON (${label}) preserves complete session and ID counter`,()=>{
  const run=session();
  const before=run('JSON.stringify(serializeState())');
  const uid=run('uid');
  run('saved.site.site_project="Replacement";saved.showImperial=true;'+change);
  assert.throws(()=>run('restoreState(saved)'));
  // savedAt is generated when serializing; compare the actual persistent fields.
  const strip=s=>{const v=JSON.parse(s);delete v.savedAt;return v;};
  assert.deepEqual(strip(run('JSON.stringify(serializeState())')),strip(before));
  assert.equal(run('uid'),uid);
});

test('checklist, confirmation, numeric drafts and display units round-trip',()=>{
  const run=session();
  run('intakes[0].flowVal="50oops";checklistAnswers[2]=true;showImperial=true;saved=serializeState();checklistAnswers=[];restoreState(saved)');
  assert.equal(run('intakes[0].flowVal'),'50oops');
  assert.equal(run('calcIntake(intakes[0]).state'),'invalid');
  assert.equal(run('checklistAnswers[2]'),true);
  assert.equal(run('showImperial'),true);
});

test('legacy session clears old checklist and stays unassessed',()=>{
  const run=session();
  run('delete saved.checklist;delete saved.intakes[0].assessmentConfirmed;checklistAnswers[0]=true;restoreState(saved)');
  assert.equal(run('checklistAnswers.some(Boolean)'),false);
  assert.equal(run('calcIntake(intakes[0]).state'),'unassessed');
});

test('site state precedence cannot conceal incomplete evidence or failed checks',()=>{
  const run=session();
  assert.equal(run('siteState()'),'unassessed');
  run('intakes[0].assessmentConfirmed=true');
  assert.equal(run('siteState()'),'pass');
  run('var second=newIntake();intakes.push(second);second.velSource="spot"');
  assert.equal(run('siteState()'),'review');
  run('second.opening_mm=10');
  assert.equal(run('siteState()'),'fail');
  run('second.flowVal="bad"');
  assert.equal(run('siteState()'),'invalid');
});

test('flow unit conversion preserves canonical flow and malformed drafts',()=>{
  const run=app();run('var it=newIntake();var before=calcIntake(it).Q;changeFlowUnit(it,"cfs")');
  assert.ok(run('Math.abs(calcIntake(it).Q-before)<1e-12'));
  run('changeFlowUnit(it,"Ls")');
  assert.ok(run('Math.abs(num(it.flowVal)-50)<1e-9'));
  run('it.flowVal="50oops";changeFlowUnit(it,"cfs")');
  assert.equal(run('it.flowVal'),'50oops');
});

test('CSV import rejects incompatible environments with row guidance and no site mutation',()=>{
  const run=app();
  run('var result=parseIntakeCSV("name,flow_m3s,water_type\\nPond,0.05,waterbody\\nRiver,0.05,watercourse")');
  assert.equal(run('result.added.length'),1);
  assert.match(run('result.errors[0]'),/row 3.*matching site/);
  assert.equal(run('currentEnv()'),'waterbody');
  assert.throws(()=>run('parseIntakeCSV("flow_Ls\\n50")'),/unknown column/);
  assert.throws(()=>run('parseIntakeCSV("flow_m3s,flow_m3s\\n0.05,0.06")'),/duplicate/);
});

test('new intake with an empty product library can round-trip its manual values',()=>{
  const run=session();run('PRODUCTS=[];intakes=[newIntake()];restoreState(serializeState())');
  assert.equal(run('intakes[0].productIdx'),-1);
  assert.equal(run('calcIntake(intakes[0]).state'),'unassessed');
});

test('invalid library numeric drafts render as escaped text',()=>{
  const run=app();
  run('document.createElement=()=>({querySelectorAll:()=>[]});PRODUCTS[0].opening_mm="</option></select><img src=x>";PRODUCTS[0].oar="<script>";var card=renderIntakeCard(newIntake(),0)');
  assert.equal(run('card.innerHTML.includes("<img src=x>")'),false);
  assert.ok(run('card.innerHTML.includes("&lt;img src=x&gt;")'));
});
