---
name: windows-screen-capture
description: Capture the Windows desktop or a specific screen region with DPI awareness and inspect it via AI vision without user approval prompts. Use when inspecting a Windows UI, photo, terminal pane, cursor, selection, or highlight.
---

# Windows screen capture

Use the built-in peforth screen capture and vision words when a user asks you to inspect what is visibly shown on the Windows desktop (such as a photo, GUI window, cursor, or highlight).

All read-only screen capture and image inspection commands listed below are **auto-approved** in `peforth_run_forth` (they execute immediately without pausing for user confirmation).

## 1. One-step live desktop inspection (`ai-screen`)

To capture the full Windows virtual desktop and inspect it with AI vision in a single step:

```forth
s" Describe what is visible on the desktop, especially in the upper-right corner." false ai-screen
```

- Stack effect: `( prompt-string [stream?] -- [response-string] )`
- Passing `false` pushes the vision answer string onto the Forth stack (and prints the capture metadata JSON `{path, width, height, orig_width, orig_height, size, captured_at}` to stdout).

## 2. One-step region / zoomed-in inspection (`ai-screen-region`)

When you need to zoom into a specific corner, window, or UI detail at higher effective resolution, use `ai-screen-region` with either **normalized coordinates (`0.0` to `1.0`)** or **pixel coordinates (`x y width height`)**:

```forth
\ Inspect the upper-right quadrant using normalized coordinates (x=0.5, y=0.0, w=0.5, h=0.5):
s" Describe the photo and details in the upper-right corner." 0.5 0.0 0.5 0.5 false ai-screen-region

\ Or using pixel coordinates (x=1920, y=0, w=1920, h=1080):
s" Read the text in this region." 1920 0 1920 1080 false ai-screen-region
```

- Stack effect: `( prompt-string x y width height [stream?] -- [response-string] )`

## 3. Capture-only words (`desktop-capture` and `desktop-capture-region`)

If you only need to capture a fresh screenshot file (or inspect an existing local image file with `ai-image-file`):

```forth
\ Capture full desktop (prints metadata JSON and pushes the unique JPEG path):
desktop-capture

\ Capture a specific region:
0.5 0.0 0.5 0.5 desktop-capture-region

\ Inspect any local image file (auto-approved in peforth_run_forth):
s" Inspect the screenshot." s" C:\path\to\image.png" false ai-image-file
```

## Why you should use these built-in words instead of raw `run_pwsh`

1. **Zero approval friction**: `ai-screen`, `ai-screen-region`, `desktop-capture`, `desktop-capture-region`, and `ai-image-file` are recognized as read-only inspection commands and run without prompting the user for approval.
2. **Automatic DPI awareness**: Calls `SetProcessDPIAware()` before reading `SystemInformation.VirtualScreen`, ensuring 4K / high-DPI desktops (`3840x2160`) are captured in full rather than clipped at `1920x1080`.
3. **Unique timestamped filenames**: Saves each capture as `$env:TEMP\desktop-live-YYYYMMDD-HHMMSS-<id>.jpg` and verifies the file on disk, eliminating stale-screenshot bugs caused by reusing a fixed `desktop-capture.png` filename.
4. **Automatic 1 MiB Data URI compliance**: The OpenAI Agents API enforces a strict `1,048,576`-character limit on `input_image.image_url` (`string_above_max_length`). Both `desktop-capture` and `ai-image-file` automatically downscale and JPEG-compress large images (`<= 750 KB`) so they never fail with HTTP 400.
5. **Isolated vision turn**: `ai-image-file`, `ai-screen`, and `ai-screen-region` run in an isolated one-shot session so they can be called safely inside an active AI turn without HTTP 409 session conflicts.
