"""Native GTK behavior on an explicitly isolated X11 test display."""
import os
import unittest
if os.environ.get('TALLYDESKLET_GUI_TESTS')!='1':
    raise unittest.SkipTest('Run scripts/gui-check.sh for isolated GTK tests')
import copy
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace as NS
from unittest.mock import patch
import gi
gi.require_version('Gtk','3.0')
gi.require_version('Gdk','3.0')
gi.require_version('PangoCairo','1.0')
from gi.repository import Gio,GLib,Gtk,Gdk,PangoCairo
from tallydesklet.config import ConfigStore,validate
from tallydesklet.ui.widget import MeterWindow
from tallydesklet.ui.settings import SettingsDialog
from tallydesklet.ui.theme import PALETTES,geometry


def settle(seconds=.18):
    context=GLib.MainContext.default()
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        while context.pending():context.iteration(False)
        time.sleep(.005)


class NativePreferencesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=Gtk.Application(application_id='org.tallydesklet.UiTests',flags=Gio.ApplicationFlags.NON_UNIQUE)
        cls.app.register(None)
        cls.app.settings=None
        cls.app.save=lambda:None
        cls.app.reset_position=lambda:None
        cls.app.quit=lambda:None

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env=patch.dict(os.environ,{'XDG_CONFIG_HOME':self.temp.name,'XDG_STATE_HOME':self.temp.name})
        self.env.start();self.addCleanup(self.env.stop)
        self.app.config=validate({})
        self.app.store=ConfigStore(Path(self.temp.name)/'config.json')
        self.app.store.save(self.app.config)
        def apply(c):
            self.app.store.save(c)
            self.app.config=copy.deepcopy(c)
            self.app.window.apply()
        self.app.apply_config=apply
        self.app.window=MeterWindow(self.app)
        self.dialog=SettingsDialog(self.app)
        self.app.settings=self.dialog
        settle()

    def tearDown(self):
        self.dialog.destroy()
        self.app.settings=None
        self.app.window.destroy()
        settle(.04)

    def test_all_palettes_preview_without_saving_and_cancel_restores(self):
        original=self.app.store.path.read_bytes()
        for key in PALETTES:
            self.dialog.choose_theme(key)
            settle()
            self.assertEqual(self.app.window.config['appearance']['theme'],key)
            self.assertEqual(self.app.config['appearance']['theme'],'ember')
            self.assertEqual(self.app.store.path.read_bytes(),original)
        self.dialog.destroy();settle()
        self.assertIsNone(self.app.window.preview_config)
        self.assertEqual(self.app.window.config['appearance']['theme'],'ember')
        self.assertEqual(self.dialog.preview_id,0)

    def test_apply_persian_language_numerals_and_layout_then_english(self):
        d=self.dialog
        d.language.set_active_id('fa');settle()
        self.assertEqual(d.get_direction(),Gtk.TextDirection.RTL)
        self.assertEqual(self.app.window.config['display']['language'],'fa')
        side=NS(x=d.sidebar.translate_coordinates(d.body,0,0)[0]);stack=NS(x=d.stack.translate_coordinates(d.body,0,0)[0])
        self.assertGreater(side.x,stack.x)
        d.show_page('display');settle(.25)
        heading=d.stack.get_child_by_name('display').get_child().get_child().get_children()[0]
        self.assertEqual(heading.get_direction(),Gtk.TextDirection.RTL)
        offset=heading.get_layout_offsets()[0]
        ink=heading.get_layout().get_pixel_extents()[0]
        self.assertGreater(offset+ink.x+ink.width,heading.get_allocated_width()-30)
        d.digits.set_active_id('latin')
        d.choose_theme('ocean');d.respond(d,Gtk.ResponseType.APPLY);settle()
        self.assertEqual(self.app.store.load()['display']['digits'],'latin')
        self.assertEqual(self.app.config['appearance']['theme'],'ocean')
        self.assertFalse(d.dirty())
        d.language.set_active_id('en');settle()
        self.assertEqual(d.get_direction(),Gtk.TextDirection.LTR)
        self.assertLess(d.sidebar.translate_coordinates(d.body,0,0)[0],d.stack.translate_coordinates(d.body,0,0)[0])
        d.respond(d,Gtk.ResponseType.APPLY)
        self.assertEqual(self.app.store.load()['display']['language'],'en')

    def test_invalid_disk_path_keeps_saved_config_and_draft(self):
        original=self.app.store.path.read_bytes()
        self.dialog.path.set_text('/fixture/not-a-real-path')
        self.dialog.respond(self.dialog,Gtk.ResponseType.APPLY)
        self.assertEqual(self.app.store.path.read_bytes(),original)
        self.assertEqual(self.dialog.path.get_text(),'/fixture/not-a-real-path')
        self.assertEqual(self.dialog.stack.get_visible_child_name(),'monitoring')
        self.assertIn('existing',self.dialog.status.get_text())

    def test_existing_disk_path_with_trailing_space_is_saved_literally(self):
        path = Path(self.temp.name) / 'disk '
        path.mkdir()
        self.dialog.path.set_text(str(path))
        self.dialog.respond(self.dialog, Gtk.ResponseType.APPLY)
        self.assertEqual(self.app.store.load()['disk']['path'], str(path))
        self.assertFalse(self.dialog.dirty())

    def test_appearance_preview_keeps_current_desktop_position_and_flags(self):
        window = self.app.window
        self.app.config['window']['position'] = [100,200]
        window.apply()
        self.dialog.choose_theme('ocean'); settle()
        self.app.config['window'].update(position=None, always_on_top=True, locked=True)
        window.apply(); settle()
        self.assertEqual(window.config['appearance']['theme'], 'ocean')
        self.assertEqual(window.config['window'], self.app.config['window'])
        self.assertNotEqual(tuple(window.get_position()), (100,200))

    def test_failed_save_preserves_config_and_preview(self):
        self.dialog.choose_theme('lilac');settle()
        before=copy.deepcopy(self.app.config)
        with patch.object(self.app.store,'save',side_effect=OSError('fixture disk full')):
            self.dialog.respond(self.dialog,Gtk.ResponseType.APPLY)
        self.assertEqual(self.app.config,before)
        self.assertEqual(self.dialog.selected_theme(),'lilac')
        self.assertTrue(self.dialog.dirty())
        self.assertIn('fixture disk full',self.dialog.status.get_text())

    def test_compact_sections_and_last_visible_section(self):
        self.dialog.compact.set_active(True)
        for key,w in self.dialog.sections.items():w.set_active(False)
        settle()
        self.assertTrue(any(w.get_active() for w in self.dialog.sections.values()))
        self.dialog.respond(self.dialog,Gtk.ResponseType.APPLY);settle()
        expected=geometry(self.app.config)
        scale=self.app.config['appearance']['scale']
        self.assertEqual(self.app.window.canvas.get_size_request(),(round(expected[0]*scale),round(expected[1]*scale)))

    def test_reduce_motion_and_custom_accent_are_reversible(self):
        self.dialog.reduced.set_active(True)
        self.dialog.custom.set_active(True)
        settle()
        self.assertEqual(self.dialog.stack.get_transition_type(),Gtk.StackTransitionType.NONE)
        self.assertTrue(self.dialog.accent.get_sensitive())
        self.dialog.restore_colors();settle()
        self.assertFalse(self.dialog.custom.get_active())
        self.assertFalse(self.dialog.accent.get_sensitive())

    def test_sampling_and_alert_choices_do_not_apply_before_save(self):
        d=self.dialog
        d.interval.set_active_id('5.0')
        d.week.set_active_id('5')
        d.alert_enabled.set_active(True)
        self.assertEqual(self.app.config['sampling']['interval_seconds'],1)
        self.assertFalse(self.app.config['alerts']['enabled'])
        d.respond(d,Gtk.ResponseType.APPLY)
        c=self.app.store.load()
        self.assertEqual(c['sampling']['interval_seconds'],5)
        self.assertEqual(c['usage']['week_start'],5)
        self.assertTrue(c['alerts']['enabled'])

    def test_language_and_large_fonts_keep_controls_inside_window(self):
        settings=Gtk.Settings.get_default()
        before=settings.get_property('gtk-xft-dpi')
        try:
            settings.set_property('gtk-xft-dpi',round(96*1.4*1024))
            for language in ('en','fa'):
                self.dialog.language.set_active_id(language)
                for name,_,_ in self.dialog.PAGES:
                    self.dialog.show_page(name);settle(.22)
                    size=NS(width=self.dialog.get_allocated_width(),height=self.dialog.get_allocated_height())
                    monitor=self.dialog.get_display().get_monitor_at_window(self.dialog.get_window())
                    area=monitor.get_workarea()
                    self.assertLessEqual(size.width,area.width)
                    self.assertLessEqual(size.height,area.height)
                    for b in (self.dialog.apply_button,self.dialog.close_button):
                        point=b.translate_coordinates(self.dialog,0,0)
                        self.assertGreaterEqual(point[0],0)
                        self.assertLessEqual(point[0]+b.get_allocated_width(),size.width)
                        self.assertLessEqual(point[1]+b.get_allocated_height(),size.height)
                    scroller=self.dialog.stack.get_visible_child()
                    self.assertEqual(scroller.get_policy()[1],Gtk.PolicyType.AUTOMATIC)
        finally:settings.set_property('gtk-xft-dpi',before)

    def test_keyboard_actions_apply_desktop_flags_without_focus_ambiguity(self):
        d=self.dialog
        def press(key):
            return d.key_press(d,NS(keyval=key,state=Gdk.ModifierType.MOD1_MASK))
        self.assertTrue(press(Gdk.KEY_d))
        self.assertEqual(d.stack.get_visible_child_name(),'desktop')
        self.assertTrue(press(Gdk.KEY_t))
        self.assertTrue(press(Gdk.KEY_l))
        self.assertTrue(press(Gdk.KEY_a))
        self.assertTrue(self.app.store.load()['window']['locked'])
        self.assertTrue(self.app.store.load()['window']['always_on_top'])

    def test_bundled_persian_font_is_registered(self):
        names={f.get_name() for f in PangoCairo.FontMap.get_default().list_families()}
        self.assertIn('Vazirmatn',names)

    def test_close_unchanged_dialog_and_timer_cleanup(self):
        self.assertFalse(self.dialog.dirty())
        self.dialog.request_close();settle()
        self.assertTrue(self.dialog.cleaned)
        self.assertEqual(self.dialog.preview_id,0)


