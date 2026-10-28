# Testing TallyDesklet

## 0.3.2 reliability fixes — 28 October 2026

- 64 logic/package tests passed. Default discovery reports one additional skipped
  GUI module; the 16 native GTK/notification tests passed separately on the private display.
- Baseline, composited and 200% display-scale GUI runs passed, including CLI
  forwarding, geometry, settings, window hints, drag/lock/reset, Show Desktop,
  workspaces and usage/position persistence across process restart.
- New regressions cover backward dates within/outside the seven-day retention
  window, saved-history restart, per-metric warning cooldowns/sustained windows,
  overflowing preference recovery, literal paths and desktop controls during previews.
- Verification host: Linux Mint 22.3, distribution Python 3.12.3, GTK 3.24.41,
  PyGObject 3.48.2, Cairo 1.18.0 and psutil 5.9.8. Xvfb 21.1.12 and xdotool
  3.20160805.1 were extracted under /tmp, with no system-package installation.
  Every GUI run used scripts/gui-check.sh with private D-Bus, X display and XDG directories.
- The SVG loader is now an explicit runtime dependency. The public-document
  allowlist includes USAGE.md and RELEASE_NOTES.md and still excludes private captures.
- Rootless package build, checksum and file-hash validation, dependency metadata
  and desktop-entry validation passed. The extracted .deb passed the same baseline
  CLI/window smoke checks through proot, including saved usage and position across
  restart, without installing it or changing the real desktop.
- Actual installation/upgrade/removal, login startup, physical hotplug,
  suspend/resume and sustained resource behavior were not tested. Conventional
  debhelper packaging and lintian were not run because those tools are absent.
  These results describe local verification. Hosted CI and release workflow
  outcomes are recorded separately in the repository's Actions history.

## 0.3.1 header update — 12 October 2026

- All 72 existing checks passed in an isolated private D-Bus/virtual X11/Xfwm4 session: 58 logic/package checks and 14 native GTK/notification checks.
- The 14 native checks also passed at 200% display scale. Regenerated and visually reviewed English, Persian and compact widget captures show the literal TallyDesklet heading, no chip logo/live indicator, and the existing gear at the opposite edge. All six theme previews use the shared renderer and fixed synthetic values.
- Rootless Debian packaging passed with matching application/changelog versions and checksums. Source and installed metrics/configuration code otherwise retain their previous behavior.
- Native Mint installation, real login/startup, suspend/resume and physical monitor hotplug were not repeated for this header-only update. Hosted CI retains its normal/composited/HiDPI GUI smoke and conventional Debian checks.

## Publication checks — version 0.2.1

All 44 deterministic unit tests passed during publication preparation. The
source launcher reports 0.2.1. Unit tests use injected counters and temporary
directories; they do not depend on a particular network adapter or write real
user preferences.

The local environment and historical performance reports are intentionally
kept private. No hardware model, host OS inventory, or live readings are
published here. This record makes no claim about a fresh target-system install.

```sh
PYTHONPATH=src /usr/bin/python3 -m unittest discover -s tests -v
./scripts/dev-run.sh --version
./scripts/build-deb.sh
(cd dist && sha256sum -c SHA256SUMS)
```

Coverage includes memory/bar agreement, disk reserved space, units, network
rates, route selection, warm-up, counter resets, interface switching, resume
gaps, bounded histories, atomic settings, monitor clamping, opt-in autostart,
combined usage totals, midnight/Sunday rollovers, bounded storage, restart,
corrupt-history recovery, and persistence failures.

Rename tests also cover importing legacy preferences and usage, preserving
original files, preferring new state, private file permissions, corrupt data,
failed imports, explicit paths, and preserving opt-in login startup choices.

The packaging regression test adds private files and live captures to a fixture
source tree and asserts that only allowlisted public documents enter the package.
The rootless build, checksum check, and desktop-entry validation also passed.

## Isolated GUI checks

```sh
sudo apt install xvfb xauth xfwm4 xdotool wmctrl x11-utils
./scripts/gui-check.sh
./scripts/gui-check.sh --composited
./scripts/gui-check.sh --hidpi
```

