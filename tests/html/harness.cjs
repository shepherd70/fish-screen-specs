const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../fish-screen-tool.html'), 'utf8');
function app() {
  const elements = new Map();
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, {value:id==='site_env'?'waterbody':'', checked:false, style:{}, textContent:'', innerHTML:'', querySelectorAll:()=>[]});
      return elements.get(id);
    },
    addEventListener() {},
    querySelectorAll:()=>[],
  };
  const context = vm.createContext({document, console, setTimeout, clearTimeout});
  vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
  return code => vm.runInContext(code, context);
}
module.exports = {app};
