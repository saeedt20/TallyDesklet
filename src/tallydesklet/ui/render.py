"""Cairo/Pango card rendering shared with deterministic documentation previews."""
import cairo
from gi.repository import Pango, PangoCairo
from ..formatting import capacity, quantity
from ..i18n import numerals, rtl, tr
from .graphs import bar, graph
from .theme import color, geometry, palette, rounded


def text(cr, cfg, value, x, y, size=12, tint="#FFFFFF", bold=False, right=False, width=None, numeric=False):
    layout = PangoCairo.create_layout(cr)
    layout.set_auto_dir(False)
    layout.get_context().set_base_dir(Pango.Direction.LTR if numeric or not rtl(cfg) else Pango.Direction.RTL)
    font = Pango.FontDescription("Vazirmatn" if rtl(cfg) else "Sans")
    font.set_absolute_size(size*Pango.SCALE)
    font.set_weight(Pango.Weight.SEMIBOLD if bold else Pango.Weight.NORMAL)
    layout.set_font_description(font)
    layout.set_text(str(value), -1)
    if width is not None:
        layout.set_width(round(width*Pango.SCALE))
        layout.set_ellipsize(Pango.EllipsizeMode.END)
        layout.set_alignment(Pango.Alignment.RIGHT if right else Pango.Alignment.LEFT)
    actual = width if width is not None else layout.get_pixel_size()[0]
    cr.move_to(x-actual if right else x, y)
    color(cr, tint)
    PangoCairo.show_layout(cr, layout)
    return layout.get_pixel_size()


def chip(cr, x, y, tint):
    color(cr, tint)
    cr.set_line_width(1.5)
    rounded(cr, x+4, y+4, 16, 16, 2)
    cr.stroke()
    for offset in (7, 12, 17):
        for a, b in (((x+offset, y), (x+offset, y+4)), ((x+offset, y+20), (x+offset, y+24)),
                     ((x, y+offset), (x+4, y+offset)), ((x+20, y+offset), (x+24, y+offset))):
            cr.move_to(*a)
            cr.line_to(*b)
    cr.stroke()


def grid(cr, x, y, w, h, tint):
    color(cr, tint, .24)
    cr.set_line_width(.6)
    cr.set_dash((2, 4))
    for i in range(1, 5):
        cr.move_to(x+w*i/5, y)
        cr.line_to(x+w*i/5, y+h)
    cr.stroke()
    cr.set_dash(())
    cr.move_to(x, y+h)
    cr.line_to(x+w, y+h)
    cr.stroke()


def arrow(cr, x, y, tint, down):
    color(cr, tint)
    cr.set_line_width(1.8)
    end, start = (y+16, y) if down else (y, y+16)
    cr.move_to(x, start)
    cr.line_to(x, end)
    delta = -5 if down else 5
    cr.move_to(x-5, end+delta)
    cr.line_to(x, end)
    cr.line_to(x+5, end+delta)
    cr.stroke()


