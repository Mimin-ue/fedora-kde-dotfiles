#!/usr/bin/env python3
"""Restore the saved visual setup; no writes unless --apply or --stage-only is given."""
from pathlib import Path
import argparse,configparser,datetime,hashlib,json,locale,os,platform,re,shutil,subprocess,tarfile,tempfile,urllib.request
ROOT=Path(__file__).resolve().parent

def run(*args,check=True,env=None):
    return subprocess.run(args,check=check,capture_output=True,text=True,env=env).stdout

def ini(path):
    c=configparser.ConfigParser(interpolation=None,strict=False);c.optionxform=str;c.read(path);return c

def write_ini(path,c):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:c.write(f,space_around_delimiters=False)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def extract(archive,destination):
    with tarfile.open(archive) as a:a.extractall(destination,filter='data')

def expand_tree(folder,home):
    for p in folder.rglob('*'):
        if not p.is_file() or p.is_symlink():continue
        try:s=p.read_text()
        except UnicodeDecodeError:continue
        if '@HOME@' in s:p.write_text(s.replace('@HOME@',str(home)))

def main():
    parser=argparse.ArgumentParser(description='Restaurar el escritorio Fedora KDE guardado.')
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--apply',action='store_true',help='Respaldar y aplicar en la sesión KDE actual.')
    modes.add_argument('--stage-only',type=Path,metavar='DIRECTORIO',help='Probar la instalación en una carpeta vacía, sin tocar KDE ni servicios.')
    modes.add_argument('--check',action='store_true',help='Comprobar dependencias e integridad; no modifica el escritorio.')
    args=parser.parse_args()
    archive=ROOT/'desktop-files.tar.gz';expected=(ROOT/'desktop-files.sha256').read_text().split()[0]
    if digest(archive)!=expected:raise SystemExit('El archivo de recursos no coincide con su suma SHA256.')
    required=['qdbus-qt6','kwriteconfig6','kbuildsycoca6','fish','fastfetch','cava','systemctl','fc-cache']
    missing=[x for x in required if not shutil.which(x)]
    try:__import__('PySide6.QtDBus')
    except ImportError:missing.append('python3-pyside6')
    print('Integridad de recursos: correcta. Faltan: '+(', '.join(missing) or 'ninguna dependencia principal'))
    if not args.apply and not args.stage_only:
        print('Sin cambios. Usar --apply para instalar o --stage-only DIRECTORIO para una prueba aislada.')
        return
    if os.geteuid()==0:raise SystemExit('Ejecutar con la cuenta normal de KDE, sin sudo.')
    if args.apply and missing:raise SystemExit('Instala las dependencias indicadas en README.md antes de aplicar.')
    if args.apply and platform.machine()!='x86_64':raise SystemExit('El paquete de Kitty verificado es x86_64; esta arquitectura necesita otra versión validada.')
    if args.apply:
        # Verify the intended desktop session before writing.
        run('qdbus-qt6','org.kde.plasmashell','/PlasmaShell','org.freedesktop.DBus.Peer.Ping')
        home=Path.home();backup=home/'.local/state/fedora-kde-dotfiles/backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    else:
        home=args.stage_only.resolve()
        if home.exists() and any(home.iterdir()):raise SystemExit('La carpeta de prueba debe estar vacía.')
        home.mkdir(parents=True,exist_ok=True);backup=home/'.local/state/fedora-kde-dotfiles/backups/staging'
    backup.mkdir(parents=True,mode=0o700);manifest={};runtime={'stage_only':not args.apply}
    def save(path):
        name=str(path)
        if name in manifest:return
        if path.is_symlink():raise RuntimeError('Revisar enlace existente antes de sustituir: '+name)
        item={'existed':path.exists(),'directory':path.is_dir(),'copy':str(len(manifest))};manifest[name]=item
        if path.is_dir():shutil.copytree(path,backup/item['copy'],symlinks=True)
        elif path.exists():shutil.copy2(path,backup/item['copy'])
        (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
    def put(src,dst):
        save(dst);dst.parent.mkdir(parents=True,exist_ok=True)
        if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True,symlinks=True)
        else:shutil.copy2(src,dst)
    with tempfile.TemporaryDirectory(prefix='fedora-kde-files-') as temp:
        data=Path(temp);extract(archive,data)
        file_manifest=json.loads((ROOT/'files-manifest.json').read_text())
        for name,sha in file_manifest.items():
            if digest(data/name)!=sha:raise RuntimeError('Recurso alterado: '+name)
        expand_tree(data,home)
        extract(data/'gruvbox-plus-dark.tar.gz',data/'icons')
        settings=json.loads((ROOT/'settings.json').read_text().replace('@HOME@',str(home)))
        settings['home']=str(home)
        # Keep existing local apps; do not pin launchers for absent software.
        for module in settings['modules']:
            if module['plugin']=='org.kde.plasma.quicklaunch':
                urls=module['groups']['General']['launcherUrls'].split(',')
                module['groups']['General']['launcherUrls']=[u for u in urls if 'venom-terminal.desktop' in u or Path(u.removeprefix('file://')).exists()]
        for name in settings['configs']:save(home/'.config'/name)
        for name in ['plasma-org.kde.plasma.desktop-appletsrc','plasmashellrc']:save(home/'.config'/name)
        if args.apply:
            manager=['qdbus-qt6','org.kde.KWin','/VirtualDesktopManager']
            raw=run(*manager,'org.kde.KWin.VirtualDesktopManager.desktops')
            runtime['original_desktops']=list(dict.fromkeys(re.findall(r'[0-9a-f]{8}-[0-9a-f-]{27,}',raw)))
            runtime['spectrum_enabled']=subprocess.run(['systemctl','--user','is-enabled','local-mimin-spectrum.service'],capture_output=True).returncode==0
            runtime['spectrum_active']=subprocess.run(['systemctl','--user','is-active','local-mimin-spectrum.service'],capture_output=True).returncode==0
            count=int(run(*manager,'org.kde.KWin.VirtualDesktopManager.count').strip())
            for index in range(count,settings['desktop_count']):run(*manager,'org.kde.KWin.VirtualDesktopManager.createDesktop',str(index),str(index+1))
            after=run(*manager,'org.kde.KWin.VirtualDesktopManager.desktops')
            runtime['created_desktops']=[x for x in dict.fromkeys(re.findall(r'[0-9a-f]{8}-[0-9a-f-]{27,}',after)) if x not in runtime['original_desktops']]
            subprocess.run(['systemctl','--user','stop','local-mimin-spectrum.service'],capture_output=True)
            run('systemctl','--user','stop','plasma-plasmashell.service')
        try:
            for parent in (data/'share').iterdir():
                if parent.name in ['plasma','kwin','aurorae']:
                    # Copy only the packages in the archive, never the entire existing user tree.
                    for category in parent.iterdir():
                        if category.name=='local-panel-assets':put(category,home/'.local/share/plasma'/category.name)
                        else:
                            for item in category.iterdir():put(item,home/'.local/share'/parent.name/category.name/item.name)
                elif parent.name in ['desktop-audio-spectrum']:put(parent,home/'.local/share'/parent.name)
                else:
                    for item in parent.iterdir():put(item,home/'.local/share'/parent.name/item.name)
            put(data/'icons/Gruvbox-Plus-Dark',home/'.local/share/icons/Gruvbox-Plus-Dark')
            put(data/'config/kitty/venom',home/'.config/kitty/venom')
            put(data/'config/Kvantum',home/'.config/Kvantum')
            put(data/'config/systemd/user/local-mimin-spectrum.service',home/'.config/systemd/user/local-mimin-spectrum.service')
            for name,groups in settings['configs'].items():
                p=home/'.config'/name;c=ini(p)
                for group,values in groups.items():
                    if not c.has_section(group):c.add_section(group)
                    for key,value in values.items():c[group][key]=str(value)
                write_ini(p,c)
            executable=home/'.local/opt/kitty-0.50.0/bin/kitty'
            if not executable.exists() and args.apply:
                release=json.loads((data/'kitty-release.json').read_text());download=data/'kitty.txz'
                print('Descargando Kitty oficial '+release['version']+'; se verificará SHA256 antes de extraer.')
                urllib.request.urlretrieve(release['archive_url'],download)
                if digest(download)!=release['sha256']:raise RuntimeError('La descarga de Kitty no coincide con la suma verificada.')
                destination=home/'.local/opt/kitty-0.50.0';save(destination);destination.mkdir(parents=True,exist_ok=True);extract(download,destination)
            p=home/'.local/share/applications/venom-terminal.desktop';save(p);p.parent.mkdir(parents=True,exist_ok=True)
            def quote(value):return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
            p.write_text('[Desktop Entry]\nType=Application\nName=Terminal Venom\nComment=Kitty, Fish y Fastfetch con ilustración de Venom\nExec='+quote(executable)+' --class venom-terminal --title "Terminal Venom" --config '+quote(home/'.config/kitty/venom/kitty.conf')+'\nIcon=utilities-terminal\nTerminal=false\nCategories=System;TerminalEmulator;\nStartupWMClass=venom-terminal\nPath='+str(home)+'\n')
        finally:
            (backup/'runtime.json').write_text(json.dumps(runtime,indent=2))
            if args.apply:run('systemctl','--user','start','plasma-plasmashell.service')
        if args.apply:
            run('fc-cache','-f',str(home/'.local/share/fonts'))
            for language in ['es_ES.UTF-8','en_US.UTF-8']:
                env=os.environ.copy();env.update(LANG=language,LC_ALL=language);env.pop('LANGUAGE',None)
                run('kbuildsycoca6','--noincremental',env=env)
            # Wait for the freshly started panel service to be ready.
            import time
            for _ in range(40):
                result=subprocess.run(['qdbus-qt6','org.kde.plasmashell','/PlasmaShell','org.freedesktop.DBus.Peer.Ping'],capture_output=True)
                if result.returncode==0:break
                time.sleep(.2)
            js=(ROOT/'panel.js').read_text().replace('__PORTABLE_SETTINGS__',json.dumps(settings,ensure_ascii=False),1)
            result=run('qdbus-qt6','org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',js)
            layout=json.loads(result.strip());runtime['panel']=layout;(backup/'runtime.json').write_text(json.dumps(runtime,indent=2))
            run('systemctl','--user','stop','plasma-plasmashell.service')
            try:
                p=home/'.config/plasma-org.kde.plasma.desktop-appletsrc';c=ini(p);group='Containments]['+str(layout['panel'])+'][General'
                if not c.has_section(group):c.add_section(group)
                c[group]['AppletOrder']=';'.join(map(str,layout['order']))
                for index,module in enumerate(settings['modules']):
                    if module['plugin']=='org.kde.plasma.systemtray':
                        traygroup='Containments]['+str(layout['panel'])+'][Applets]['+str(layout['order'][index])+'][General'
                        if not c.has_section(traygroup):c.add_section(traygroup)
                        for key,value in module['groups']['General'].items():c[traygroup][key]=str(value)
                write_ini(p,c)
            finally:run('systemctl','--user','start','plasma-plasmashell.service')
            run('systemctl','--user','daemon-reload');run('systemctl','--user','enable','--now','local-mimin-spectrum.service')
            run('qdbus-qt6','org.kde.KWin','/KWin','org.kde.KWin.reconfigure')
            for effect in ['scale','squash']:run('qdbus-qt6','org.kde.KWin','/Effects','org.kde.kwin.Effects.unloadEffect',effect,check=False)
            for effect in ['fade','mimin-soft-minimize','minimizeall']:run('qdbus-qt6','org.kde.KWin','/Effects','org.kde.kwin.Effects.loadEffect',effect,check=False)
            run('qdbus-qt6','org.kde.KWin','/Effects','org.kde.kwin.Effects.reconfigureEffect','fade',check=False)
        print('Preparación aislada completa.' if args.stage_only else 'Escritorio aplicado. Abrir Terminal Venom; cerrar e iniciar sesión para completar estilos de aplicaciones ya abiertas.')
        print('Respaldo local:',backup)
        print('Mosaicos: Meta+T → tres columnas 25/50/25 %, separación 4 px (se ajustan por monitor).')
if __name__=='__main__':main()
