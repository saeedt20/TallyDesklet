"""Meaningful migration, contrast, language, accounting and alert behavior."""
from datetime import date
from types import SimpleNamespace as NS
import unittest
from tallydesklet.config import DEFAULTS,validate
from tallydesklet.i18n import numerals,rtl,tr
from tallydesklet.ui.theme import PALETTES,contrast,geometry,palette
from tallydesklet.alerts import AlertEngine
from tallydesklet.usage import UsageTracker
from tallydesklet.metrics import Capacity


class RedesignConfigTests(unittest.TestCase):
    def test_legacy_preferences_and_custom_color_survive(self):
        for mode in ('dark','light'):
            c=validate({'appearance':{'theme':mode,'accent_color':'#123ABC','background_opacity':.5,'scale':1.5},
                        'window':{'position':[-100,40],'locked':True}})
            self.assertEqual(c['appearance']['theme'],mode)
            self.assertTrue(c['appearance']['custom_accent'])
            self.assertEqual(c['appearance']['accent_color'],'#123ABC')
            self.assertEqual(c['window']['position'],[-100,40])
            self.assertTrue(c['window']['locked'])
            self.assertFalse(c['alerts']['enabled'])
            self.assertEqual(c['usage']['week_start'],6)

    def test_invalid_language_digits_alerts_and_empty_sections(self):
        c=validate({'display':{'language':'xx','digits':'arabic','cpu':False,'ram':False,'disk':False,'network':False,'usage':False},
                    'alerts':{'ram_percent':500,'disk_percent':True,'enabled':'true'},'usage':{'week_start':100}})
        self.assertEqual((c['display']['language'],c['display']['digits']),('en','auto'))
        self.assertTrue(c['display']['cpu'])
        self.assertEqual((c['alerts']['ram_percent'],c['alerts']['disk_percent']),(99,90))
        self.assertFalse(c['alerts']['enabled'])
        self.assertEqual(c['usage']['week_start'],6)

    def test_geometry_reacts_to_sections_and_compact_without_scaling_screen(self):
        c=validate({})
        self.assertEqual(geometry(c)[:2],(340,430))
        c['appearance']['compact']=True
        self.assertEqual(geometry(c)[:2],(320,342))
        c['display']['network']=False
        self.assertEqual(geometry(c)[:2],(320,257))

    def test_palette_selection_and_custom_accent_do_not_mutate_shared_data(self):
        c=validate({})
        p=palette(c)
        p['background']='#000000'
        self.assertEqual(palette(c)['background'],'#191D21')
        c['appearance'].update(theme='paper',custom_accent=True,accent_color='#FFFFFF')
        self.assertGreaterEqual(contrast(palette(c)['accent'],palette(c)['background']),4.5)

    def test_curated_text_and_graph_colors_are_readable(self):
        self.assertEqual(len(PALETTES),6)
        for name,p in PALETTES.items():
            for key in ('text','muted','accent','secondary'):
                with self.subTest(theme=name,color=key):
                    self.assertGreaterEqual(contrast(p[key],p['background']),4.5)


class LocalizationTests(unittest.TestCase):
    def test_bilingual_directions_independent_digits(self):
        c=validate({'display':{'language':'fa'}})
        self.assertTrue(rtl(c))
        self.assertEqual(tr(c,'Memory'),'حافظهٔ رم')
        self.assertEqual(numerals(c,'18.5%'),'۱۸٫۵٪')
        self.assertEqual(tr(c,'_Lock position'),'_قفل موقعیت')
        c['display']['digits']='latin'
        self.assertEqual(numerals(c,'۱۸٫۵٪'),'18.5%')
        c['display'].update(language='en',digits='persian')
        self.assertFalse(rtl(c))
        self.assertEqual(tr(c,'Memory'),'Memory')
        self.assertEqual(numerals(c,'18.5%'),'۱۸٫۵٪')

    def test_paths_and_interface_names_are_not_translated(self):
        c=validate({'display':{'language':'fa'}})
        self.assertEqual(tr(c,'eth0'),'eth0')
        self.assertEqual(tr(c,'/media/data'),' /media/data'.strip())
        self.assertEqual(tr(c,'1 seconds'),'۱ ثانیه')


class WeekStartTests(unittest.TestCase):
    def test_saturday_sunday_monday_recalculate_existing_buckets(self):
        d=date(2026,10,12)
        t=UsageTracker(d,{'2026-10-09':1,'2026-10-10':2,'2026-10-11':4,'2026-10-12':8})
        self.assertEqual(t.totals(d,week_start=5).weekly,14)
        self.assertEqual(t.totals(d,week_start=6).weekly,12)
        self.assertEqual(t.totals(d,week_start=0).weekly,8)
        self.assertEqual(t.totals(d).daily,8)
        self.assertEqual(len(t.document()['days']),4)


class AlertTests(unittest.TestCase):
    def setUp(self):
        self.cfg=validate({'alerts':{'enabled':True}})
        self.engine=AlertEngine()

    def sample(self,at,ram=.95,disk=.95):
        s=NS(ram=Capacity(round(ram*1000),1000,0) if ram is not None else None,
             disk=Capacity(round(disk*1000),1000,0) if disk is not None else None)
        return self.engine.evaluate(at,s,self.cfg)

    def test_off_by_default(self):
        self.cfg=validate({})
        for at in range(100):self.assertEqual(self.sample(at),[])

    def test_sustained_load_and_single_notification_per_episode(self):
        for at in range(61):self.assertEqual(self.sample(at),[])
        self.assertEqual(self.sample(61),[('ram',95),('disk',95)])
        for at in range(62,720):self.assertEqual(self.sample(at),[])

    def test_transient_spikes_reset_the_sixty_second_window(self):
        for at in range(50):self.sample(at)
        self.sample(50,ram=.5,disk=.5)
        for at in range(51,111):self.assertEqual(self.sample(at),[])
        self.assertEqual(self.sample(111),[('ram',95),('disk',95)])

    def test_missing_data_resume_and_optout_do_not_trigger(self):
        for at in range(50):self.sample(at)
        self.assertEqual(self.sample(50,ram=None,disk=None),[])
        self.assertEqual(self.sample(300),[])
        for at in range(301,361):self.assertEqual(self.sample(at),[])
        self.cfg['alerts']['enabled']=False
        self.assertEqual(self.sample(361),[])

    def test_rearming_and_cooldown_do_not_spam(self):
        for at in range(62):self.sample(at)
        self.sample(62,ram=.5,disk=.5)
        for at in range(63,661):self.assertEqual(self.sample(at),[])
        self.assertEqual(self.sample(661),[('ram',95),('disk',95)])

    def test_disabled_metric_is_independent(self):
        self.cfg['alerts']['disk']=False
        for at in range(61):self.assertEqual(self.sample(at),[])
        self.assertEqual(self.sample(61),[('ram',95)])
