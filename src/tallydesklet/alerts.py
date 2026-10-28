"""Optional sustained thresholds and bounded native desktop notifications."""
from dataclasses import dataclass
import math


@dataclass
class ThresholdState:
    above_since: float | None = None
    last_attempt: float = float('-inf')
    latched: bool = False


class AlertEngine:
    def __init__(self):
        self.states = {name:ThresholdState() for name in ('ram','disk')}
        self.previous = None

    def reset(self, before, after):
        for name, state in self.states.items():
            if any(before[key] != after[key] for key in ('enabled', name, name+'_percent')):
                state.above_since = None
                state.latched = False

    def evaluate(self, now, sample, config):
        a = config['alerts']
        gap = self.previous is None or now-self.previous>15 or now<=self.previous
        self.previous = now
        if not a['enabled']:
            for state in self.states.values():
                state.above_since = None
                state.latched = False
            return []
        result = []
        for name,state in self.states.items():
            metric = getattr(sample,name)
            threshold = a[name+'_percent']/100
            fraction = metric.fraction if metric else None
            if not a[name] or fraction is None or not math.isfinite(fraction) or gap:
                state.above_since = None
                continue
            if fraction < threshold-.05:
                state.above_since = None
                state.latched = False
            elif fraction < threshold:
                state.above_since = None
            elif not state.latched:
                if state.above_since is None:
                    state.above_since = now
                elif now-state.above_since>=60 and now-state.last_attempt>=600:
                    state.last_attempt = now
                    state.latched = True
                    result.append((name,round(fraction*100)))
        return result


class Notifier:
    """Lazy freedesktop session-bus calls, cancellable and opt-in checked twice."""
    def __init__(self, app):
        from gi.repository import Gio
        self.app, self.bus = app,None
        self.cancellable = Gio.Cancellable()
        self.closed = False
        self.pending = set()

    def send(self, key, percent):
        from gi.repository import Gio
        if self.closed or not self.app.config['alerts']['enabled'] or key in self.pending:
            return
        self.pending.add(key)
        if self.bus:
            self.dispatch(key,percent)
        else:
            Gio.bus_get(Gio.BusType.SESSION,self.cancellable,self.connected,(key,percent))

    def connected(self, source, result, data):
        from gi.repository import Gio, GLib
        try:
            self.bus = Gio.bus_get_finish(result)
        except GLib.Error:
            self.pending.discard(data[0])
            self.notice()
            return
        self.dispatch(*data)

    def dispatch(self, key, percent):
        from gi.repository import Gio, GLib
        from .i18n import numerals,tr
        c = self.app.config
        if self.closed or not c['alerts']['enabled'] or not c['alerts'][key]:
            self.pending.discard(key)
            return
        title = tr(c,'High memory usage' if key=='ram' else 'Disk is getting full')
        body = numerals(c,f'{percent}%')
        args = GLib.Variant('(susssasa{sv}i)',('TallyDesklet',0,'tallydesklet',title,body,[],
                {'urgency':GLib.Variant('y',1),'desktop-entry':GLib.Variant('s','tallydesklet')},-1))
        self.bus.call('org.freedesktop.Notifications','/org/freedesktop/Notifications',
            'org.freedesktop.Notifications','Notify',args,GLib.VariantType.new('(u)'),
            Gio.DBusCallFlags.NONE,3000,self.cancellable,self.finished,key)

    def finished(self, source, result, key):
        from gi.repository import GLib
        self.pending.discard(key)
        try:
            source.call_finish(result)
        except GLib.Error:
            self.notice()

    def notice(self):
        if not self.closed and self.app.settings:
            from .i18n import tr
            self.app.settings.set_status(tr(self.app.config,'Notifications unavailable'))

    def close(self):
        self.closed = True
        self.cancellable.cancel()
        self.pending.clear()
