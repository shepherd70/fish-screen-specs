// Emits each fixture row's calculation for comparison with the Python reader.
const fs = require('node:fs');
const {app} = require('./harness.cjs');
const run=app();
run(`var rows=parseCSV(${JSON.stringify(fs.readFileSync(process.argv[2],'utf8'))});var header=rows.shift();`);
const results=run(`rows.map((cells,i)=>{
  el('site_env').value=csvCell(header,cells,'water_type') || 'waterbody';
  try {
    const it=intakeFromCSVRow(header,cells,i+2), r=calcIntake(it);
    return {name:it.name,error:null,Q:r.Q,Vd:r.Vd,effective:r.Aeff_req,gross:r.Ageo_req_total,
      geometry:csvCell(header,cells,'geometry') ? {dims:r.solvedDims,area:r.Ageo_total} : null};
  } catch(error) {return {error:error.message};}
})`);
process.stdout.write(JSON.stringify(results));
