# Implementation decisions

- Python 3 + distribution GTK 3/PyGObject, Cairo/Pango and psutil. Use system
  packages so native runtime dependencies follow the distribution.
- A managed GTK toplevel uses DESKTOP + keep-below by default, NORMAL + keep-above
  in top mode. Never override-redirect, never a dock strut. The widget rejects
  focus, skips taskbar/pager, and settings remain an ordinary focusable dialog.
- Logical design tokens live in `ui/theme.py`. The 320 × 330 canvas gives stable
  alignment as measurements change; Pango supplies the installed sans-serif
  font. Background alpha is separate from foreground text. Light-theme accent
  hues are darkened for contrast. Original SVG artwork is source, not generated
  bitmap branding. No wallpaper or desktop settings are modified by the app.
- Gear and preferences are native accessible GTK controls. The metric canvas
  exposes its live values and explanations as an accessible description and a
  tooltip. The main unfocused card is also recoverable through `--settings`.
- Version 0.2 adds two columns above Network: weekly usage on the left, daily on
  the right. Both combine observed download/upload byte deltas on the selected
  interface. Local calendar days and Sunday weeks use bounded daily buckets,
  with one-minute atomic XDG-state checkpoints and a final worker-thread flush.
  Baselines are not persisted, so closed-app traffic is excluded. Reconnect/reset
  and gaps over 15 seconds do not contribute estimated traffic. A cross-midnight
  valid delta belongs to the later sample's day. The tooltip explains partial periods.
- One sampler thread owns psutil's CPU baseline. UI receives a bounded queue;
  a blocked filesystem read cannot freeze GTK. Route subprocesses have one-second
  deadlines and run off the UI thread. A slow filesystem can delay metric updates
  until the OS call returns; no parallel unbounded worker creation is used.
- Linux CLOCK_BOOTTIME is monotonic and includes suspend. CPU and network warm
  up after gaps over 15 seconds. Timestamp histories retain at most 60 seconds
  and 256 entries. Upload/download share a floor of 1000 B/s and a slowly decaying
  peak scale; missing data creates gaps rather than fictional zeroes.
- Monitor connectors identify preferred screens. Coordinates remain signed;
  disappearing monitors and size changes clamp to an available work area.
  Header dragging uses pointer deltas and managed-window moves because Xfwm
  ignores standard WM move requests for DESKTOP windows. Position saves occur
  after release, never on every mouse event.
- Gio/GTK D-Bus application identity provides one instance per login bus.
  CLI version/help do not need a display. Desktop recovery commands go to the
  running process. Configuration and autostart use XDG user paths only.
- Version comes from the Python package; the build checks Debian changelog sync.
  Conventional debhelper metadata and a rootless dpkg-deb fallback share one
  staging implementation. The fallback is useful on desktops lacking debhelper.
- The owner selected MIT licensing and the GitHub username with a noreply
  address for public maintainer metadata.

## Primary references consulted

- [GTK 3 window API](https://docs.gtk.org/gtk3/class.Window.html) and
  [window-type hints](https://docs.gtk.org/gtk3/method.Window.set_type_hint.html).
- [psutil API](https://psutil.readthedocs.io/stable/), cross-checked against
  docstrings and actual named tuples (`available`, `free`, `bytes_recv`,
  `bytes_sent`, and `nowrap=False`).
- [Xfwm documentation](https://docs.xfce.org/xfce/xfwm4/introduction).
- [Autostart specification](https://specifications.freedesktop.org/autostart/latest/).
- [Debian control fields](https://www.debian.org/doc/debian-policy/ch-controlfields.html).

Current action releases were checked when preparing CI:
[checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) and
[upload-artifact v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2).

## Version 0.3 design

The card is 340 × 430 logical pixels, with a 320 × 342 compact alternative.
Hidden sections reduce height. A normal first installation uses Ember; upgrading
retains existing dark/light/custom-color preferences. Six palettes share the
same geometry and a minimum 4.5:1 solid-background foreground contrast. User
accent colors are adjusted when necessary for legibility; text opacity is never
reduced with the background. Unsupported compositing uses the opaque fallback.

CPU is the leading reading. RAM and filesystem occupancy use 36 segmented bars
with a fractional final segment, so fill remains consistent with the actual
percentage. Download and upload have labels/arrows and solid/dashed traces on
one shared scale. The final row holds Today/This week. Charts remain chronological
LTR while Persian text, section placement and bar fill are RTL.

Settings have native accessible controls, scrolled content/navigation and a fixed
footer. Persian reverses navigation and aligns labels to the logical start;
English remains LTR. The sidebar collapses to named icons on narrow logical
screens. CSD dialogs are clamped to the work area. Theme tiles are small Cairo
illustrations, explicitly distinct from the real sample-driven card.

Appearance/display drafts preview on the widget without writing preferences.
Apply validates and saves before adopting the configuration; failed saves keep
the prior state and draft. Closing asks before discarding edits, removes timers
and restores saved appearance. Sampling, notification opt-in and autostart never
change due to a preview. Original outline icons and process-private OFL font
registration keep branding and dependencies simple.

Gtk.Stack fades last 180 ms; control hover transitions last 150 ms. Reduced
motion disables these. There are no always-running animation timers or animated
fake readings. Memory/disk warnings use actual samples, sustained dwell, rearm
hysteresis and cooldown; notification connection/calls are asynchronous and are
cancelled on shutdown. Session policy controls whether accepted alerts appear.
