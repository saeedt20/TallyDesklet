"""Bounded, bilingual native preferences with reversible appearance preview."""
import copy
from pathlib import Path
from gi.repository import Gdk, GLib, Gtk, Pango
from .. import __version__, autostart
from ..config import validate
from ..i18n import rtl, tr, numerals
from .icons import symbol
from .theme import PALETTES, color, palette, rounded
from .render import text, grid


class ThemeTile(Gtk.Button):
    def __init__(self, key, owner):
        super().__init__()
        self.key, self.owner = key, owner
        self.get_style_context().add_class('theme-tile')
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(190, 94)
        self.canvas.connect('draw', self.draw)
        self.add(self.canvas)
        self.connect('clicked', lambda *_: owner.choose_theme(key))
        self.get_accessible().set_name(tr(owner.draft, PALETTES[key]['name']))

    def draw(self, widget, cr):
        p, c = PALETTES[self.key], self.owner.draft
        w, h = widget.get_allocated_width(), widget.get_allocated_height()
        chosen = self.owner.selected_theme() == self.key
        rounded(cr, 1, 1, w-2, h-2, 11)
        color(cr, p['background'])
        cr.fill_preserve()
        color(cr, p['accent'] if chosen else p['line'], 1 if chosen else .5)
        cr.set_line_width(2 if chosen else .7)
        cr.stroke()
        right = rtl(c)
        x = w-13 if right else 13
        text(cr, c, tr(c, p['name']), x, 9, 12, p['text'], bold=True, right=right, width=w-44)
        if chosen:
            text(cr, c, '✓', 13 if right else w-25, 9, 12, p['accent'])
        # Illustrative thumbnail, never treated as a live metric.
        grid(cr, 13, 33, w-26, 20, p['line'])
        color(cr, p['accent'])
        cr.set_line_width(1.6)
        for i, amount in enumerate((.7,.72,.25,.6,.55,.65,.38,.75,.6,.72,.65)):
            point = (13+(w-26)*i/10, 34+amount*16)
            cr.move_to(*point) if i == 0 else cr.line_to(*point)
        cr.stroke()
        text(cr, c, tr(c,p['subtitle']), x, 65, 9, p['muted'], right=right, width=w-26)
        return False


