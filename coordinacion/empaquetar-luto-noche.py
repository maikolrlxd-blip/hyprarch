"""Paquete reproducible; solo cuatro carpetas propias, respetando ignores del repo.
Uso: python coordinacion/empaquetar-luto-noche.py <carpeta outputs>
No modifica juego, otras carpetas, Git ni entregas anteriores.
"""
from pathlib import Path
import subprocess,sys,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parent.parent
ASSETS=['apocalipsis-arte/bosses/la-lamentadora-v05','apocalipsis-arte/armas/lanzallamas-v01',
        'apocalipsis-arte/zombi-mujer/animaciones-quemado-v01','apocalipsis-arte/mapa/hospital-v01']
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
archive=out/'LUTO - arte nocturno 2026-10-24.zip'
if archive.exists():raise RuntimeError('Entrega existente: no sobrescribir '+str(archive))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
files=[]
for directory in ASSETS:
    raw=subprocess.check_output(['git','-c','core.quotepath=false','ls-files','--cached','--others','--exclude-standard','-z','--',directory],cwd=ROOT)
    paths=sorted({ROOT/f.decode('utf-8') for f in raw.split(b'\0') if f})
    paths=[p for p in paths if p.name!='MANIFEST.json']
    manifest=ROOT/directory/'MANIFEST.json'
    rows=[{'path':p.relative_to(ROOT/directory).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
    manifest.write_text(json.dumps({'scope':'Entrega de arte Blender, sin motor','files':rows},indent=2,ensure_ascii=False),encoding='utf-8')
    files+=paths+[manifest]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
    z.write(ROOT/'coordinacion'/'RELEVO-NOCHE-LUTO.md','RELEVO-NOCHE-LUTO.md')
    z.write(Path(__file__),'empaquetar-luto-noche.py')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for p in files:assert hashlib.sha256(z.read(p.relative_to(ROOT).as_posix())).hexdigest()==sha(p)
    count=len(z.infolist())
digest=sha(archive)
Path(str(archive)+'.sha256').write_text(digest+'  '+archive.name+'\n',encoding='utf-8')
report={'archive':str(archive),'sha256':digest,'bytes':archive.stat().st_size,'files':count,'crc_and_hashes_passed':True,'scope':'Assets offline; no Play'}
(out/'LUTO - entrega nocturna 2026-10-24.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
