const {run,VS}=require('./bot');
const D=VS.data;
// uso: node sweep.js stage '{"rate0":1.6,...}' [seeds] [meta]
const stage=process.argv[2], over=JSON.parse(process.argv[3]||'{}'), n=+process.argv[4]||6, meta=process.argv[5]?JSON.parse(process.argv[5]):{};
if(over.tune){Object.assign(D.tune,over.tune);delete over.tune}
Object.assign(D.stages[stage],over);
let w=0,t=0,l=0,en=0,tk=0;
for(let i=0;i<n;i++){const r=run({seed:200+i,stage,meta});if(r.won)w++;t+=r.time;l+=r.level;en+=r.maxEn;tk+=r.dmgTaken}
console.log(`${stage} ${JSON.stringify(over)} meta=${JSON.stringify(meta)} -> wins ${w}/${n} avgT ${(t/n).toFixed(0)} lvl ${(l/n).toFixed(0)} maxEn ${(en/n).toFixed(0)} dmgTaken ${(tk/n).toFixed(0)}`);