class SettingsDialog(Gtk.Dialog):
    PAGES = [('appearance','Appearance','applications-graphics-symbolic'),
             ('display','Display & language','preferences-desktop-locale-symbolic'),
             ('monitoring','Monitoring','utilities-system-monitor-symbolic'),
             ('desktop','Desktop & startup','preferences-desktop-display-symbolic'),
             ('alerts','Alerts','dialog-information-symbolic'),
             ('about','About','help-about-symbolic')]

    def __init__(self, app):
        super().__init__(title=tr(app.config,'TallyDesklet Settings'), transient_for=app.window, modal=False)
        self.app, self.draft = app, copy.deepcopy(app.config)
        self.set_application(app)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_resizable(True)
        self.header = Gtk.HeaderBar(title=tr(app.config,'TallyDesklet Settings'),show_close_button=True)
        self.set_titlebar(self.header)
        self.set_border_width(0)
        self.get_style_context().add_class('tally-settings')
        self.provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(),self.provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.labels, self.align_labels, self.buttons, self.combos = [], [], [], []
        self.preview_id = 0
        self.building = True
        self.cleaned = False
        self.bound_id = 0
        display = self.get_display()
        monitor = display.get_monitor_at_window(app.window.get_window()) if app.window.get_window() else display.get_primary_monitor()
        monitor = monitor or display.get_monitor(0)
        area = monitor.get_workarea()
        self.compact_navigation = area.width < 850
        self.set_default_size(min(750, max(320, area.width-64)), min(620, max(280, area.height-100)))
        self.close_button = self.add_button(tr(self.draft,'_Close'), Gtk.ResponseType.CLOSE)
        self.apply_button = self.add_button(tr(self.draft,'_Apply'), Gtk.ResponseType.APPLY)
        self.apply_button.get_style_context().add_class('suggested-action')
        self.buttons += [(self.close_button,'_Close'), (self.apply_button,'_Apply')]
        self.connect('response', self.respond)
        self.connect('delete-event', lambda *_: self.request_close() or True)
        self.connect('key-press-event', self.key_press)
        self.connect('destroy', self.cleanup)
        self.connect('configure-event',self.schedule_bounds)
        self.body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.get_content_area().pack_start(self.body, True, True, 0)
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=14)
        self.sidebar.set_size_request(42 if self.compact_navigation else 156,-1)
        self.sidebar.get_style_context().add_class('sidebar')
        brand = Gtk.Label(label='TD' if self.compact_navigation else 'TallyDesklet')
        brand.get_style_context().add_class('brand')
        self.sidebar.pack_start(brand,False,False,10)
        self.nav = {}
        self.nav_images = {}
        self.sidebar_scroll = Gtk.ScrolledWindow()
        self.sidebar_scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        self.sidebar_scroll.set_size_request(90 if self.compact_navigation else 200,-1)
        self.sidebar_scroll.add(self.sidebar)
        self.body.pack_start(self.sidebar_scroll,False,False,0)
        self.stack = Gtk.Stack()
        self.stack.set_hhomogeneous(True)
        self.stack.set_vhomogeneous(True)
        self.stack.set_transition_duration(180)
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE if self.draft['appearance']['reduced_motion'] else Gtk.StackTransitionType.CROSSFADE)
        self.body.pack_start(self.stack,True,True,0)
        for name,title,icon in self.PAGES:
            b = Gtk.Button()
            b.get_style_context().add_class('nav-button')
            row = Gtk.Box(spacing=9,margin=3)
            image = symbol({'appearance':'appearance','display':'language','monitoring':'monitor','desktop':'desktop','alerts':'bell','about':'info'}[name],palette(self.draft)['muted'])
            self.nav_images[name] = image
            row.pack_start(image,False,False,0)
            l = self.label('_Desktop & startup' if name=='desktop' else title, wrap=False, mnemonic=True)
            l.set_mnemonic_widget(b)
            row.pack_start(l,True,True,0)
            if self.compact_navigation:
                l.set_no_show_all(True)
                l.hide()
            b.set_tooltip_text(tr(self.draft,title))
            b.get_accessible().set_name(tr(self.draft,title))
            b.add(row)
            b.connect('clicked',lambda _,page=name:self.show_page(page))
            self.nav[name] = b
            self.sidebar.pack_start(b,False,False,0)
        self.sidebar.pack_end(Gtk.Label(label=__version__),False,False,8)
        self.appearance_page()
        self.display_page()
        self.monitoring_page()
        self.desktop_page()
        self.alerts_page()
        self.about_page()
        self.status = self.label('',wrap=True)
        self.status.set_no_show_all(True)
        self.status.set_margin_start(18)
        self.status.set_margin_end(18)
        self.status.set_margin_top(6)
        self.status.set_margin_bottom(6)
        self.get_content_area().pack_end(self.status,False,False,0)
        self.building = False
        self.localize()
        self.style()
        self.accent.set_sensitive(self.custom.get_active())
        self.show_page('appearance')
        self.show_all()
        self.status.hide()
        self.bound_id = GLib.idle_add(self.bound_to_monitor)
        if app.store.notice:
            self.set_status(app.store.notice)

    def schedule_bounds(self,*_):
        if not self.cleaned and not self.bound_id:
            self.bound_id = GLib.idle_add(self.bound_to_monitor)
        return False

    def bound_to_monitor(self):
        self.bound_id = 0
        if self.cleaned or not self.get_window():
            return False
        monitor = self.get_display().get_monitor_at_window(self.get_window())
        area = monitor.get_workarea()
        frame = self.get_window().get_frame_extents()
        x,y = self.get_position()
        fx = max(area.x,min(frame.x,area.x+area.width-frame.width))
        fy = max(area.y,min(frame.y,area.y+area.height-frame.height))
        if (fx,fy)!=(frame.x,frame.y):
            self.move(x+fx-frame.x,y+fy-frame.y)
        return False

    def label(self, title, wrap=True, mnemonic=False):
        l = Gtk.Label()
        l.set_xalign(0)
        l.set_line_wrap(wrap)
        l.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        if wrap:
            l.set_max_width_chars(42)
        l.set_text(tr(self.draft,title))
        l.set_use_underline(mnemonic)
        self.labels.append((l,title,mnemonic))
        self.align_labels.append(l)
        return l

    def button(self, title, callback):
        b = Gtk.Button(label=tr(self.draft,title))
        self.buttons.append((b,title))
        b.connect('clicked',callback)
        return b

    def page(self, name, title, hint=None):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14,margin=22)
        scroll.add(content)
        heading = self.label(title)
        heading.get_style_context().add_class('page-title')
        content.pack_start(heading,False,False,0)
        if hint:
            self.hint(content,hint)
        self.stack.add_named(scroll,name)
        return content

    def hint(self, content, title):
        l = self.label(title)
        l.get_style_context().add_class('hint')
        content.pack_start(l,False,False,0)
        return l

    def group(self, content):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=0)
        box.get_style_context().add_class('preferences-group')
        content.pack_start(box,False,False,0)
        return box

    def row(self, content, title, control):
        row = Gtk.Box(spacing=12,margin=12)
        l = self.label(title,mnemonic=True)
        l.set_mnemonic_widget(control)
        control.get_accessible().set_name(tr(self.draft,title).replace('_',''))
        row.pack_start(l,True,True,0)
        row.pack_end(control,False,False,0)
        control.set_valign(Gtk.Align.CENTER)
        content.pack_start(row,False,False,0)
        return row

    def combo(self, content, title, choices, selected):
        w = Gtk.ComboBoxText()
        w.set_hexpand(False)
        for key,label in choices:
            w.append(key,tr(self.draft,label))
        w.set_active_id(selected)
        self.combos.append((w,choices))
        self.row(content,title,w)
        w.connect('changed',self.changed)
        return w

    def switch(self, content, title, value):
        w = Gtk.Switch()
        w.set_active(value)
        self.row(content,title,w)
        w.connect('notify::active',self.changed)
        return w

    def slider(self, content, title, value, low, high, step, digits):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5,margin=12)
        l = self.label(title,mnemonic=True)
        w = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,low,high,step)
        w.set_digits(digits)
        w.set_value(value)
        w.set_hexpand(True)
        w.set_direction(Gtk.TextDirection.LTR)
        w.connect('format-value',lambda _,v:numerals(self.draft,f'{v:.{digits}f}'))
        l.set_mnemonic_widget(w)
        w.get_accessible().set_name(tr(self.draft,title))
        box.pack_start(l,False,False,0)
        box.pack_start(w,False,False,0)
        content.pack_start(box,False,False,0)
        w.connect('value-changed',self.changed)
        return w

    def appearance_page(self):
        page = self.page('appearance','Appearance','Display changes preview immediately. Close restores your saved preferences.')
        self.tiles = {}
        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_min_children_per_line(1)
        flow.set_max_children_per_line(2)
        flow.set_row_spacing(8)
        flow.set_column_spacing(8)
        flow.set_homogeneous(True)
        for key in PALETTES:
            tile = ThemeTile(key,self)
            self.tiles[key] = tile
            flow.add(tile)
        page.pack_start(flow,False,False,0)
        a = self.draft['appearance']
        g = self.group(page)
        self.opacity = self.slider(g,'Background opacity',a['background_opacity'],.35,1,.05,2)
        self.scale = self.slider(g,'Widget scale',a['scale'],.75,2,.25,2)
        self.compact = self.switch(g,'Compact layout',a['compact'])
        self.reduced = self.switch(g,'Reduce motion',a['reduced_motion'])
        g = self.group(page)
        self.custom = self.switch(g,'Custom accent color',a['custom_accent'])
        self.accent = Gtk.ColorButton()
        self.accent.set_use_alpha(False)
        rgba = Gdk.RGBA()
        rgba.parse(a['accent_color'])
        self.accent.set_rgba(rgba)
        self.accent.connect('color-set',self.changed)
        self.row(g,'Accent color',self.accent)
        page.pack_start(self.button('Restore theme colors',self.restore_colors),False,False,0)

    def display_page(self):
        page = self.page('display','Display & language')
        g = self.group(page)
        d,a = self.draft['display'],self.draft['appearance']
        self.language = self.combo(g,'Language',[('en','English'),('fa','فارسی')],d['language'])
        self.digits = self.combo(g,'Numerals',[('auto','Automatic'),('latin','Latin'),('persian','Persian')],d['digits'])
        self.units = self.combo(g,'Units',[('decimal','Decimal · GB, MB/s'),('binary','Binary · GiB, MiB/s')],a['units'])
        self.hint(page,'Visible sections')
        g = self.group(page)
        self.sections = {}
        for key,title in [('cpu','CPU'),('ram','Memory'),('disk','System disk'),('network','Network'),('usage','Today / This week')]:
            w = self.switch(g,title,d[key])
            w.connect('notify::active',self.visibility_changed,key)
            self.sections[key] = w
        self.hint(page,'Keep at least one section visible.')

    def monitoring_page(self):
        page = self.page('monitoring','Monitoring')
        g = self.group(page)
        c = self.draft
        self.interval = self.combo(g,'Refresh interval',[(str(v),f'{v:g} seconds') for v in (.5,1.,2.,5.)],str(float(c['sampling']['interval_seconds'])))
        names = self.app.window.sample.interfaces if self.app.window.sample else ()
        selected = c['network']['interface']
        names = sorted(set(names)|({selected} if selected!='auto' else set()))
        self.interface = self.combo(g,'Network interface',[('auto','Automatic · routed interface')]+[(v,v) for v in names],selected)
        self.week = self.combo(g,'Week starts on',[('5','Saturday'),('6','Sunday'),('0','Monday')],str(c['usage']['week_start']))
        self.path = Gtk.Entry(text=c['disk']['path'])
        self.path.set_direction(Gtk.TextDirection.LTR)
        self.path.connect('changed',self.changed)
        line = Gtk.Box(spacing=6)
        line.pack_start(self.path,True,True,0)
        browse = self.button('Choose folder',self.browse)
        browse.set_image(Gtk.Image.new_from_icon_name('folder-open-symbolic',Gtk.IconSize.BUTTON))
        line.pack_end(browse,False,False,0)
        self.row(g,'Disk path',line)
        self.hint(page,'Disk: capacity of the filesystem containing this path, not read/write speed.')
        self.hint(page,'Usage combines download + upload observed while TallyDesklet runs. Closed-app traffic is excluded.')
        self.hint(page,'Daily reset: local midnight. The selected weekday defines the calendar week.')

    def desktop_page(self):
        page = self.page('desktop','Desktop & startup')
        g = self.group(page)
        w = self.draft['window']
        self.locked = self.switch(g,'_Lock position',w['locked'])
        self.above = self.switch(g,'Always on _top',w['always_on_top'])
        self.workspaces = self.switch(g,'Show on all workspaces',w['all_workspaces'])
        self.startup = self.switch(g,'Start at login',autostart.enabled())
        if not Path('/usr/bin/tallydesklet').is_file():
            self.startup.set_sensitive(False)
            self.hint(page,'Install the .deb to enable a stable login startup command.')
        page.pack_start(self.button('Reset position',self.reset_position),False,False,0)

    def alerts_page(self):
        page = self.page('alerts','Alerts','Notifications are optional and require TallyDesklet to be running.')
        g = self.group(page)
        a = self.draft['alerts']
        self.alert_enabled = self.switch(g,'Enable notifications',a['enabled'])
        self.alert_ram = self.switch(g,'Memory warning',a['ram'])
        self.ram_threshold = self.slider(g,'Memory threshold',a['ram_percent'],50,99,1,0)
        self.alert_disk = self.switch(g,'Disk warning',a['disk'])
        self.disk_threshold = self.slider(g,'Disk threshold',a['disk_percent'],50,99,1,0)
        self.hint(page,'Warn after 60 seconds above the threshold. At most once per metric in 10 minutes.')

    def about_page(self):
        page = self.page('about','About')
        title = Gtk.Label(label='TallyDesklet')
        title.get_style_context().add_class('page-title')
        page.pack_start(title,False,False,0)
        page.pack_start(Gtk.Label(label=__version__),False,False,0)
        self.hint(page,'All measurements and preferences stay on your computer.')
        for caption,url in [('GitHub repository','https://github.com/saeedt20/TallyDesklet'),('Report an issue','https://github.com/saeedt20/TallyDesklet/issues')]:
            link = Gtk.LinkButton.new_with_label(url,tr(self.draft,caption))
            self.buttons.append((link,caption))
            page.pack_start(link,False,False,0)
        self.hint(page,'Credits & licenses')
        self.hint(page,'Created by saeedt20 · MIT license')
        self.hint(page,'Vazirmatn by the Vazirmatn Project Authors · SIL Open Font License 1.1')

    def selected_theme(self):
        return {'dark':'mint','light':'paper'}.get(self.draft['appearance']['theme'],self.draft['appearance']['theme'])

    def choose_theme(self,key):
        self.draft['appearance']['theme'] = key
        self.custom.set_active(False)
        rgba = Gdk.RGBA()
        rgba.parse(PALETTES[key]['accent'])
        self.accent.set_rgba(rgba)
        self.changed()

    def restore_colors(self,*_):
        self.choose_theme(self.selected_theme())

    def read_controls(self):
        c = copy.deepcopy(self.draft)
        a,d = c['appearance'],c['display']
        rgba = self.accent.get_rgba()
        a.update(background_opacity=self.opacity.get_value(),scale=self.scale.get_value(),
                 compact=self.compact.get_active(),reduced_motion=self.reduced.get_active(),
                 custom_accent=self.custom.get_active(),units=self.units.get_active_id(),
                 accent_color='#{:02X}{:02X}{:02X}'.format(*(round(v*255) for v in (rgba.red,rgba.green,rgba.blue))))
        d.update(language=self.language.get_active_id(),digits=self.digits.get_active_id())
        d.update({key:w.get_active() for key,w in self.sections.items()})
        c['sampling']['interval_seconds'] = float(self.interval.get_active_id())
        c['network']['interface'] = self.interface.get_active_id()
        c['disk']['path'] = self.path.get_text().strip()
        c['usage']['week_start'] = int(self.week.get_active_id())
        c['window'].update(locked=self.locked.get_active(),always_on_top=self.above.get_active(),all_workspaces=self.workspaces.get_active())
        c['alerts'].update(enabled=self.alert_enabled.get_active(),ram=self.alert_ram.get_active(),disk=self.alert_disk.get_active(),
                           ram_percent=round(self.ram_threshold.get_value()),disk_percent=round(self.disk_threshold.get_value()))
        return c

    def changed(self,*_):
        if self.building or self.cleaned:
            return
        before = self.draft['display']['language']
        self.draft = self.read_controls()
        if before != self.draft['display']['language']:
            self.localize()
        self.style()
        for tile in self.tiles.values():
            tile.queue_draw()
        self.accent.set_sensitive(self.custom.get_active())
        self.stack.set_transition_type(Gtk.StackTransitionType.NONE if self.reduced.get_active() else Gtk.StackTransitionType.CROSSFADE)
        self.set_status(tr(self.draft,'Preview only · press Apply to save'))
        if self.preview_id:
            GLib.source_remove(self.preview_id)
        self.preview_id = GLib.timeout_add(120,self.preview)

    def preview(self):
        self.preview_id = 0
        c = copy.deepcopy(self.app.config)
        c['appearance'] = copy.deepcopy(self.draft['appearance'])
        c['display'] = copy.deepcopy(self.draft['display'])
        self.app.window.preview_config = validate(c)
        self.app.window.apply()
        return False

    def localize(self):
        self.building = True
        direction = Gtk.TextDirection.RTL if rtl(self.draft) else Gtk.TextDirection.LTR
        def direct(w):
            w.set_direction(direction)
            if isinstance(w,Gtk.Container):
                for child in w.get_children():
                    direct(child)
        direct(self)
        self.set_title(tr(self.draft,'TallyDesklet Settings'))
        self.header.set_title(tr(self.draft,'TallyDesklet Settings'))
        for label,title,mnemonic in self.labels:
            label.set_text(tr(self.draft,title))
            label.set_use_underline(mnemonic)
        for label in self.align_labels:
            label.set_xalign(0)
        for b,title in self.buttons:
            b.set_label(tr(self.draft,title))
            b.set_use_underline(True)
        for w,choices in self.combos:
            active = w.get_active_id()
            w.remove_all()
            for key,label in choices:
                w.append(key,tr(self.draft,label))
            w.set_active_id(active)
        for key,tile in self.tiles.items():
            tile.get_accessible().set_name(tr(self.draft,PALETTES[key]['name']))
        self.path.set_direction(Gtk.TextDirection.LTR)
        for scale in (self.opacity,self.scale,self.ram_threshold,self.disk_threshold):
            scale.set_direction(Gtk.TextDirection.LTR)
        for name,title,_ in self.PAGES:
            self.nav[name].set_tooltip_text(tr(self.draft,title))
            self.nav[name].get_accessible().set_name(tr(self.draft,title))
        self.building = False

    def style(self):
        p = palette(self.draft)
        for name,image in self.nav_images.items():
            fresh = symbol({'appearance':'appearance','display':'language','monitoring':'monitor','desktop':'desktop','alerts':'bell','about':'info'}[name],p['muted'])
            image.set_from_pixbuf(fresh.get_pixbuf())
        duration = 0 if self.draft['appearance']['reduced_motion'] else 150
        font = 'Vazirmatn' if rtl(self.draft) else 'Sans'
        css = f'''
        .tally-settings {{ background: {p['background']}; color: {p['text']}; font-family: "{font}"; font-size: 13px; }}
        .tally-settings decoration {{ background: {p['background']}; border: 1px solid {p['line']}; box-shadow: none; }}
        .tally-settings headerbar {{ background: {p['panel']}; color: {p['text']}; border: none; box-shadow: none; }}
        .tally-settings label {{ color: {p['text']}; }}
        .tally-settings .hint {{ color: {p['muted']}; font-size: 11px; }}
        .tally-settings .brand {{ font-size: 17px; font-weight: 600; }}
        .tally-settings .page-title {{ font-size: 22px; font-weight: 600; }}
        .tally-settings .sidebar {{ background: {p['panel']}; border-radius: 14px; padding: 8px; }}
        .tally-settings .preferences-group {{ background: {p['panel']}; border-radius: 12px; }}
        .tally-settings button {{ background: {p['panel']}; background-image: none; color: {p['text']}; border: 1px solid alpha({p['line']},.5); border-radius: 8px; padding: 7px 10px; box-shadow: none; text-shadow: none; transition: background-color {duration}ms ease, border-color {duration}ms ease; }}
        .tally-settings button:hover {{ background: mix({p['panel']},{p['accent']},.13); border-color: {p['accent']}; }}
        .tally-settings button:focus {{ outline: 2px solid {p['accent']}; outline-offset: 1px; }}
        .tally-settings button.nav-button {{ background: transparent; border-color: transparent; padding: 8px 2px; }}
        .tally-settings button.nav-button.active {{ background: alpha({p['accent']},.17); border-color: alpha({p['accent']},.5); }}
        .tally-settings button.theme-tile {{ background: transparent; border: none; padding: 0; }}
        .tally-settings flowboxchild {{ padding: 0; }}
        .tally-settings button.suggested-action {{ background: {p['accent']}; color: {p['background']}; border-color: {p['accent']}; font-weight: 600; }}
        .tally-settings button.suggested-action label {{ color: {p['background']}; }}
        .tally-settings entry, .tally-settings combobox button {{ background: {p['background']}; color: {p['text']}; border-color: alpha({p['line']},.6); min-height: 24px; }}
        .tally-settings switch {{ background: {p['line']}; border: none; min-width: 38px; min-height: 20px; }}
        .tally-settings switch:checked {{ background: {p['accent']}; }}
        .tally-settings switch slider {{ background: {p['text']}; border: none; min-width: 18px; min-height: 18px; }}
        .tally-settings scale trough {{ background: {p['line']}; min-height: 4px; border: none; }}
        .tally-settings scale highlight {{ background: {p['accent']}; border: none; }}
        .tally-settings scale slider {{ background: {p['accent']}; border: none; min-width: 14px; min-height: 14px; }}
        .tally-settings separator {{ background: alpha({p['line']},.35); }}
        '''
        self.provider.load_from_data(css.encode())

    def show_page(self,name):
        self.stack.set_visible_child_name(name)
        for page,b in self.nav.items():
            context = b.get_style_context()
            context.add_class('active') if page==name else context.remove_class('active')

    def set_status(self,message):
        self.status.set_text(message)
        self.status.show()

    def visibility_changed(self,widget,_,key):
        if self.building or any(w.get_active() for w in self.sections.values()):
            return
        widget.set_active(True)
        self.set_status(tr(self.draft,'Keep at least one section visible.'))

    def browse(self,*_):
        dialog = Gtk.FileChooserDialog(title=tr(self.draft,'Choose folder'),transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.set_direction(self.get_direction())
        dialog.add_buttons(tr(self.draft,'Cancel'),Gtk.ResponseType.CANCEL,tr(self.draft,'Choose'),Gtk.ResponseType.ACCEPT)
        if Path(self.path.get_text()).is_dir():
            dialog.set_filename(self.path.get_text())
        if dialog.run()==Gtk.ResponseType.ACCEPT:
            self.path.set_text(dialog.get_filename())
        dialog.destroy()

    def reset_position(self,*_):
        self.app.reset_position()
        self.draft['window'].update(position=None,monitor='primary')
        self.app.window.reposition()

    def sync_window_options(self):
        self.building = True
        c = self.app.config['window']
        self.draft['window'] = copy.deepcopy(c)
        self.locked.set_active(c['locked'])
        self.above.set_active(c['always_on_top'])
        self.workspaces.set_active(c['all_workspaces'])
        self.building = False

    def dirty(self):
        c = self.read_controls()
        c['window']['position'] = self.app.config['window']['position']
        c['window']['monitor'] = self.app.config['window']['monitor']
        return validate(c)!=self.app.config or self.startup.get_active()!=autostart.enabled()

    def request_close(self):
        if self.dirty():
            dialog = Gtk.MessageDialog(transient_for=self,modal=True,message_type=Gtk.MessageType.QUESTION,
                                       text=tr(self.draft,'Unsaved changes'))
            dialog.set_direction(self.get_direction())
            dialog.add_button(tr(self.draft,'Keep editing'),Gtk.ResponseType.CANCEL)
            dialog.add_button(tr(self.draft,'Discard changes'),Gtk.ResponseType.ACCEPT)
            dialog.set_default_response(Gtk.ResponseType.CANCEL)
            answer = dialog.run()
            dialog.destroy()
            if answer!=Gtk.ResponseType.ACCEPT:
                return True
        self.destroy()
        return True

    def key_press(self,widget,event):
        if event.state & Gdk.ModifierType.MOD1_MASK:
            key = Gdk.keyval_to_lower(event.keyval)
            if key == Gdk.KEY_a:
                self.respond(self,Gtk.ResponseType.APPLY)
                return True
            if key == Gdk.KEY_d:
                self.show_page('desktop')
                return True
            if self.stack.get_visible_child_name() == 'desktop':
                if key == Gdk.KEY_t:
                    self.above.set_active(not self.above.get_active())
                    return True
                if key == Gdk.KEY_l:
                    self.locked.set_active(not self.locked.get_active())
                    return True
        if event.keyval==Gdk.KEY_Escape:
            return self.request_close()
        return False

    def respond(self,dialog,response):
        if response!=Gtk.ResponseType.APPLY:
            self.request_close()
            return
        c = self.read_controls()
        path = c['disk']['path']
        if not path.startswith('/') or not Path(path).exists():
            self.show_page('monitoring')
            self.set_status(tr(self.draft,'Choose an existing absolute path. Its containing filesystem will be measured.'))
            return
        c['window']['position'] = self.app.config['window']['position']
        c['window']['monitor'] = self.app.config['window']['monitor']
        old_startup = autostart.enabled()
        try:
            if self.startup.get_active()!=old_startup:
                autostart.set_enabled(self.startup.get_active())
            self.app.apply_config(validate(c))
        except (OSError,ValueError) as error:
            if autostart.enabled()!=old_startup:
                try:
                    autostart.set_enabled(old_startup)
                except (OSError,ValueError):
                    pass
            self.set_status(tr(self.draft,'Could not save preferences')+': '+str(error))
            return
        if self.preview_id:
            GLib.source_remove(self.preview_id)
            self.preview_id = 0
        self.draft = copy.deepcopy(self.app.config)
        self.app.window.preview_config = None
        self.app.window.apply()
        self.set_status(tr(self.draft,'Preferences applied.'))

    def cleanup(self,*_):
        self.cleaned = True
        Gtk.StyleContext.remove_provider_for_screen(self.get_screen(),self.provider)
        if self.preview_id:
            GLib.source_remove(self.preview_id)
            self.preview_id = 0
        if self.bound_id:
            GLib.source_remove(self.bound_id)
            self.bound_id = 0
        if self.app.window:
            self.app.window.preview_config = None
            self.app.window.apply()
