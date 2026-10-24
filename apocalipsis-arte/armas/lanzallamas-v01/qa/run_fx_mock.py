"""Ejecuta el modulo real dentro de mocks declarados, sin motor."""
from pathlib import Path
import subprocess,sys,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/'integracion'/'QuemadoFX.lua').read_text(encoding='utf-8')
test=ROOT/'qa'/'fx_generated_test.luau'
test.write_text((ROOT/'qa'/'fx_harness_prefix.luau').read_text()+source+'\n'+(ROOT/'qa'/'fx_harness_suffix.luau').read_text(),encoding='utf-8')
r=subprocess.run([sys.argv[1],str(test)],capture_output=True,text=True)
(ROOT/'qa'/'fx-mock.log').write_text(r.stdout+r.stderr,encoding='utf-8')
(ROOT/'qa'/'VALIDACION-FX-MOCK.json').write_text(json.dumps({'passed':r.returncode==0,'cases':r.stdout.count('FX_MOCK PASS'),'module_sha256':hashlib.sha256(source.encode()).hexdigest(),'scope':'Mocks de ciclo de vida, sin ParticleEmitter real ni pruebas de motor'},indent=2),encoding='utf-8')
print(r.stdout,r.stderr);raise SystemExit(r.returncode)
