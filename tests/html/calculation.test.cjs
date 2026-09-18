const {test} = require('node:test');
const assert = require('node:assert/strict');
const {app} = require('./harness.cjs');

test('fresh example is unassessed, confirmed sizing retains worked result', () => {
  const run=app();
  run('var it=newIntake()');
  assert.equal(run('it.name'),'Intake 1');
  assert.equal(run('calcIntake(it).state'),'unassessed');
  assert.equal(run('calcIntake(it).pass'),false);
  assert.equal(run('calcIntake(it).solvedRounded'),3.989);
  run('it.assessmentConfirmed=true');
  assert.equal(run('calcIntake(it).state'),'pass');
});

for (const [label, change, field] of [
  ['trailing junk','it.flowVal="50oops"','flowVal'],
  ['infinity','it.flowVal="Infinity"','flowVal'],
  ['fractional units','it.units=1.5','units'],
  ['negative cylinder','it.solveFor="";it.dims.D=-3;it.dims.L=-3','dim.D'],
  ['envelope text','it.maxDim="abc"','maxDim'],
  ['fouling out of range','it.fouling=1.5','fouling'],
  ['negative angle','el("site_env").value="watercourse";it.faceAngle=-1','faceAngle'],
  ['blank opening','it.opening_mm=""','opening_mm'],
]) test(`card and optimizer reject ${label}`,()=>{
  const run=app();run('var it=newIntake();it.assessmentConfirmed=true;'+change);
  assert.equal(run('calcIntake(it).state'),'invalid');
  assert.ok(run(`calcIntake(it).fields[${JSON.stringify(field)}]`));
  assert.ok(run('optimizeIntake(it).error'));
});

test('elevated credit requires flowing environment and baseline confirmation',()=>{
  const run=app();run('var it=newIntake();it.velSource="elevated";it.assessmentConfirmed=true;it.baselineConfirmed=true');
  assert.equal(run('calcIntake(it).state'),'invalid');
  run('el("site_env").value="watercourse";it.baselineConfirmed=false');
  assert.equal(run('calcIntake(it).state'),'review');
  assert.ok(run('optimizeIntake(it).error'));
  run('it.baselineConfirmed=true');
  assert.equal(run('calcIntake(it).Vd'),0.12);
  assert.equal(run('calcIntake(it).state'),'pass');
  assert.equal(run('calcIntake(it).checks.some(c=>c.title.includes("Sweeping"))'),false);
});

test('SPOT needs basis and species, with additional review above sweeping ceiling',()=>{
  const run=app();run('var it=newIntake();it.velSource="spot";it.spotVel=0.5;it.assessmentConfirmed=true');
  assert.equal(run('calcIntake(it).state'),'review');
  run('it.spotBasis="SPOT calculation record 17";el("site_species").value="Recorded species"');
  assert.equal(run('calcIntake(it).state'),'review');
  run('it.spotReviewed=true');
  assert.equal(run('calcIntake(it).state'),'pass');
});

test('optimizer excludes failing angle and preserves fixed dimensions',()=>{
  const run=app();run('var it=newIntake();el("site_env").value="watercourse";it.faceAngle=60');
  assert.equal(run('optimizeIntake(it).best'),null);
  run('it.faceAngle=0;it.dims.D=1;it.maxDim=0.8;it.opt.objective="maxmargin"');
  assert.equal(run('optimizeIntake(it).best'),null);
  run('applyOptimization(it)');
  assert.equal(run('it.dims.D'),1);
});

test('applied recommendation passes all calculated checks and keeps fixed dimensions',()=>{
  const run=app();run('var it=newIntake();it.assessmentConfirmed=true;applyOptimization(it)');
  assert.equal(run('it.opt.msgOk'),true);
  assert.equal(run('it.dims.D'),0.3);
  assert.equal(run('calcIntake(it).sizingPass'),true);
  assert.equal(run('calcIntake(it).state'),'unassessed');
  run('it.assessmentConfirmed=true');
  assert.equal(run('calcIntake(it).pass'),true);
});

test('changing optimizer free dimension preserves the other displayed solved dimension',()=>{
  const run=app();run('var it=newIntake();var displayed=calcIntake(it).solvedDims.L;it.opt.freeDim="D";var expected=optimizeIntake(it).best.chosen;applyOptimization(it)');
  assert.equal(run('it.dims.L'),run('displayed'));
  assert.ok(run('Math.abs(calcIntake(it).Vactual-expected.Vact)<1e-12'));
  assert.equal(run('calcIntake(it).sizingPass'),true);
});
