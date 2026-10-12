# TallyDesklet 0.3.0 — Themes and bilingual redesign

A redesigned native desktop card and settings for Linux Mint 22.3 Xfce/X11.

- Six complete themes: Ember, Mint, Ocean, Lilac, Paper and Silver.
- Readable CPU history, segmented RAM/filesystem bars, distinct network traces,
  and Today/This week totals; normal 340 × 430 or compact 320 × 342 logical pixels.
- Persian RTL and English LTR, bundled Vazirmatn, independently selectable numerals.
- Scrolled settings with mirrored sidebar, responsive icon navigation, bounded
  About/credits, GitHub links and native controls styled to match the card.
- Reversible appearance preview; Apply saves and Close/Discard restores saved
  preferences. Sampling, startup and notifications change only after Apply.
- Per-section visibility, custom accent/reset, restrained fades and reduced motion.
- Saturday, Sunday or Monday week starts without resetting retained daily totals.
- Optional sustained RAM/disk notifications, off by default: 60 seconds above
  threshold, ten-minute cooldown and five-point rearm hysteresis.
- Upgrade retains old preferences, position, usage and explicit startup choice.
  Legacy dark/light and custom colors remain supported. Fresh installs use Ember.

## Install / upgrade

Download `tallydesklet_0.3.0-1_all.deb` and `SHA256SUMS`, then run in that folder:

```sh
sha256sum -c SHA256SUMS
install -m 644 ./tallydesklet_0.3.0-1_all.deb /tmp/tallydesklet_0.3.0-1_all.deb
tallydesklet --quit
sudo apt install /tmp/tallydesklet_0.3.0-1_all.deb
tallydesklet
```

The readable `/tmp` copy avoids APT's `_apt` notice when your home/download folder
is private. Do not change home-directory permissions or run the app as root.

Open the gear → Display & language to choose Persian. To use the reference's
orange appearance after upgrading, select **Ember / اخگر** in Appearance.
Notifications and login startup remain opt-in. Notifications require the app
running and an available desktop notification service.

## Verification scope

58 logic/data tests and 14 native GTK/notification tests cover migration, all
palettes, contrast, preview/apply/discard, failed saves, week accounting, sustained
alerts, native notification protocol, RTL/LTR, large fonts and 200% scaling.
The Ubuntu 24.04 CI pipeline also exercises Xfwm desktop/CLI integration and
rootless/conventional Debian builds. See `docs/TESTING.md` for the verification
record and remaining real Mint/login/hardware checks. Documentation images are
real GTK captures with fixed synthetic example data, never live user readings.

Original application: MIT, saeedt20. Bundled unmodified Vazirmatn: SIL OFL 1.1.