class NativeNotificationTests(unittest.TestCase):
    XML='''<node><interface name="org.freedesktop.Notifications"><method name="Notify">
      <arg type="s" direction="in"/><arg type="u" direction="in"/><arg type="s" direction="in"/>
      <arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="as" direction="in"/>
      <arg type="a{sv}" direction="in"/><arg type="i" direction="in"/><arg type="u" direction="out"/>
      </method></interface></node>'''
    def setUp(self):
        from tallydesklet.alerts import Notifier
        self.calls=[];self.fail=False;self.status=[]
        self.app=NS(config=validate({'alerts':{'enabled':True},'display':{'language':'fa'}}),
                    settings=NS(set_status=self.status.append))
        self.bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
        self.node=Gio.DBusNodeInfo.new_for_xml(self.XML)
        self.reg=self.bus.register_object('/org/freedesktop/Notifications',self.node.interfaces[0],self.method,None,None)
        self.bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',
            GLib.Variant('(su)',('org.freedesktop.Notifications',0)),None,Gio.DBusCallFlags.NONE,2000,None)
        self.client=Notifier(self.app)
    def tearDown(self):
        self.client.close();settle(.04)
        self.bus.unregister_object(self.reg)
        self.bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','ReleaseName',
            GLib.Variant('(s)',('org.freedesktop.Notifications',)),None,Gio.DBusCallFlags.NONE,2000,None)
    def method(self,connection,sender,path,interface,method,params,invocation):
        self.calls.append(params.unpack())
        if self.fail:invocation.return_dbus_error('org.freedesktop.Notifications.Error','Synthetic unavailable service')
        else:invocation.return_value(GLib.Variant('(u)',(41,)))
    def test_real_protocol_uses_localized_text_and_correct_desktop_identity(self):
        self.client.send('ram',95);settle(.25)
        self.assertEqual(len(self.calls),1)
        call=self.calls[0]
        self.assertEqual(call[3],'مصرف بالای رم')
        self.assertEqual(call[4],'۹۵٪')
        self.assertEqual(call[6]['desktop-entry'],'tallydesklet')
        self.assertEqual(call[5],[])
        self.assertFalse(self.client.pending)
    def test_default_optout_and_queued_optout_do_not_send(self):
        self.app.config['alerts']['enabled']=False
        self.client.send('ram',95);settle()
        self.assertEqual(self.calls,[])
        self.app.config['alerts']['enabled']=True
        self.client.send('ram',95)
        self.app.config['alerts']['enabled']=False
        settle(.25);self.assertEqual(self.calls,[])
    def test_failed_service_is_reported_and_shutdown_cancels(self):
        self.fail=True
        self.client.send('disk',95);settle(.25)
        self.assertTrue(self.status)
        self.assertFalse(self.client.pending)
        self.calls.clear()
        self.client.close();self.client.send('disk',95);settle()
        self.assertEqual(self.calls,[])
