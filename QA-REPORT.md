# Battery Cat 1.1 — verification

Verified on Windows 10 x64, 10 September 2026.

## Passed

- 12 automated tests: low/target alarms, plugged/unplugged transitions, duplicate suppression, hysteresis, acknowledgement, snooze expiry, skipped percentage values, missing/invalid battery values, settings sanitization, unknown estimates, settings Save button through Qt input events, scroll access to footer, validation after saving, generated WAV structure, mocked Windows autostart quoting and removal.
- Separate Qt integration scenario: PNG has actual alpha, settings persist, low alarm opens, snooze closes it, plugging in at target opens target alarm, acknowledgement prevents repeat, missing battery and 240px widget render.
- Seven widget/settings/alarm screenshots inspected. Independent visual review: ship; reported feedback-color issue fixed and reviewer confirmed resolved.
- Standalone packaged executable runs with bundled font and artwork and reads actual laptop battery. Short diagnostic with widget and settings open: 76.6 MB RSS.
- Final NSIS installer compiles without warnings, 27,057,027 bytes. Silent installation into isolated QA folder returns code 0.
- Executable extracted by final installer runs and reads real battery; font and alpha checks pass. RSS in this short test: 76.8 MB.
- Uninstaller launcher returns 0; application executable and entire owned dependency folder removed. Deliberately placed unrelated user file remains.
- 1.1 build reran all 14 automated tests. Packaged 1.1 executable smoke test passed with real battery data, bundled font and alpha artwork; observed short-run RSS was 70.8 MB.
- The 1.1 NSIS installer compiled successfully and is available in `release`. The 1.0 installer had a full isolated install/uninstall test; the 1.1 installer was rebuilt from the same installer script with the 1.1 payload. A fresh 1.1 install test was not repeated because the environment blocked the cleanup command after build.

## Scope limits

- Installer test used /TEST mode: same file installation and removal, without changing real Start menu/Desktop shortcuts or uninstall registry entries. Autostart registry calls were mocked in automated tests.
- Sound generation and Windows playback invocation tested; audibility depends on actual device and mute settings and was not independently assessed by listening.
- No prolonged discharge/charge cycle or sleep/resume hardware test. Real battery reading plus simulated alarm transitions were exercised.
- RAM figure is an observed short-run working set, not a guarantee or idle CPU benchmark.
- No clean-machine VM test, code-signing certificate, macOS build, Linux build, or cross-platform desktop/compositor validation.

## Distribution

Windows 10/11 x64 installer bundles Python and Qt. Source archive includes app code, build/installer scripts, font/asset provenance, notices, design documentation, and tests. All user monitoring data remains local. This app does not control charging hardware.
