# TallyDesklet user guide

See the [README](../README.md) for the current download and installation steps.

## Everyday use

Drag the unlocked header to move the card. The gear opens Settings. Right-click the card for Settings, Lock position,
Always on top, Reset position, and Quit. A repeat launch
opens Settings in the existing instance. Escape closes Settings.

| Command | Action |
| --- | --- |
| `tallydesklet` | Start the card; a repeat invocation opens Settings |
| `tallydesklet --settings` | Open Settings |
| `tallydesklet --reset-position` | Restore the upper-right position in the monitor's work area |
| `tallydesklet --version` | Print the version without opening a display |
| `tallydesklet --quit` | Close the running application |

Enable or disable **Start at login** in Settings. The option requires the stable
installed launcher at `/usr/bin/tallydesklet`; it is unavailable in a source-only
checkout. Autostart state comes from your user-scoped XDG desktop entry.

## New settings in 0.3

- **Appearance:** six theme tiles, opacity/scale sliders, Compact, reduced motion,
  optional custom accent and Restore theme colors.
- **Display & language:** English/Persian, Auto/Latin/Persian digits, SI/IEC units,
  and section visibility. Charts retain chronological left-to-right order.
- **Monitoring:** sample interval, literal interface ID, filesystem path chooser,
  and Saturday/Sunday/Monday week start. Changing week start recalculates retained
  daily buckets without changing their values.
- **Desktop & startup:** lock, top/below, all workspaces, explicit login startup,
  and immediate position reset. Narrow screens use named icon navigation.
- **Alerts:** optional memory/disk notifications, off by default. A reading must
  remain above its threshold for 60 seconds, with five-point rearm hysteresis and
  at most one attempt per metric per ten minutes. Missing data/resume gaps reset
  the sustained window. The program must be running and a session notification
  service must be available; desktop notification policy controls presentation.
- **About:** version, GitHub, issue reporting and MIT/OFL attribution.

Appearance and display preview without saving. Sampling, week definition,
notifications and login startup change only after **Apply**. Close or Escape asks
before discarding unsaved changes. Existing preferences, usage and startup choice
survive upgrade; legacy dark/light themes and chosen accent colors are preserved.
Fresh installs default to Ember. Font registration is process-private.

## Upgrade from Mint Meter

Quit the old app with `mint-meter --quit` before installing the new package.
APT replaces `mint-meter` with `tallydesklet`; the old command remains available
as a compatibility launcher.

On first launch, legacy `mint-meter/config.json` and `mint-meter/usage.json` are
copied from their XDG directories only when the corresponding TallyDesklet file
is absent. Original files remain intact, and newer TallyDesklet files take
priority. Existing opt-in login entries keep working; changing **Start at login**
replaces or removes the old entry only after your explicit choice.

## What the numbers mean

| Reading | Definition |
| --- | --- |
| CPU | Aggregate utilization across all cores; the initial sample is warm-up |
| RAM | Used memory is **total − available**; the bar uses the same ratio |
| System disk | Occupied / total capacity of the filesystem containing the selected path, `/` by default; refreshed every 10 seconds |
| Download / upload | Byte-counter differences divided by monotonic elapsed time, on one selected interface |
| Daily usage | Combined received + sent bytes observed while the app runs; resets at local midnight |
| Weekly usage | Combined usage for the calendar week; **Saturday, Sunday or Monday**, selected in Settings; Sunday preserved on upgrade |

Decimal units use powers of 1000 (`GB`, `MB/s`); binary units use 1024
(`GiB`, `MiB/s`). Disk capacity is storage occupancy, not disk I/O or a sum of
physical drives. Its tooltip separately reports space available to the user,
which may differ because of reserved filesystem blocks.

Usage totals survive normal restarts and remain available while offline. They
exclude traffic while the app is closed and ambiguous counter resets, reconnects,
or sampling gaps over 15 seconds. Initial periods may be partial. These totals
represent observed traffic, not an ISP bill or complete historical accounting.

<details>
<summary>Network selection, VPNs, unavailable readings, and persistence details</summary>

Automatic selection uses kernel route lookups without sending packets: IPv4 to
`1.1.1.1` first, IPv6 to `2606:4700:4700::1111` second. Kernel routing policy and
metrics choose the device; the lookup refreshes every 5 seconds. Loopback is
excluded. VPN logical routes, including split-default routes, are followed when
selected by the kernel. Select a physical interface manually to measure its
encapsulated traffic. Interfaces are never summed; destination-specific split
tunnels may use a different interface than these representative lookups.

An existing route does not prove internet connectivity. **Offline** means no
eligible active route/device; **Unavailable** means the device or its data could
not be read. A valid idle sample is `0 B/s`. Interface changes, resets, and gaps
over 15 seconds establish new baselines. Histories use Linux's suspend-aware
monotonic BOOTTIME clock.

A valid usage delta spanning midnight belongs to the later day. Switching
interfaces preserves accumulated totals and starts the new interface with a
fresh baseline. Only seven daily aggregates are retained. Usage is checkpointed
at most once per minute and flushed on normal exit; a forced kill or power loss
can lose up to the last minute. Corrupt history is preserved as
`usage.broken-<timestamp>.json` before tracking restarts. Read failures show
unavailable totals; save failures retain live totals and display a notice.

</details>

## Preferences and removal

| Data | Default location |
| --- | --- |
| Preferences | `~/.config/tallydesklet/config.json` |
| Bounded usage history | `~/.local/state/tallydesklet/usage.json` |
| Opt-in login entry | `~/.config/autostart/tallydesklet.desktop` |

`XDG_CONFIG_HOME` and `XDG_STATE_HOME` override these base directories. Saves are
atomic. Invalid preferences are preserved as `config.broken-<timestamp>.json`
before defaults load. Individual samples and graph histories are not stored.

Disable **Start at login** in Settings, then quit and remove the package:

```bash
tallydesklet --quit
sudo apt remove tallydesklet
```

Personal settings and usage history are preserved. If the app is already
uninstalled, remove only `tallydesklet.desktop` and, if upgrading,
`mint-meter.desktop` from `${XDG_CONFIG_HOME:-$HOME/.config}/autostart/`.

To erase saved data, optionally remove the `tallydesklet` directories under
`${XDG_CONFIG_HOME:-$HOME/.config}/` and `${XDG_STATE_HOME:-$HOME/.local/state}/`
after quitting. Legacy `mint-meter` directories are preserved backups; delete
them only if you no longer need them.

## Troubleshooting and compatibility

| Symptom | What to check |
| --- | --- |
| `No module named gi` or `cairo` | Install system dependencies and use `/usr/bin/python3` |
| Widget seems missing | Run `tallydesklet --reset-position`, then `tallydesklet --settings` |
| Disk is Unavailable | Select an existing, accessible path in Settings |
| Network is Offline or Unavailable | Check routing and select the intended interface |
| Background is opaque | Check desktop compositing; the opaque fallback is supported |
| Startup option is disabled in a checkout | Install the `.deb` to provide the stable launcher |

**X11 is the release target.** Wayland may display the card but ignore positioning,
stacking, dragging, or workspace hints; full Wayland widget integration is not
claimed. Window-manager hints are requests, not guarantees.

## Privacy

TallyDesklet reads local counters without an account, telemetry, cloud service,
or background web server. Configuration and bounded usage history stay in your
XDG directories. Review live screenshots before sharing: they can reveal machine
capacity, interface names, paths, and activity. Documentation previews use only
fixed example data.