These commands start Xfwm on an isolated Xvfb display with a private D-Bus
session and temporary XDG config/state directories. Never run GUI automation
against a real user desktop session. Captures go into ignored `dist/`
directories because real readings can expose personal machine information.

Publication checks reran baseline, composited, and HiDPI isolated GUI checks,
including
dark/light themes, widget scales 1×/2×, positioning, saved usage, and CLI controls.
Source files, the staged Git index, and the extracted package passed redacted
Gitleaks scans. A separate review checked tracked filenames, public identity,
and the absence of host identifiers, personal paths, and private artifacts.

Historical virtual-display checks exercised geometry, dark/light themes,
scaling, focus, window hints, drag/lock/reset, single-instance forwarding,
Show Desktop, workspaces, settings, and saved usage after restart. Historical
results do not substitute for a fresh hosted CI run or physical-session testing.

## Physical-session acceptance checklist

- [ ] Fresh installation, upgrade, and removal with dependency resolution.
- [ ] Launcher and icon from the application menu.
- [ ] Real desktop clicks, Show Desktop, and workspace changes.
- [ ] Wi-Fi/Ethernet reconnect and VPN selection on hardware.
- [ ] Monitor hotplug and resolution changes.
- [ ] Actual suspend/resume.
- [ ] Opt-in startup on the next login and disabling it.
- [ ] Sustained runtime and resource use on representative hardware.

Virtual displays and deterministic fixtures do not prove hardware hotplug,
login startup, or suspend integration. No public performance guarantee is made.

## Continuous integration

GitHub Actions uses an Ubuntu 24.04 hosted runner to run unit tests, build a
rootless package, exercise isolated GUI checks, validate the desktop entry,
check package contents with lintian, and run the conventional debhelper build.
Consult the repository's Actions tab for actual run results.


## 0.3.0 redesign verification

Local environment: Ubuntu 24.04, distribution Python 3.12.3, GTK 3.24.41,
PyGObject 3.48.2, Cairo/Pango and psutil 5.9.8. Distribution libraries were
extracted into a private runtime; Xvfb/Xfwm, D-Bus and XDG paths were isolated.
No real user desktop preferences, usage or notifications were used in tests.
The actual application also passed UI-driven Xfwm top/below, lock/drag/save,
Show Desktop, workspace and graceful-shutdown checks on the private display.

- 58 deterministic logic/data tests: legacy migration, accounting, SI/IEC,
  palette contrast, configuration bounds, RTL/numerals, alternate week starts,
  sustained threshold/reset/rearm/cooldown, package privacy and persistence.
- 14 native GUI/protocol tests: all palette previews without saving; discard and
  timer cleanup; actual Apply; Persian RTL/English LTR navigation and text; large
  font/window bounds at 100%/200%; section minimum; failure-preserved draft;
  native Notify payload/identity, async opt-out, service failure and shutdown.
- Actual synthetic-data GTK screenshots reviewed for both languages, all themes
  and settings pages. These are generated without starting the collector.
- Rootless Debian staging/build and architecture/dependency/font/license checks.
- Short actual-application idle observation: 35.03 seconds at one-second sampling,
  0.631% of one CPU core; RSS 69.54–69.60 MiB. This is a virtual short observation,
  not a hardware/endurance guarantee; settings/active workloads may use more.

The local managed test bus uses TCP and cannot transport the Unix file descriptors
used by GApplication's remote command-line forwarding. Hosted CI uses a normal
private Unix D-Bus session and exercises repeat launch, --settings/--quit/reset,
Xfwm hints, keyboard controls, drag/lock/restart, Show Desktop and workspaces.
The existing CI also runs normal, composited and HiDPI checks, lintian and both
rootless/conventional Debian builds. The publication report identifies their
actual outcome; this description does not turn an unrun check into a pass.

Still requiring a real Linux Mint 22.3 Xfce machine: actual upgrade/install/remove,
next-login startup, hardware monitor hotplug, suspend/resume, actual notification
presentation and sustained resource behavior. Wayland positioning is not claimed.
