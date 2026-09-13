# AGENTS.md

## Tests

This package's comprehensive tests live in
[github.com/org-ai-assisted/dist-ai](https://github.com/org-ai-assisted/dist-ai), not here
(too high-volume to review in this repo; they run in CI).

## Wayland platform env (single source of truth)

- The non-Qubes Wayland session sets `GDK_BACKEND=wayland,x11` (gtk3, comma) and
  `QT_QPA_PLATFORM='wayland;xcb'` (Qt, semicolon, quoted) ONLY in
  `etc/profile.d/15_desktop-config-dist.sh`. The labwc environment file is all commented
  examples -- do NOT set them there.
- Keep the `,x11` / `;xcb` fallback: a Wayland-ONLY value (no X fallback) makes apps needing
  XWayland (GParted, firewall settings, live status checker, tb-updater/msgcollector Qt dialogs)
  abort with no window.
- Fix session-wide platform issues HERE, not with per-app patches.
- Because this sets `QT_QPA_PLATFORM`, msgcollector's `select_qt_platform()` guard is a no-op in
  this session (it only acts when unset); it stays as defense-in-depth for bare/cron launches with
  no desktop-config-dist.
