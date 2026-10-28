"""Compact Cairo card with native GTK interaction and desktop hints."""
from gi.repository import Gdk, GLib, Gtk

from ..formatting import capacity, quantity
from ..i18n import numerals, rtl, tr
from ..fonts import load as load_fonts
from .render import draw_card
from .icons import symbol
from ..history import GraphScale, History
from ..position import place
from .theme import geometry, palette


class MeterWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="TallyDesklet")
        self.app = app
        self.sample = None
        self.preview_config = None
        load_fonts()
        self.cpu, self.down, self.up = History(), History(), History()
        self.net_scale = GraphScale()
        self.position_timer = 0
        self.dragging = False
        self.drag_origin = None
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        self.get_style_context().add_class("tallydesklet")
        css = Gtk.CssProvider()
        css.load_from_data(b"window.tallydesklet { background: transparent; } "
                           b".tallydesklet-gear { background: transparent; border: none; box-shadow: none; padding: 0; min-width: 24px; min-height: 24px; }")
        Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self.canvas = Gtk.DrawingArea()
        self.canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK |
                               Gdk.EventMask.POINTER_MOTION_MASK)
        self.canvas.connect("draw", self.draw_card)
        self.canvas.connect("button-press-event", self.button_press)
        self.canvas.connect("motion-notify-event", self.drag_motion)
        self.canvas.connect("button-release-event", self.drag_end)
        self.canvas.set_has_tooltip(True)
        self.canvas.connect("query-tooltip", self.tooltip)
        self.canvas.get_accessible().set_name("TallyDesklet")
        self.fixed.put(self.canvas, 0, 0)
        self.gear = Gtk.Button()
        self.gear.set_image(Gtk.Image.new_from_icon_name("emblem-system-symbolic", Gtk.IconSize.MENU))
        self.gear.get_style_context().add_class("tallydesklet-gear")
        self.gear.set_tooltip_text("TallyDesklet menu")
        self.gear.get_accessible().set_name("TallyDesklet settings and actions")
        self.gear.connect("clicked", lambda button: self.app.open_settings())
        self.fixed.put(self.gear, 280, 12)
        self.connect("delete-event", lambda *_: app.quit() or True)
        screen.connect("monitors-changed", lambda *_: self.reposition())
        screen.connect("size-changed", lambda *_: self.reposition())
        screen.connect("composited-changed", lambda *_: self.queue_draw())
        self.connect("destroy", self.cleanup)
        self.apply()
        self.show_all()
        GLib.idle_add(self.reposition)

    @property
    def config(self):
        if self.preview_config:
            return dict(self.app.config, appearance=self.preview_config['appearance'],
                        display=self.preview_config['display'])
        return self.app.config

    def apply(self):
        scale = self.config["appearance"]["scale"]
        width, height, _ = geometry(self.config)
        w, h = round(width * scale), round(height * scale)
        self.canvas.set_size_request(w, h)
        self.fixed.set_size_request(w, h)
        self.fixed.move(self.gear, round((14 if rtl(self.config) else width-42) * scale), round(14 * scale))
        self.gear.set_size_request(round(26*scale), round(26*scale))
        self.gear.set_image(symbol("gear",palette(self.config)["muted"],round(20*scale)))
        self.resize(w, h)
        settings = self.config["window"]
        above = settings["always_on_top"]
        # Managed DESKTOP windows survive Show Desktop without reserving a strut.
        self.set_keep_above(False)
        self.set_keep_below(False)
        self.set_type_hint(Gdk.WindowTypeHint.NORMAL if above else Gdk.WindowTypeHint.DESKTOP)
        self.set_keep_above(above)
        self.set_keep_below(not above)
        self.stick() if settings["all_workspaces"] else self.unstick()
        self.gear.get_style_context().add_class("tallydesklet-gear")
        fg = Gdk.RGBA()
        fg.parse(palette(self.config)["muted"])
        self.gear.override_color(Gtk.StateFlags.NORMAL, fg)
        self.gear.set_tooltip_text(tr(self.config, "Settings"))
        self.canvas.get_accessible().set_name("TallyDesklet")
        self.gear.get_accessible().set_name(tr(self.config, "Settings"))
        self.reposition()
        self.queue_draw()

    def monitor_key(self, monitor):
        display = self.get_display()
        screen = self.get_screen()
        for i in range(display.get_n_monitors()):
            if display.get_monitor(i) == monitor:
                return screen.get_monitor_plug_name(i) or f"monitor-{i}"
        return "primary"

    def reposition(self):
        display = self.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        for i in range(display.get_n_monitors()):
            candidate = display.get_monitor(i)
            if self.monitor_key(candidate) == self.config["window"]["monitor"]:
                monitor = candidate
                break
        if monitor is None:
            return False
        area = monitor.get_workarea()
        scale = self.config["appearance"]["scale"]
        position = place((area.x, area.y, area.width, area.height),
                         (round(geometry(self.config)[0] * scale), round(geometry(self.config)[1] * scale)),
                         self.config["window"]["position"], self.config["window"]["margin"])
        self.move(*position)
        return False

    def save_position(self):
        self.position_timer = 0
        self.dragging = False
        self.app.config["window"]["position"] = list(self.get_position())
        monitor = self.get_display().get_monitor_at_window(self.get_window())
        self.app.config["window"]["monitor"] = self.monitor_key(monitor)
        self.app.save()
        return False

    def cleanup(self, *_):
        if hasattr(self,"menu"):
            self.menu.destroy()
        if self.position_timer:
            GLib.source_remove(self.position_timer)
            self.position_timer = 0

    def button_press(self, widget, event):
        if event.button == 3:
            self.show_menu(event)
            return True
        if event.button == 1 and event.y < 55*self.config["appearance"]["scale"] and not self.config["window"]["locked"]:
            self.dragging = True
            self.drag_origin = (event.x_root, event.y_root, *self.get_position())
            # Xfwm refuses _NET_WM_MOVERESIZE for DESKTOP windows. Keep this a
            # managed window and move on pointer motion instead of changing type.
            self.canvas.grab_add()
            return True
        return False

    def drag_motion(self, widget, event):
        if self.dragging and self.drag_origin:
            rx, ry, x, y = self.drag_origin
            self.move(round(x + event.x_root-rx), round(y + event.y_root-ry))
            return True
        return False

    def drag_end(self, widget, event):
        if self.dragging and event.button == 1:
            self.canvas.grab_remove()
            self.drag_origin = None
            self.dragging = False
            # Let the final ConfigureNotify arrive before reading/saving position.
            self.position_timer = GLib.timeout_add(150, self.save_position)
            return True
        return False

    def show_menu(self, event=None):
        if hasattr(self,'menu'):
            self.menu.destroy()
        menu = Gtk.Menu()
        menu.get_style_context().add_class('tally-menu')
        p = palette(self.config)
        provider = Gtk.CssProvider()
        provider.load_from_data(f".tally-menu {{background:{p['background']};color:{p['text']};border:1px solid {p['line']};border-radius:10px;padding:6px;}} .tally-menu menuitem {{padding:7px 10px;color:{p['text']};border-radius:6px;}} .tally-menu menuitem:hover {{background:alpha({p['accent']},.18);}} .tally-menu label {{color:{p['text']};}}".encode())
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(),provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        menu.connect("destroy",lambda *_:Gtk.StyleContext.remove_provider_for_screen(self.get_screen(),provider))
        settings = Gtk.MenuItem(label=tr(self.config, "Settings") + "…")
        settings.connect("activate", lambda *_: self.app.open_settings())
        menu.append(settings)
        for key, label in (("locked", "Lock position"), ("always_on_top", "Always on top")):
            item = Gtk.CheckMenuItem(label=tr(self.config, label))
            item.set_active(self.config["window"][key])
            item.connect("toggled", self.toggle, key)
            menu.append(item)
        for label, action in (("Reset position", self.app.reset_position), ("Quit", self.app.quit)):
            item = Gtk.MenuItem(label=tr(self.config, label))
            item.connect("activate", lambda _, fn=action: fn())
            menu.append(item)
        direction = Gtk.TextDirection.RTL if rtl(self.config) else Gtk.TextDirection.LTR
        menu.set_direction(direction)
        for item in menu.get_children():
            item.set_direction(direction)
            for child in item.get_children():
                child.set_direction(direction)
        menu.show_all()
        self.menu = menu
        if event:
            menu.popup_at_pointer(event)
        else:
            menu.popup_at_widget(self.gear, Gdk.Gravity.SOUTH_EAST, Gdk.Gravity.NORTH_EAST, None)

    def toggle(self, item, key):
        import copy
        config = copy.deepcopy(self.app.config)
        config["window"][key] = item.get_active()
        try:
            self.app.apply_config(config)
            if self.app.settings:
                self.app.settings.sync_window_options()
        except OSError as error:
            self.app.store.notice = str(error)

    def update(self, sample):
        previous = self.sample
        if previous and previous.network.interface != sample.network.interface:
            self.down.points.clear()
            self.up.points.clear()
        self.sample = sample
        self.cpu.append(sample.time, sample.cpu)
        self.down.append(sample.time, sample.network.down)
        self.up.append(sample.time, sample.network.up)
        peak = max([v for history in (self.down, self.up) for _, v in history.points if v is not None] or [0])
        self.net_scale.update(peak, sample.time-previous.time if previous else 1)
        self.canvas.get_accessible().set_description(self.summary())
        self.canvas.queue_draw()

    def summary(self):
        cfg = self.config
        t = lambda v: tr(cfg,v)
        if not self.sample:
            return t('Waiting for the first system sample')
        s = self.sample
        binary = cfg['appearance']['units']=='binary'
        lines = [f"{t('CPU')}: {numerals(cfg,f'{s.cpu:.0f}%')}" if s.cpu is not None else t('Warming up')]
        for name,metric in (('Memory',s.ram),('System disk',s.disk)):
            lines.append(f"{t(name)}: {numerals(cfg,capacity(metric.used,metric.total,binary))}; "
                         f"{t('Available')}: {numerals(cfg,quantity(metric.available,binary))}"
                         if metric else f"{t(name)}: {t('Unavailable')}")
        lines += [f"{t('Filesystem containing')}: {cfg['disk']['path']}",
                  f"{t('Today')}: {numerals(cfg,quantity(s.usage.daily,binary))}; "
                  f"{t('This week')}: {numerals(cfg,quantity(s.usage.weekly,binary))}",
                  t('Usage combines download + upload observed while TallyDesklet runs. Closed-app traffic is excluded.'),
                  t('Daily reset: local midnight. The selected weekday defines the calendar week.'),
                  f"{t('Week starts on')}: {t({0:'Monday',5:'Saturday',6:'Sunday'}[cfg['usage']['week_start']])}",
                  f"{t('Interface')}: {s.network.interface or cfg['network']['interface']} · {t(s.network.status)}",
                  f"{t('Download')}: {numerals(cfg,quantity(s.network.down,binary,True))}; "
                  f"{t('Upload')}: {numerals(cfg,quantity(s.network.up,binary,True))}"]
        if s.usage.started_on:
            lines.append(f"{t('Usage tracking started')}: {s.usage.started_on}")
        if s.usage.notice:
            lines.append(s.usage.notice)
        return '\n'.join(lines)

    def tooltip(self, widget, x, y, keyboard, tooltip):
        tooltip.set_text(self.summary())
        return True

    def draw_card(self, widget, cr):
        draw_card(cr, self.config, self.sample,
                  (self.cpu.points, self.down.points, self.up.points), self.net_scale.value,
                  self.get_screen().is_composited(), self.config["appearance"]["scale"])
        return False
