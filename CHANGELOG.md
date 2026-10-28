# Changelog

## 0.3.2 — 28 October 2026

- Preserve recorded usage when the local date moves backward, including across restart.
- Keep Reset position, position locking and Always on top effective during appearance previews.
- Preserve warning cooldowns when alert settings change; reset only affected sustained readings.
- Keep filesystem paths literal, including trailing spaces.
- Preserve and recover preference files containing overflowing numeric values.
- Require the SVG loader and include the user guide and release notes in Debian packages.
- Remove unused renderer imports and theme constants.

## 0.3.1 — 12 October 2026

- Simplify the widget header to TallyDesklet and the settings gear.
- Remove the CPU logo, System title and Live dot/text from both languages.
- Keep the Latin brand left-aligned in English and right-aligned in Persian.


## 0.3.0 — 2026-10-12

- Redesign the widget and native settings with six coordinated themes.
- Add Persian RTL, English LTR, bundled Vazirmatn and independent numeral choice.
- Add reversible appearance previews, custom accent reset and reduced motion.
- Add compact layout, per-section visibility and responsive settings navigation.
- Add Saturday/Sunday/Monday week starts without changing stored daily totals.
- Add optional sustained RAM/disk notifications, default off.
- Preserve existing preferences, startup choice, usage and legacy palettes.
- Expand deterministic logic tests, real notification protocol and native UI checks.


## 0.2.1 — TallyDesklet

- Rename the app, repository, package, and command to TallyDesklet.
- Import legacy preferences and usage while preserving originals and newer state.
- Keep the old command and existing opt-in login entries working.
- Update documentation and privacy-safe native GTK previews.

## 0.2.0 — 2026-10-08

- Add weekly usage on the left and daily usage on the right, immediately above Network.
- Combine download and upload totals on the selected interface while Mint Meter runs.
- Reset daily at local midnight and weekly on Sunday; preserve totals across restarts.
- Store at most seven daily buckets, checkpoint once per minute, and flush on normal quit.
- Exclude ambiguous reconnect, counter-reset, and resume-gap traffic; explain partial tracking in the tooltip.
- Extend the compact card to 320 × 330 logical pixels.
- Correct network-rate timing when route inspection is slow.

## 0.1.0 — 2026-09-28

- Initial compact GTK desktop card with live CPU, RAM, filesystem and network metrics.
- Bounded histories, capacity bars, dark/light themes, scaling and unit preferences.
- Position persistence, lock, reset, desktop/top stacking and workspace controls.
- Single-instance CLI, native settings and opt-in login startup.
- Core tests, virtual-display GUI checks, rootless Debian packaging and CI workflows.
- Original local evaluation build; now published under the MIT license.
