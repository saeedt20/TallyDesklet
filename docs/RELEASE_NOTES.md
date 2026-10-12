# TallyDesklet 0.3.1 — A simpler widget header

- Replace the CPU logo, System heading and Live dot/text with the widget name: **TallyDesklet**.
- Keep the settings gear at the opposite edge, with English left-aligned and Persian right-aligned branding. The name keeps its Latin spelling in both languages.
- Existing metrics, graphs, themes, compact mode, settings, usage history and opt-in startup are preserved.

## Install / upgrade

Download `tallydesklet_0.3.1-1_all.deb` and `SHA256SUMS`, then run in that folder:

```sh
sha256sum -c SHA256SUMS
tallydesklet --quit
install -m 644 ./tallydesklet_0.3.1-1_all.deb /tmp/tallydesklet_0.3.1-1_all.deb
sudo apt install /tmp/tallydesklet_0.3.1-1_all.deb
tallydesklet
```

Restart the old running process to load the updated header. The readable /tmp copy avoids APT's `_apt` home-folder access notice.

## Verification

All 72 existing logic/package and native GTK checks passed. The 14 native checks also passed at 200% display scale. The documentation previews use fixed synthetic values. Virtual X11 checks do not certify Mint installation, hardware hotplug or real login startup; see docs/TESTING.md.
