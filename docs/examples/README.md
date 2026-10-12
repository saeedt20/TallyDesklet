# Native interface previews

All PNGs here are captures of the actual TallyDesklet GTK/Cairo implementation
with **fixed synthetic example readings**, `example0` as an illustrative interface,
and temporary XDG directories. `scripts/render-examples.py` starts no collector.
The running application always collects real readings.

`dark.png` is Ember, `light.png` is Paper; Mint/Ocean/Lilac/Silver have named
captures. `themes.png` combines these six actual captures. `persian.png` shows
RTL with Vazirmatn, `compact.png` the compact layout, and settings captures show
English and Persian appearance/display/desktop pages.

Generate only on a private D-Bus/Xvfb session with temporary XDG preferences.
The package explicitly whitelists reviewed preview filenames. Real desktop/live
verification captures and resource logs remain ignored private local artifacts.
