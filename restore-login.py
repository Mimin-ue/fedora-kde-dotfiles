from pathlib import Path
import os,json,shutil
if os.geteuid()!=0:raise SystemExit('Se necesita autorización de administrador.')
root=Path('/var/lib/plasmalogin/mimin-appearance-backups');backup=root/(root/'LAST').read_text().strip();manifest=json.loads((backup/'manifest.json').read_text())
for name,item in manifest.items():
 p=Path(item['target'])
 if item['existed']:
  shutil.copy2(backup/name,p)
  if 'uid' in item:os.chown(p,item['uid'],item['gid']);os.chmod(p,item['mode'])
 else:p.unlink(missing_ok=True)
print('Restaurada la apariencia anterior del inicio de sesión.')
