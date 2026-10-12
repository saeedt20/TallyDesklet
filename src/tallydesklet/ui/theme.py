"""Shared palettes, contrast-safe colors and logical geometry; no GTK imports."""
import copy
WIDTH, HEIGHT, PADDING, RADIUS = 340, 430, 18, 20
CYAN = "#70C7D5"
PALETTES = {
    "ember": {"name": "Ember", "subtitle": "Charcoal & warm orange", "background": "#191D21", "panel": "#23282E", "text": "#F5F2EE", "muted": "#B9BEC5", "line": "#59616B", "accent": "#FF985C", "secondary": "#D0B199", "light": False},
    "mint": {"name": "Mint", "subtitle": "Quiet mint green", "background": "#17231F", "panel": "#21332B", "text": "#F0F7F3", "muted": "#B4C8BE", "line": "#526D60", "accent": "#73DDB0", "secondary": "#A4CEDB", "light": False},
    "ocean": {"name": "Ocean", "subtitle": "Deep blue & cyan", "background": "#152333", "panel": "#203247", "text": "#EEF5FC", "muted": "#ACC1D5", "line": "#4A657D", "accent": "#62CEE4", "secondary": "#A9B9FD", "light": False},
    "lilac": {"name": "Lilac", "subtitle": "Soft violet", "background": "#241F2D", "panel": "#332B40", "text": "#F5F0FB", "muted": "#C5B9D3", "line": "#70607E", "accent": "#C5A5FA", "secondary": "#E5B7D2", "light": False},
    "paper": {"name": "Paper", "subtitle": "Warm white & amber", "background": "#F8F4ED", "panel": "#EEE8DE", "text": "#292720", "muted": "#655F55", "line": "#BFB5A6", "accent": "#A64912", "secondary": "#686050", "light": True},
    "silver": {"name": "Silver", "subtitle": "Cool gray & blue", "background": "#EFF2F6", "panel": "#E1E7EE", "text": "#222C39", "muted": "#526172", "line": "#ABB7C5", "accent": "#245FB7", "secondary": "#67508D", "light": True},
}
THEMES = {**PALETTES, "dark": PALETTES["mint"], "light": PALETTES["paper"]}


def rgb(value):
    return tuple(int(value[i:i+2], 16) / 255 for i in (1, 3, 5))


def luminance(value):
    components = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb(value)]
    return sum(c*w for c, w in zip(components, (.2126, .7152, .0722)))


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high+.05)/(low+.05)


def readable(value, background, ratio=4.5):
    if contrast(value, background) >= ratio:
        return value
    original = rgb(value)
    target = (0., 0., 0.) if luminance(background) > .4 else (1., 1., 1.)
    for step in range(1, 101):
        mixed = "#" + "".join(f"{round(255*(c+(t-c)*step/100)):02X}" for c, t in zip(original, target))
        if contrast(mixed, background) >= ratio:
            return mixed
    return "#000000" if target[0] == 0 else "#FFFFFF"


def palette(config):
    appearance = config["appearance"]
    result = copy.copy(THEMES[appearance["theme"]])
    if appearance["custom_accent"]:
        result["accent"] = readable(appearance["accent_color"], result["background"])
    result["warning"] = "#A92C38" if result["light"] else "#FF7E87"
    return result


def geometry(config):
    width = 320 if config["appearance"]["compact"] else WIDTH
    heights = {"cpu": 82, "ram": 57, "disk": 57, "network": 109, "usage": 69}
    if config["appearance"]["compact"]:
        heights = {"cpu": 64, "ram": 45, "disk": 45, "network": 85, "usage": 47}
    visible = [(name, height) for name, height in heights.items() if config["display"][name]]
    return width, 56 + sum(h for _, h in visible), visible


def color(cr, value, alpha=1):
    cr.set_source_rgba(*rgb(value), alpha)


def rounded(cr, x, y, w, h, radius):
    from math import pi
    radius = min(radius, w/2, h/2)
    cr.new_sub_path()
    for cx, cy, start in ((x+w-radius, y+radius, -pi/2), (x+w-radius, y+h-radius, 0),
                          (x+radius, y+h-radius, pi/2), (x+radius, y+radius, pi)):
        cr.arc(cx, cy, radius, start, start+pi/2)
    cr.close_path()
