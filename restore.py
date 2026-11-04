#!/usr/bin/env python3
"""Restore one local backup created by install.py. Never close user sessions."""
from pathlib import Path
import argparse,configparser,json,os,shutil,subprocess

def run(*a,check=True):return subprocess.run(a,check=check,capture_output=True,text=True).stdout

def main():
    p=argparse.ArgumentParser(description='Restaurar un respaldo local de este escritorio.')
    p.add_argument('backup',type=Path,help='Carpeta de respaldo mostrada al instalar.')
    args=p.parse_args();b=args.backup.resolve();manifest=json.loads((b/'manifest.json').read_text());runtime=json.loads((b/'runtime.json').read_text());live=not runtime['stage_only']
    if os.geteuid()==0:raise SystemExit('Ejecutar sin sudo.')
    if live:
        for effect in ['mimin-soft-minimize']:run('qdbus-qt6','org.kde.KWin','/Effects','org.kde.kwin.Effects.unloadEffect',effect,check=False)
        for uid in runtime.get('created_desktops',[]):run('qdbus-qt6','org.kde.KWin','/VirtualDesktopManager','org.kde.KWin.VirtualDesktopManager.removeDesktop',uid,check=False)
        run('systemctl','--user','stop','local-mimin-spectrum.service',check=False)
        if not runtime.get('spectrum_enabled'):run('systemctl','--user','disable','local-mimin-spectrum.service',check=False)
        run('systemctl','--user','stop','plasma-plasmashell.service')
    try:
        for name,item in reversed(list(manifest.items())):
            target=Path(name)
            if target.is_symlink():raise RuntimeError('Revisar enlace antes de restaurar: '+name)
            if item['directory'] or (not item['existed'] and target.is_dir()):
                if target.exists():shutil.rmtree(target)
                if item['existed']:shutil.copytree(b/item['copy'],target,symlinks=True)
            elif item['existed']:
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(b/item['copy'],target)
            else:target.unlink(missing_ok=True)
    finally:
        if live:run('systemctl','--user','start','plasma-plasmashell.service')
    if live:
        run('systemctl','--user','daemon-reload')
        if runtime.get('spectrum_active'):run('systemctl','--user','start','local-mimin-spectrum.service')
        run('fc-cache','-f',str(Path.home()/'.local/share/fonts'))
        run('kbuildsycoca6','--noincremental')
        run('qdbus-qt6','org.kde.KWin','/KWin','org.kde.KWin.reconfigure')
        c=configparser.ConfigParser(interpolation=None);c.read(Path.home()/'.config/kwinrc')
        for effect,default in [('fade',False),('scale',True),('squash',True),('minimizeall',False),('mimin-soft-minimize',False)]:
            enabled=c.getboolean('Plugins',effect+'Enabled',fallback=default)
            run('qdbus-qt6','org.kde.KWin','/Effects','org.kde.kwin.Effects.loadEffect' if enabled else 'org.kde.kwin.Effects.unloadEffect',effect,check=False)
    print('Respaldo restaurado. Volver a iniciar sesión para completar los cambios de estilo.')
if __name__=='__main__':main()
