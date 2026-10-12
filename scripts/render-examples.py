#!/usr/bin/python3
"""Real GTK previews with fixed example data on a private X display; no collector."""
import math
from pathlib import Path
import sys,time
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import cairo,gi
gi.require_version('Gtk','3.0');gi.require_version('Gdk','3.0');gi.require_version('PangoCairo','1.0')
from gi.repository import Gio,GLib,Gtk
from tallydesklet.config import validate
from tallydesklet.metrics import Capacity,Sample
from tallydesklet.network import Rate
from tallydesklet.usage import UsageTotals
from tallydesklet.ui.settings import SettingsDialog
from tallydesklet.ui.widget import MeterWindow
from tallydesklet.ui.theme import PALETTES


def settle():
    until=time.monotonic()+.3
    while time.monotonic()<until:
        while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
        time.sleep(.005)


def capture(widget,path):
    settle()
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,widget.get_allocated_width(),widget.get_allocated_height())
    widget.draw(cairo.Context(surface));surface.write_to_png(str(path))
    print('Synthetic-data native GTK preview:',path.name)


def main():
    output=ROOT/'docs/examples';output.mkdir(parents=True,exist_ok=True)
    Gtk.Settings.get_default().set_property('gtk-theme-name','Adwaita')
    Gtk.Settings.get_default().set_property('gtk-font-name','Sans 10')
    app=Gtk.Application(application_id='org.tallydesklet.Examples',flags=Gio.ApplicationFlags.NON_UNIQUE)
    app.register(None);app.store=SimpleNamespace(notice=None);app.save=lambda:None;app.settings=None
    app.apply_config=lambda _:None
    images=[]
    for theme,language,compact,name in [(k,'en',False,k) for k in PALETTES]+[('ember','fa',False,'persian'),('ember','en',True,'compact')]:
        app.config=validate({'appearance':{'theme':theme,'scale':2.,'compact':compact},'display':{'language':language}})
        app.window=MeterWindow(app)
        for second in range(61):
            cpu=5+7*abs(math.sin(second*.23))+2*abs(math.cos(second*.61))
            down=4000+2500*math.sin(second*.17);up=700+600*math.cos(second*.31)
            if second==60:cpu,down,up=8,2800,800
            app.window.update(Sample(float(second),cpu,Capacity(1_500_000_000,8_200_000_000,6_700_000_000),
                Capacity(209_900_000_000,490_600_000_000,280_700_000_000),
                Rate('example0',down,up,'Ready'),('example0',),0,UsageTotals(114_000_000,2_100_000_000,'2026-10-10')))
        filename='dark' if name=='ember' else 'light' if name=='paper' else name
        capture(app.window,output/(filename+'.png'))
        if name in PALETTES:images.append(output/(filename+'.png'))
        if name in ('ember','persian'):
            settings=SettingsDialog(app)
            capture(settings,output/('settings-fa.png' if language=='fa' else 'settings.png'))
            if language=='fa':
                settings.show_page('display');capture(settings,output/'settings-display.png')
                settings.show_page('desktop');capture(settings,output/'settings-desktop.png')
                settings.show_page('about');capture(settings,output/'about-fa.png')
            settings.destroy();settle()
        app.window.destroy();settle()
    # A gallery consists solely of actual synthetic-data widget captures.
    from gi.repository import GdkPixbuf
    surfaces=[cairo.ImageSurface.create_from_png(str(path)) for path in images]
    thumb_width=272;thumb_height=344;gap=16
    gallery=cairo.ImageSurface(cairo.FORMAT_ARGB32,3*thumb_width+4*gap,2*thumb_height+3*gap)
    cr=cairo.Context(gallery);cr.set_source_rgb(.08,.09,.11);cr.paint()
    for i,surface in enumerate(surfaces):
        cr.save();cr.translate(gap+(i%3)*(thumb_width+gap),gap+(i//3)*(thumb_height+gap))
        cr.scale(thumb_width/surface.get_width(),thumb_height/surface.get_height())
        cr.set_source_surface(surface,0,0);cr.paint();cr.restore()
    gallery.write_to_png(str(output/'themes.png'))

if __name__=='__main__':main()
