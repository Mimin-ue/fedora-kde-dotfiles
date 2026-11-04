"""Aplicar exclusivamente la apariencia de Plasma Login; requiere autorización de administrador."""
from pathlib import Path
import os,pwd,shutil,datetime,json,configparser,subprocess,tarfile,tempfile,hashlib
if os.geteuid()!=0:raise SystemExit('Se necesita autorización de administrador para la pantalla de inicio de sesión.')
root=Path(__file__).resolve().parent
archive=root/'desktop-files.tar.gz';expected=(root/'desktop-files.sha256').read_text().split()[0]
if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise SystemExit('El archivo de recursos no coincide con su suma SHA256.')
try:account=pwd.getpwnam('plasmalogin')
except KeyError:raise SystemExit('Este equipo no usa Plasma Login Manager. No aplicar este script a SDDM u otro gestor.')
temporary=tempfile.TemporaryDirectory(prefix='fedora-kde-login-')
with tarfile.open(archive) as archive_file:
 for member in archive_file:
  if member.name=='login' or member.name.startswith('login/'):
   archive_file.extract(member,temporary.name,filter='data')
source=Path(temporary.name)/'login'
managed=Path('/var/lib/plasmalogin')
backup=managed/'mimin-appearance-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
targets={'background.jpg':managed/'wallpapers/mimin-login.jpg','kdeglobals':managed/'.config/kdeglobals','90-mimin-appearance.conf':Path('/etc/plasmalogin.conf.d/90-mimin-appearance.conf')}
manifest={}
for name,p in targets.items():
 if p.is_symlink():raise SystemExit('Se encontró un enlace; revisar '+str(p))
 manifest[name]={'target':str(p),'existed':p.exists()}
 if p.exists():
  st=p.stat();manifest[name].update(uid=st.st_uid,gid=st.st_gid,mode=st.st_mode & 0o777)
 if p.exists():shutil.copy2(p,backup/name)
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
# El esquema se integra en el perfil independiente del usuario del greeter.
new=configparser.ConfigParser(interpolation=None);new.optionxform=str;new.read(source/'kdeglobals')
current=configparser.ConfigParser(interpolation=None);current.optionxform=str
if targets['kdeglobals'].exists():current.read(targets['kdeglobals'])
for section in new.sections():
 if not current.has_section(section):current.add_section(section)
 for k,v in new[section].items():current[section][k]=v
for name,p in targets.items():
 p.parent.mkdir(parents=True,exist_ok=True)
 if name=='kdeglobals':
  with p.open('w') as f:current.write(f,space_around_delimiters=False)
 else:shutil.copyfile(source/name,p)
 os.chmod(p,0o644)
 if str(p).startswith(str(managed)):
  os.chown(p,account.pw_uid,account.pw_gid);os.chown(p.parent,account.pw_uid,account.pw_gid)
if shutil.which('restorecon'):
 for p in targets.values():subprocess.run(['restorecon',str(p)],check=True)
assert targets['background.jpg'].read_bytes()==(source/'background.jpg').read_bytes()
assert targets['90-mimin-appearance.conf'].read_bytes()==(source/'90-mimin-appearance.conf').read_bytes()
assert targets['background.jpg'].stat().st_uid==account.pw_uid
(backup.parent/'LAST').write_text(backup.name+'\n')
print('Apariencia de Plasma Login aplicada. Será visible al volver a iniciar sesión. Respaldo:',backup)