def draw_card(cr, cfg, sample=None, histories=None, maximum=1000, composited=False, factor=1):
    width, height, sections = geometry(cfg)
    a, p, is_rtl = cfg["appearance"], palette(cfg), rtl(cfg)
    compact = a["compact"]
    pad, end = 18, width-18
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.set_source_rgba(0, 0, 0, 0)
    cr.paint()
    cr.set_operator(cairo.OPERATOR_OVER)
    cr.scale(factor, factor)
    rounded(cr, .5, .5, width-1, height-1, 20)
    color(cr, p["background"], a["background_opacity"] if composited else 1)
    cr.fill_preserve()
    color(cr, p["line"], .6)
    cr.set_line_width(.7)
    cr.stroke()
    # A soft top edge adds depth without continuous redraws or wallpaper blur.
    color(cr, p["text"], .09)
    cr.move_to(24, 1)
    cr.line_to(width-24, 1)
    cr.stroke()
    def label(value, x, y, size=12, **kwargs):
        return text(cr, cfg, numerals(cfg,tr(cfg, value)), x, y, size, kwargs.pop("tint", p["text"]), **kwargs)
    def value(v, x, y, size=12, **kwargs):
        return text(cr, cfg, numerals(cfg, v), x, y, size, kwargs.pop("tint", p["text"]), numeric=True, **kwargs)
    chip(cr, end-24 if is_rtl else pad, 16, p["text"])
    label("System", end-35 if is_rtl else pad+35, 15, 18, right=is_rtl, bold=True)
    live = sample is not None and sample.cpu is not None
    color(cr, p["accent"] if live else p["muted"], 1 if live else .5)
    dot = 164 if is_rtl else 146
    cr.arc(dot, 27, 3, 0, 6.2832)
    cr.fill()
    label("Live" if live else "Warming up", dot-9 if is_rtl else dot+9, 19, 10,
          right=is_rtl, width=95, tint=p["accent"] if live else p["muted"])
    binary = a["units"] == "binary"
    now = sample.time if sample else 0
    cpu, down, up = histories or ((), (), ())
    y = 56
    for key, section_height in sections:
        color(cr, p["line"], .4)
        cr.set_line_width(.6)
        cr.move_to(pad, y-1)
        cr.line_to(end, y-1)
        cr.stroke()
        if key == "cpu":
            label("CPU", end if is_rtl else pad, y+8, 12, right=is_rtl, tint=p["muted"])
            percent = f"{sample.cpu:.0f}%" if sample and sample.cpu is not None else "—"
            value(percent, end if is_rtl else pad, y+26, 30 if compact else 36, bold=True, right=is_rtl, width=94)
            gx, gw, gh = (pad if is_rtl else pad+110), width-2*pad-110, 23 if compact else 34
            grid(cr, gx, y+22, gw, gh, p["line"])
            graph(cr, cpu, now, gx, y+22, gw, gh, 100, p["accent"], True)
            if not compact:
                label("60 s", gx+gw, y+58, 8, right=True, tint=p["muted"])
        elif key in ("ram", "disk"):
            metric = getattr(sample, key) if sample else None
            label("Memory" if key == "ram" else "System disk", end if is_rtl else pad, y+9,
                  12 if compact else 12.5, right=is_rtl, width=92, tint=p["muted"])
            used = capacity(metric.used, metric.total, binary) if metric else tr(cfg, "Unavailable") if sample else "—"
            percent = f"{metric.fraction*100:.0f}%" if metric else "—"
            tint = p["warning"] if metric and metric.fraction*100 >= cfg["alerts"][key+"_percent"] else p["accent"]
            amount_x = pad+46 if is_rtl else end-46
            value(used, amount_x, y+10, 10.5, right=not is_rtl, width=width-2*pad-145)
            value(percent, pad if is_rtl else end, y+8, 13, right=not is_rtl, width=42,
                  bold=True, tint=tint)
            bar(cr, pad, y+(30 if compact else 36), width-2*pad,
                metric.fraction if metric else 0, tint, p["line"], is_rtl)
        elif key == "network":
            label("Network", end if is_rtl else pad, y+8, 13, right=is_rtl, bold=True)
            rate = sample.network if sample else None
            ready = rate and rate.status == "Ready"
            if not ready:
                label(rate.status if rate else "Warming up", pad if is_rtl else end, y+10, 10,
                      right=not is_rtl, width=145, tint=p["muted"])
            half = (width-2*pad)/2
            for downloading, tint in ((True, p["accent"]), (False, p["secondary"])):
                on_right = downloading == is_rtl
                left = pad+half+10 if on_right else pad
                right_edge = end if on_right else pad+half-10
                arrow(cr, right_edge-6 if is_rtl else left+6, y+34, tint, downloading)
                label("Download" if downloading else "Upload", right_edge-22 if is_rtl else left+22,
                      y+32, 10.5, right=is_rtl, tint=p["muted"])
                speed = quantity(rate.down if downloading else rate.up, binary, True) if ready else "—"
                value(speed, right_edge if is_rtl else left, y+49, 16 if compact else 19,
                      right=is_rtl, bold=True, width=half-12)
            color(cr, p["line"], .4)
            cr.move_to(width/2, y+35)
            cr.line_to(width/2, y+68)
            cr.stroke()
            gy, gh = y+(70 if compact else 77), 9 if compact else 18
            grid(cr, pad, gy, width-2*pad, gh, p["line"])
            graph(cr, down, now, pad, gy, width-2*pad, gh, maximum, p["accent"], True)
            graph(cr, up, now, pad, gy, width-2*pad, gh, maximum, p["secondary"], dashed=True)
        elif key == "usage":
            half = (width-2*pad)/2
            for today, amount in ((True, sample.usage.daily if sample else None),
                                  (False, sample.usage.weekly if sample else None)):
                on_right = today == is_rtl
                left, right_edge = (pad+half+10, end) if on_right else (pad, pad+half-10)
                label("Today" if today else "This week", right_edge if is_rtl else left, y+9, 11,
                      right=is_rtl, tint=p["muted"])
                value(quantity(amount, binary), right_edge if is_rtl else left, y+27,
                      16 if compact else 20, right=is_rtl, bold=True, width=half-12)
            color(cr, p["line"], .4)
            cr.move_to(width/2, y+12)
            cr.line_to(width/2, y+section_height-15)
            cr.stroke()
        y += section_height
    return width, height
