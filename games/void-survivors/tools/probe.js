const {VS,botInput,botChoose}=require('./bot');
const U=VS.util;
const s=VS.Save.defaults();
const sim=new VS.Sim({ship:process.argv[4]||'falcon',stage:process.argv[2]||'s1',meta:VS.Meta.bonuses(s),rand:U.rng(+process.argv[3]||101),events:false});
let next=30;
while((sim.state==='running'||sim.state==='levelup')&&sim.t<600){
  if(sim.state==='levelup'){botChoose(sim);continue}
  sim.update(1/60,botInput(sim,1));
  if(sim.t>=next){next+=30;
    const boss=sim.enemies.find(e=>e.boss);
    console.log(`t=${sim.t.toFixed(0)} lvl=${sim.level} hp=${sim.p.hp.toFixed(0)}/${sim.st.maxHp.toFixed(0)} en=${sim.enemies.length} kills=${sim.kills} W=[${sim.weapons.map(w=>w.id+w.level).join(',')}] P=${JSON.stringify(sim.passives)} boss=${boss?boss.type+':'+boss.hp.toFixed(0)+'/'+boss.max.toFixed(0):'-'} dmgDone=${sim.dmgDone.toFixed(0)}`);
  }
}
console.log(sim.state,sim.t.toFixed(0));
