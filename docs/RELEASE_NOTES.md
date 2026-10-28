# TallyDesklet 0.3.2 — Reliability fixes

- Preserve usage history across backward date changes and restarts, within the existing seven-day storage bound.
- Keep desktop controls effective during appearance previews.
- Preserve per-metric warning cooldowns and literal filesystem paths.
- Recover overflowing preference files, require the SVG loader, and ship the user guide.
- Remove unused renderer imports and theme constants.

## Install / upgrade

Download [tallydesklet_0.3.2-1_all.deb](https://github.com/saeedt20/TallyDesklet/releases/download/v0.3.2/tallydesklet_0.3.2-1_all.deb) and [SHA256SUMS](https://github.com/saeedt20/TallyDesklet/releases/download/v0.3.2/SHA256SUMS), then run in the download folder:

```sh
sha256sum -c SHA256SUMS
tallydesklet --quit
install -m 644 ./tallydesklet_0.3.2-1_all.deb /tmp/tallydesklet_0.3.2-1_all.deb
sudo apt install /tmp/tallydesklet_0.3.2-1_all.deb
tallydesklet
```

Restart the running process to load the fixes. The readable /tmp copy avoids APT's `_apt` home-folder access notice. Installation does not enable login startup.

## Verification

64 logic/package tests and 16 native GTK/notification tests passed locally, together with baseline, composited and 200% display-scale GUI smoke checks. The extracted package also passed launch, CLI and shutdown checks without system installation. Regression checks cover backward dates/restart, alert cooldowns, preview/desktop interaction, literal paths and preference recovery. Package checks retain the explicit public-document allowlist. See [the validation record](https://github.com/saeedt20/TallyDesklet/blob/v0.3.2/docs/TESTING.md) for the exact environment and results. Virtual X11 checks do not certify installation, hardware hotplug, suspend/resume or real login startup.
