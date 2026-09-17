---
name: Battery Cat
description: A cream and peach cat-clock companion with calm native desktop controls.
colors:
  cream: "#FFF9EF"
  ink: "#512B1D"
  muted: "#795646"
  line: "#DFC9B7"
  field-border: "#B99A84"
  white: "#FFFFFF"
  button: "#F6E5D6"
  button-hover: "#F5CEB6"
  button-pressed: "#EDB695"
  accent: "#8C4126"
  accent-hover: "#71331D"
  low: "#A8342B"
  good: "#32664A"
typography:
  display:
    fontFamily: Nunito
    fontSize: 37pt
    fontWeight: 700
  title:
    fontFamily: Nunito
    fontSize: 25px
    fontWeight: 700
  body:
    fontFamily: Nunito
    fontSize: 14px
  label:
    fontFamily: Nunito
    fontSize: 14px
    fontWeight: 600
  widget-status:
    fontFamily: Nunito
    fontSize: 9pt
    fontWeight: 600
  widget-detail:
    fontFamily: Nunito
    fontSize: 8pt
rounded:
  field: 6px
  button: 8px
  group: 12px
spacing:
  field-padding: 6px 10px
  button-padding: 8px 16px
  group-padding: 20px 14px 12px
  window-padding: 24px 28px
  settings-gap: 14px
  alarm-gap: 16px
components:
  button:
    backgroundColor: "{colors.button}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.button}"
    padding: "{spacing.button-padding}"
  button-hover:
    backgroundColor: "{colors.button-hover}"
  button-pressed:
    backgroundColor: "{colors.button-pressed}"
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.button}"
    padding: "{spacing.button-padding}"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  field:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "{spacing.field-padding}"
  group:
    rounded: "{rounded.group}"
    padding: "{spacing.group-padding}"
---

# Design System: Battery Cat

## Overview

**Creative North Star: "A little companion on your desk."**

The approved `assets/cat-clock.png` is the visual authority: a soft cream cat alarm clock, peach rim, dark brown features, and a clear circular face for live battery information. Preserve the raster artwork and its alpha silhouette. Surrounding controls share its warm palette and rounded character while retaining familiar Qt interaction.

The voice is gentle, direct Indonesian. Keep the companion calm at rest and make reminders actionable. Windows installer delivery is primary; portable Qt source does not establish verified macOS or Linux presentation.

Key characteristics:

- Recognizable cat-clock silhouette with real text drawn in the face.
- Bundled rounded Nunito typography and warm brown contrast.
- Native controls, explicit feedback, and brief interruptible reminders.

## Colors

The palette echoes the cream and peach artwork without flattening its shaded raster colors into invented solid tokens.

- **Primary:** Warm brown `accent` marks save and acknowledge actions, slider handles, and focus. `accent-hover` deepens primary hover.
- **Neutral:** `cream` fills dialogs and the settings body; `ink` carries main text; `muted` carries supporting text. `line` separates groups and widget details; `field-border` defines white fields.
- **Control surfaces:** `button`, `button-hover`, and `button-pressed` provide the peach-tinted secondary button progression.
- **Semantic:** `low` marks low unplugged readings and errors; `good` marks connected power and successful saves. Connected power is not a claim of active charging.

**The Text Alongside Color Rule.** Every status remains understandable through wording or numerical value. Color supports the message.

## Typography

Nunito is loaded from `assets/Nunito.ttf`; it is the actual application font, not Segoe UI. Rounded letterforms connect native controls to the cat artwork.

Frontmatter records Qt stylesheet pixels for dialog typography and QFont points for painted widget text. The widget uses a logical square canvas (320 × 320) and scales artwork and text together. Display is the battery percentage; widget status is semibold, runtime is regular detail, and threshold detail uses the small size with semibold weight. Do not reinterpret point values as pixels. No custom line height, letter spacing, or tabular-number feature is configured.

## Layout

Settings use a single column inside a resizable scroll area. The window opens at 500 px wide, has a 480 px minimum width, and starts at the smaller of 820 px or available screen height minus 80 px. Content uses the window padding and settings gap tokens; threshold form rows have a 10 px vertical gap. Titles and descriptions wrap. The final action row aligns Save to the right.

Widget choices are 240, 320, and 400 px square. Its face stacks percentage, current state, runtime, divider, and thresholds. The widget is clamped to an available display after dragging or reconfiguration. The separate alarm window is 400 px wide with a centered 100 px cat image, title, explanation, and stacked acknowledge/snooze actions.

## Elevation & Depth

The raster cat supplies illustrated shading. Controls use flat fills and warm borders; no custom drop shadows or elevation tokens are installed. Native window chrome frames settings and alarms. The desktop cat is frameless. There is no decorative animation timer; battery polling runs every 15 seconds and refreshes the painted state.

## Shapes

The alpha mask defines the cat's visible and interactive silhouette, allowing input outside it to pass through. Fields, buttons, and groups use the radius tokens. Group and ordinary button borders are 1 px. Editable fields use the stronger field border. Preserve the artwork's proportions rather than approximating it with a rectangular card.

## Components

- **Buttons:** Warm secondary controls and dark primary actions. Minimum content height is 20 px plus padding and border. Hover/press changes are immediate. Focus uses a 2 px accent border; primary hover remains dark.
- **Fields:** Native spin boxes and combo boxes with white fills and 24 px minimum content height plus padding and border. Focus uses a 2 px accent border. Numeric limits and suffixes remain visible.
- **Groups:** Outlined containers with semibold titles sitting in the top border. A 14 px top margin reserves title space.
- **Checkboxes and slider:** Native checkboxes have 18 px indicators and 30 px minimum height. Volume slider has a 5 px groove and 17 px handle, with a live numeric volume label.
- **Widget:** Drag to move, double-click for settings, right-click for the menu. Always-on-top is optional. Missing battery data uses an em dash and explanatory text.
- **Alarm:** Separate always-on-top dialog with stop and snooze. Sound is finite; closing acknowledges it. Text distinguishes a configured target from full charge.
- **Feedback:** Successful saves use `good`; validation and persistence failures use `low`. Each save attempt resets error color before validating. Messages remain inline beneath settings.
- **Tray and tooltip:** Native actions expose show/hide, settings, pause/resume, acknowledge, and exit. Tooltips share the cream, ink, and line palette.

## Do's and Don'ts

- **Do** preserve the approved raster cat, palette, bundled font, and Indonesian voice.
- **Do** keep settings scrollable and alarms dismissible, with native keyboard-operable controls.
- **Do** state power-source, paused, snoozed, unavailable, and error conditions in text.
- **Don't** add a rectangular frame behind the cat or replace its silhouette with generic geometry.
- **Don't** claim connected power means active charging or imply automatic charging control.
- **Don't** add continuous animation or describe unverified platforms as tested releases.
