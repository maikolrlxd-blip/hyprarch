// Traducciones (es/en). t('clave', {var}) -> texto. Si falta una clave en el idioma activo, cae a inglés.
(function (g) {
  'use strict';
  const VS = (g.VS = g.VS || {});

  const es = {
    'app.title': 'VOID SURVIVORS', 'app.tag': 'Sobrevive al vacío',
    play: 'JUGAR', ships: 'Naves', upgrades: 'Mejoras', missions: 'Misiones', trophies: 'Logros', settings: 'Ajustes',
    back: 'Volver', continue: 'Continuar', retry: 'Reintentar', home: 'Menú', resume: 'Reanudar', quit: 'Salir', pause: 'Pausa',
    coins: 'Monedas', stage: 'Fase', locked: 'Bloqueada', buy: 'Comprar', select: 'Elegir', selected: 'Elegida', owned: 'Tuya', max: 'MAX',
    claim: 'Reclamar', claimed: 'Reclamado', level: 'Nv', time: 'Tiempo', kills: 'Bajas', best: 'Mejor', new_best: '¡Nuevo récord!',
    victory: '¡VICTORIA!', defeat: 'DERROTA', levelup: '¡NIVEL!', choose_upgrade: 'Elige una mejora',
    reroll: 'Cambiar', revive_ad: 'Revivir (anuncio)', double_ad: 'Duplicar monedas (anuncio)', coins_earned: 'Monedas ganadas',
    win_bonus: 'Bonus de victoria', new_unlock: 'Nave desbloqueada', not_enough: 'Monedas insuficientes',
    daily_login: 'Recompensa diaria', login_day: 'Día {n}', login_streak: 'Racha: {n} días', login_streak1: 'Racha: 1 día', collect: 'Recoger',
    stats: 'Estadísticas', total_kills: 'Bajas totales', total_runs: 'Partidas', total_wins: 'Victorias', play_time: 'Tiempo jugado',
    unlock_clear: 'Supera {s}', unlock_stage: 'Supera la fase anterior', cost: 'Coste', start_weapon: 'Arma inicial',
    // ajustes
    sound: 'Efectos', music: 'Música', vibration: 'Vibración', shake: 'Sacudida de pantalla', numbers: 'Números de daño', language: 'Idioma',
    reset: 'Borrar progreso', reset_confirm: '¿Borrar TODO el progreso? No se puede deshacer.', privacy: 'Política de privacidad',
    // HUD / avisos
    'warn.elite': '¡Élite!', 'warn.swarm': '¡Enjambre!', 'warn.boss': '¡JEFE!', 'warn.final': '¡JEFE FINAL!',
    'hint.move': 'Arrastra para moverte', 'hint.auto': 'Disparas automáticamente', 'hint.gems': 'Recoge gemas para subir de nivel', 'hint.boss': 'Sobrevive y derrota al jefe final',
    // stats de armas
    'stat.cd': 'Recarga', 'stat.n': 'Cantidad', 'stat.dmg': 'Daño', 'stat.pierce': 'Perforación', 'stat.jumps': 'Saltos', 'stat.aoe': 'Explosión',
    'stat.R': 'Radio', 'stat.range': 'Alcance', 'stat.knock': 'Empuje', 'stat.tick': 'Ritmo', 'stat.spin': 'Giro', 'stat.new': 'Nueva arma',
    heal: 'Reparación', 'heal.d': 'Recupera el 50% de la vida', 'coins.d': 'Obtienes monedas extra', 'bonus_coins': 'Monedas',
    evolution: 'EVOLUCIÓN', 'w.pulse.evo': 'Tormenta de pulsos', 'w.orbit.evo': 'Halo de cuchillas', 'w.chain.evo': 'Tempestad', 'w.missile.evo': 'Lluvia de misiles', 'w.nova.evo': 'Supernova', 'w.aura.evo': 'Campo vital', 'evo.need': 'Requiere {p}', 'evolved_toast': '¡{w} evolucionó!',
    'a.evolve': 'Evolución', 'a.evolve.d': 'Evoluciona un arma.', 'a.evolve2': 'Maestro de la evolución', 'a.evolve2.d': 'Evoluciona 25 armas.',
    // armas
    'w.pulse.n': 'Cañón de pulso', 'w.pulse.d': 'Dispara a los enemigos más cercanos.',
    'w.orbit.n': 'Cuchillas orbitales', 'w.orbit.d': 'Cuchillas que giran a tu alrededor.',
    'w.chain.n': 'Rayo en cadena', 'w.chain.d': 'Un rayo salta entre enemigos.',
    'w.missile.n': 'Misiles guiados', 'w.missile.d': 'Misiles que explotan en área.',
    'w.nova.n': 'Onda nova', 'w.nova.d': 'Onda expansiva que empuja y daña.',
    'w.aura.n': 'Campo de plasma', 'w.aura.d': 'Daña y ralentiza a quien se acerque.',
    // pasivos
    'p.power.n': 'Núcleo de potencia', 'p.power.d': '+12% de daño por nivel.',
    'p.overclock.n': 'Sobrecarga', 'p.overclock.d': '-8% de recarga por nivel.',
    'p.thrusters.n': 'Propulsores', 'p.thrusters.d': '+8% de velocidad por nivel.',
    'p.plating.n': 'Blindaje', 'p.plating.d': '+12% de vida máxima por nivel.',
    'p.magnet.n': 'Imán', 'p.magnet.d': '+25% de radio de recogida por nivel.',
    'p.barrier.n': 'Barrera', 'p.barrier.d': '+1 de armadura por nivel.',
    'p.scholar.n': 'Procesador', 'p.scholar.d': '+10% de experiencia por nivel.',
    'p.regen.n': 'Nanobots', 'p.regen.d': 'Regenera 0.4 de vida por segundo por nivel.',
    'p.lens.n': 'Lente focal', 'p.lens.d': '+10% de área y velocidad de proyectiles por nivel.',
    'p.fortune.n': 'Suerte', 'p.fortune.d': '+5% de crítico y más monedas por nivel.',
    // naves
    'sh.falcon.n': 'Halcón', 'sh.falcon.d': 'Equilibrada. Ideal para empezar.',
    'sh.comet.n': 'Cometa', 'sh.comet.d': 'Muy rápida, con gran radio de recogida. Poca vida.',
    'sh.bulwark.n': 'Baluarte', 'sh.bulwark.d': 'Un tanque lento: mucha vida y armadura, combate cercano.',
    'sh.wraith.n': 'Espectro', 'sh.wraith.d': 'Críticos frecuentes y misiles guiados.',
    'sh.nova.n': 'Nova', 'sh.nova.d': 'Mayor área y recarga rápida. Ondas devastadoras.',
    'stat.hp': 'Vida', 'stat.speed': 'Velocidad', 'stat.armor': 'Armadura',
    // fases
    'st.s1.n': 'Campo de escombros', 'st.s1.d': 'Los restos de una antigua flota.',
    'st.s2.n': 'Nebulosa iónica', 'st.s2.d': 'Más enemigos, más tiradores y más recompensa.',
    'st.s3.n': 'Sol negro', 'st.s3.d': 'La prueba definitiva. Gran recompensa.',
    'boss.hive': 'Madre colmena', 'boss.sentinel': 'Centinela', 'boss.jugg': 'Juggernaut',
    // mejoras permanentes
    'u.hp.n': 'Vida máxima', 'u.hp.d': '+6% de vida por nivel', 'u.dmg.n': 'Daño', 'u.dmg.d': '+4% de daño por nivel',
    'u.speed.n': 'Velocidad', 'u.speed.d': '+3% de velocidad por nivel', 'u.magnet.n': 'Imán', 'u.magnet.d': '+10% de recogida por nivel',
    'u.xp.n': 'Experiencia', 'u.xp.d': '+5% de XP por nivel', 'u.coin.n': 'Botín', 'u.coin.d': '+5% de monedas por nivel',
    'u.armor.n': 'Armadura', 'u.armor.d': '+1 de armadura por nivel', 'u.regen.n': 'Regeneración', 'u.regen.d': '+0.15 vida/s por nivel',
    'u.reroll.n': 'Cambios', 'u.reroll.d': '+1 cambio de mejoras por partida', 'u.revive.n': 'Revivir', 'u.revive.d': '+1 resurrección por partida',
    'u.choice.n': 'Cuarta opción', 'u.choice.d': 'Una opción más al subir de nivel',
    // misiones
    'm.kills': 'Derrota {n} enemigos', 'm.coins': 'Gana {n} monedas', 'm.runs': 'Juega {n} partidas', 'm.boss': 'Derrota {n} jefes',
    'm.time': 'Sobrevive {n} en una partida', 'm.level': 'Llega al nivel {n} en una partida', 'm.win': 'Gana {n} partida(s)',
    daily: 'Misiones diarias', resets: 'Se renuevan cada día',
    // logros
    'a.kills1': 'Primeras bajas', 'a.kills1.d': 'Derrota 100 enemigos.', 'a.kills2': 'Cazador', 'a.kills2.d': 'Derrota 1.500 enemigos.',
    'a.kills3': 'Exterminador', 'a.kills3.d': 'Derrota 15.000 enemigos.', 'a.bosses': 'Matajefes', 'a.bosses.d': 'Derrota 10 jefes.',
    'a.runs': 'Veterano', 'a.runs.d': 'Juega 25 partidas.', 'a.survive': 'Superviviente', 'a.survive.d': 'Aguanta 5 minutos.',
    'a.level20': 'Poder creciente', 'a.level20.d': 'Llega al nivel 20.', 'a.level35': 'Imparable', 'a.level35.d': 'Llega al nivel 35.',
    'a.win1': 'Escombros limpios', 'a.win1.d': 'Gana la fase 1.', 'a.win2': 'Tormenta domada', 'a.win2.d': 'Gana la fase 2.',
    'a.win3': 'Amo del vacío', 'a.win3.d': 'Gana la fase 3.', 'a.rich': 'Rico', 'a.rich.d': 'Gana 10.000 monedas en total.',
    'a.ships': 'Coleccionista', 'a.ships.d': 'Consigue 3 naves.', 'a.maxw': 'Arma definitiva', 'a.maxw.d': 'Sube un arma al nivel 6.',
    'a.upg': 'Mejorando', 'a.upg.d': 'Compra 25 niveles de mejoras.',
  };

  const en = {
    'app.title': 'VOID SURVIVORS', 'app.tag': 'Survive the void',
    play: 'PLAY', ships: 'Ships', upgrades: 'Upgrades', missions: 'Missions', trophies: 'Trophies', settings: 'Settings',
    back: 'Back', continue: 'Continue', retry: 'Retry', home: 'Home', resume: 'Resume', quit: 'Quit', pause: 'Paused',
    coins: 'Coins', stage: 'Stage', locked: 'Locked', buy: 'Buy', select: 'Select', selected: 'Selected', owned: 'Owned', max: 'MAX',
    claim: 'Claim', claimed: 'Claimed', level: 'Lv', time: 'Time', kills: 'Kills', best: 'Best', new_best: 'New record!',
    victory: 'VICTORY!', defeat: 'DEFEAT', levelup: 'LEVEL UP!', choose_upgrade: 'Choose an upgrade',
    reroll: 'Reroll', revive_ad: 'Revive (ad)', double_ad: 'Double coins (ad)', coins_earned: 'Coins earned',
    win_bonus: 'Victory bonus', new_unlock: 'Ship unlocked', not_enough: 'Not enough coins',
    daily_login: 'Daily reward', login_day: 'Day {n}', login_streak: 'Streak: {n} days', login_streak1: 'Streak: 1 day', collect: 'Collect',
    stats: 'Statistics', total_kills: 'Total kills', total_runs: 'Runs', total_wins: 'Wins', play_time: 'Play time',
    unlock_clear: 'Clear {s}', unlock_stage: 'Clear the previous stage', cost: 'Cost', start_weapon: 'Starting weapon',
    sound: 'Sound effects', music: 'Music', vibration: 'Vibration', shake: 'Screen shake', numbers: 'Damage numbers', language: 'Language',
    reset: 'Reset progress', reset_confirm: 'Erase ALL progress? This cannot be undone.', privacy: 'Privacy policy',
    'warn.elite': 'Elite!', 'warn.swarm': 'Swarm!', 'warn.boss': 'BOSS!', 'warn.final': 'FINAL BOSS!',
    'hint.move': 'Drag to move', 'hint.auto': 'You fire automatically', 'hint.gems': 'Collect gems to level up', 'hint.boss': 'Survive and defeat the final boss',
    'stat.cd': 'Cooldown', 'stat.n': 'Count', 'stat.dmg': 'Damage', 'stat.pierce': 'Pierce', 'stat.jumps': 'Jumps', 'stat.aoe': 'Blast',
    'stat.R': 'Radius', 'stat.range': 'Range', 'stat.knock': 'Knockback', 'stat.tick': 'Rate', 'stat.spin': 'Spin', 'stat.new': 'New weapon',
    heal: 'Repair', 'heal.d': 'Restore 50% health', 'coins.d': 'Get bonus coins', 'bonus_coins': 'Coins',
    evolution: 'EVOLUTION', 'w.pulse.evo': 'Pulse Storm', 'w.orbit.evo': 'Blade Halo', 'w.chain.evo': 'Tempest', 'w.missile.evo': 'Missile Rain', 'w.nova.evo': 'Supernova', 'w.aura.evo': 'Vital Field', 'evo.need': 'Requires {p}', 'evolved_toast': '{w} evolved!',
    'a.evolve': 'Evolution', 'a.evolve.d': 'Evolve a weapon.', 'a.evolve2': 'Evolution master', 'a.evolve2.d': 'Evolve 25 weapons.',
    'w.pulse.n': 'Pulse Cannon', 'w.pulse.d': 'Fires at the nearest enemies.',
    'w.orbit.n': 'Orbital Blades', 'w.orbit.d': 'Blades spinning around you.',
    'w.chain.n': 'Chain Lightning', 'w.chain.d': 'A bolt that jumps between enemies.',
    'w.missile.n': 'Homing Missiles', 'w.missile.d': 'Missiles that explode in an area.',
    'w.nova.n': 'Nova Wave', 'w.nova.d': 'A shockwave that pushes and damages.',
    'w.aura.n': 'Plasma Field', 'w.aura.d': 'Damages and slows anything close.',
    'p.power.n': 'Power Core', 'p.power.d': '+12% damage per level.',
    'p.overclock.n': 'Overclock', 'p.overclock.d': '-8% cooldown per level.',
    'p.thrusters.n': 'Thrusters', 'p.thrusters.d': '+8% move speed per level.',
    'p.plating.n': 'Plating', 'p.plating.d': '+12% max health per level.',
    'p.magnet.n': 'Magnet', 'p.magnet.d': '+25% pickup radius per level.',
    'p.barrier.n': 'Barrier', 'p.barrier.d': '+1 armor per level.',
    'p.scholar.n': 'Processor', 'p.scholar.d': '+10% experience per level.',
    'p.regen.n': 'Nanobots', 'p.regen.d': 'Regenerate 0.4 HP/s per level.',
    'p.lens.n': 'Focal Lens', 'p.lens.d': '+10% area and projectile speed per level.',
    'p.fortune.n': 'Fortune', 'p.fortune.d': '+5% crit and more coins per level.',
    'sh.falcon.n': 'Falcon', 'sh.falcon.d': 'Balanced. Great for starting out.',
    'sh.comet.n': 'Comet', 'sh.comet.d': 'Very fast with a large pickup radius. Fragile.',
    'sh.bulwark.n': 'Bulwark', 'sh.bulwark.d': 'A slow tank: lots of health and armor, close combat.',
    'sh.wraith.n': 'Wraith', 'sh.wraith.d': 'Frequent crits and homing missiles.',
    'sh.nova.n': 'Nova', 'sh.nova.d': 'Bigger area and faster cooldowns. Devastating waves.',
    'stat.hp': 'Health', 'stat.speed': 'Speed', 'stat.armor': 'Armor',
    'st.s1.n': 'Debris Field', 'st.s1.d': 'The remains of an ancient fleet.',
    'st.s2.n': 'Ion Nebula', 'st.s2.d': 'More enemies, more shooters, better rewards.',
    'st.s3.n': 'Black Sun', 'st.s3.d': 'The ultimate test. Huge rewards.',
    'boss.hive': 'Hive Mother', 'boss.sentinel': 'Sentinel', 'boss.jugg': 'Juggernaut',
    'u.hp.n': 'Max health', 'u.hp.d': '+6% health per level', 'u.dmg.n': 'Damage', 'u.dmg.d': '+4% damage per level',
    'u.speed.n': 'Speed', 'u.speed.d': '+3% speed per level', 'u.magnet.n': 'Magnet', 'u.magnet.d': '+10% pickup radius per level',
    'u.xp.n': 'Experience', 'u.xp.d': '+5% XP per level', 'u.coin.n': 'Loot', 'u.coin.d': '+5% coins per level',
    'u.armor.n': 'Armor', 'u.armor.d': '+1 armor per level', 'u.regen.n': 'Regeneration', 'u.regen.d': '+0.15 HP/s per level',
    'u.reroll.n': 'Rerolls', 'u.reroll.d': '+1 upgrade reroll per run', 'u.revive.n': 'Revive', 'u.revive.d': '+1 resurrection per run',
    'u.choice.n': 'Fourth option', 'u.choice.d': 'One extra choice when leveling up',
    'm.kills': 'Defeat {n} enemies', 'm.coins': 'Earn {n} coins', 'm.runs': 'Play {n} runs', 'm.boss': 'Defeat {n} bosses',
    'm.time': 'Survive {n} in one run', 'm.level': 'Reach level {n} in one run', 'm.win': 'Win {n} run(s)',
    daily: 'Daily missions', resets: 'Refreshes every day',
    'a.kills1': 'First blood', 'a.kills1.d': 'Defeat 100 enemies.', 'a.kills2': 'Hunter', 'a.kills2.d': 'Defeat 1,500 enemies.',
    'a.kills3': 'Exterminator', 'a.kills3.d': 'Defeat 15,000 enemies.', 'a.bosses': 'Boss slayer', 'a.bosses.d': 'Defeat 10 bosses.',
    'a.runs': 'Veteran', 'a.runs.d': 'Play 25 runs.', 'a.survive': 'Survivor', 'a.survive.d': 'Last 5 minutes.',
    'a.level20': 'Rising power', 'a.level20.d': 'Reach level 20.', 'a.level35': 'Unstoppable', 'a.level35.d': 'Reach level 35.',
    'a.win1': 'Debris cleared', 'a.win1.d': 'Win stage 1.', 'a.win2': 'Storm tamed', 'a.win2.d': 'Win stage 2.',
    'a.win3': 'Void master', 'a.win3.d': 'Win stage 3.', 'a.rich': 'Rich', 'a.rich.d': 'Earn 10,000 coins in total.',
    'a.ships': 'Collector', 'a.ships.d': 'Own 3 ships.', 'a.maxw': 'Ultimate weapon', 'a.maxw.d': 'Raise a weapon to level 6.',
    'a.upg': 'Upgrading', 'a.upg.d': 'Buy 25 upgrade levels.',
  };

  const dict = { es, en };
  const I = (VS.i18n = {
    lang: 'en',
    detect() {
      const l = ((g.navigator && (g.navigator.language || '')) || 'en').toLowerCase();
      return l.startsWith('es') ? 'es' : 'en';
    },
    set(l) { this.lang = dict[l] ? l : 'en'; if (g.document) g.document.documentElement.lang = this.lang; },
  });
  VS.t = function (key, vars) {
    let s = dict[I.lang][key];
    if (s === undefined) s = dict.en[key];
    if (s === undefined) return key;
    if (vars) for (const k in vars) s = s.replace('{' + k + '}', vars[k]);
    return s;
  };
  VS.i18nDict = dict;
})(typeof window !== 'undefined' ? window : globalThis);
