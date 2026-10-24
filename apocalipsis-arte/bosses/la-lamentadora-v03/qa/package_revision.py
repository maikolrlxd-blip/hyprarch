"""Empaqueta solamente la revision vigente; conserva diagnosticos fuera del ZIP."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parent.parent
files=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if '__pycache__' in rel.parts or p.suffix=='.blend1' or '.fbm' in str(rel):continue
    if rel.parts[0]=='previews' and 'v03b' not in p.name:continue
    if rel.parts[0]=='qa' and p.name in ('build-v03-01.log',):continue
    if p.name in ('MANIFEST.json',):continue
    files.append(p)
records=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,
          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
manifest=root/'MANIFEST.json'
manifest.write_text(json.dumps({'revision':'0.3b-estudio-visual','status':'pendiente feedback humano y Roblox',
  'files':records},indent=2),encoding='utf-8')
files.append(manifest)
out=Path(r'C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\La Lamentadora v03b - revision visual.zip')
if out.exists():raise RuntimeError('No sobrescribir paquete anterior')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in files:z.write(p,arcname='la-lamentadora-v03/'+p.relative_to(root).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for r in records:
        assert hashlib.sha256(z.read('la-lamentadora-v03/'+r['path'])).hexdigest()==r['sha256']
sha=hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.zip.sha256').write_text(sha+'  '+out.name+'\n',encoding='utf-8')
print(json.dumps({'package':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':sha}))
