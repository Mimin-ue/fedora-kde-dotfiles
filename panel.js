// Portable settings are injected by install.py.
var settings = __PORTABLE_SETTINGS__;
var oldPanels = panels();
var p = new Panel();
p.location = 'top'; p.height = settings.panel_height; p.floating = false; p.opacity = 'translucent';
var widgets = [], order = [], clock = null, colorizer = null;
function value(key, v) {
    if (['launcherUrls','extraItems','hiddenItems','knownItems','shownItems'].indexOf(key) >= 0)
        return Array.isArray(v) ? v : (v ? v.split(',') : []);
    if (v === 'true') return true;
    if (v === 'false') return false;
    if (typeof v === 'string' && /^-?\d+$/.test(v)) return Number(v);
    return v;
}
settings.modules.forEach(function(module) {
    var w = p.addWidget(module.plugin);
    if (!w) throw new Error('No se pudo cargar ' + module.plugin);
    Object.keys(module.groups).forEach(function(group) {
        w.currentConfigGroup = group.split('][');
        Object.keys(module.groups[group]).forEach(function(key) {
            if (key !== 'clockPreset') w.writeConfig(key, value(key, module.groups[group][key]));
        });
    });
    w.reloadConfig(); widgets.push(w); order.push(w.id);
    if (module.plugin === 'org.kde.plasma.digitalclock') clock = w;
    if (module.plugin === 'luisbocanegra.panel.colorizer') colorizer = w;
});
if (clock && colorizer) {
    colorizer.currentConfigGroup = ['General'];
    var overrides = JSON.parse(colorizer.readConfig('configurationOverrides','{}'));
    overrides.associations = [{id:clock.id,name:'org.kde.plasma.digitalclock',presets:['clock-inset']}];
    colorizer.writeConfig('configurationOverrides',JSON.stringify(overrides));colorizer.reloadConfig();
}
// Apply the wallpaper to each real desktop/monitor already present on the new machine.
desktops().forEach(function(d) {
    d.wallpaperPlugin='org.kde.image';
    d.currentConfigGroup=['Wallpaper','org.kde.image','General'];
    d.writeConfig('Image','file://' + settings.home + '/.local/share/wallpapers/mimin-dunas-azul.png');
    d.reloadConfig();
});
// The previous layout is backed up by Python before any panel is removed.
oldPanels.forEach(function(old) { old.remove(); });
print(JSON.stringify({panel:p.id,order:order}));
