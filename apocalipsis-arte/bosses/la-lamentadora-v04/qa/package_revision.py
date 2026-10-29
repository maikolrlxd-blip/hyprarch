"""Empaqueta esta revision facial, verifica CRC y hashes de las entradas."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parent.parent
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if '__pycache__' in rel.parts or p.suffix=='.blend1' or '.fbm' in str(rel):continue
    if rel.parts[0]=='previews' and not p.name.startswith('LaLamentadora_v04_'):continue
    if p.name=='MANIFEST.json':continue
    files.append(p)
records=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,
          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
manifest=root/'MANIFEST.json'
manifest.write_text(json.dumps({'revision':'0.4-rostro','status':'pendiente feedback humano y Roblox',
    'files':records},indent=2),encoding='utf-8')
files.append(manifest)
out=Path(r'C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\La Lamentadora v04 - rostro.zip')
if out.exists():raise RuntimeError('No sobrescribir paquete anterior')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in files:z.write(p,arcname='la-lamentadora-v04/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for r in records:
        assert hashlib.sha256(z.read('la-lamentadora-v04/'+r['path'])).hexdigest()==r['sha256']
sha=hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.zip.sha256').write_text(sha+'  '+out.name+'\n',encoding='utf-8')
print(json.dumps({'package':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':sha}))
