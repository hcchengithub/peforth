---
name: windows-screen-capture
description: Capture the Windows desktop at its real pixel resolution and deliver screenshots as image content. Use when inspecting a Windows UI, terminal pane, cursor, selection, or highlight.
---

# Windows screen capture

Use this workflow when a user asks you to inspect what is visibly shown on a Windows desktop. A text-only terminal read cannot reveal the visual location of a cursor or highlight.

## Capture the desktop

Run PowerShell in the same interactive Windows user session as the desktop. In this peforth runtime, use the local PowerShell route exposed by the live dictionary, such as run_pwsh.

Enable DPI awareness before loading Windows Forms or asking Windows for screen bounds. Without it, a 3840x2160 desktop was reported as 1920x1080 and the capture contained only part of the desktop.

```powershell
$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public static class PeForthCaptureDpi {
    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();
}
'@
[void][PeForthCaptureDpi]::SetProcessDPIAware()

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# VirtualScreen covers the full virtual desktop, including multiple monitors.
# Use Screen.PrimaryScreen.Bounds instead when only the primary monitor is wanted.
$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bitmap = [System.Drawing.Bitmap]::new($bounds.Width, $bounds.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $source = [System.Drawing.Point]::new($bounds.Left, $bounds.Top)
    $graphics.CopyFromScreen($source, [System.Drawing.Point]::Empty, $bounds.Size)
    $path = Join-Path $env:TEMP 'desktop-capture.png'
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    Get-Item $path | Select-Object FullName, Length
} finally {
    $graphics.Dispose()
    $bitmap.Dispose()
}
```

Check the reported width, height, and saved file size. Keep the full-resolution capture as the source. For a wide desktop, first make a scaled overview, then crop the relevant screen area from the original image for details such as a small terminal highlight. A corner-only crop can miss a UI located elsewhere.

## Show the screenshot as an image

Pass the screenshot through `ai-image-file`, which reads the captured file locally, encodes it into an `input_image` Data URI in memory, and submits it directly to the model:

```forth
s" Inspect the screenshot for the visual location of the cursor or highlight." s" C:\path\to\desktop-capture.png" false ai-image-file
```

Do not paste Base64 into terminal stdout or treat image bytes as ordinary text. Using `ai-image-file` avoids relying on external image viewers (which may fail if no GUI execution environment is attached). Furthermore, `ai-image-file` runs with session isolation protection, so it can be called safely within an active AI agent turn without causing session turn conflicts (HTTP 409).

## Respect output limits

In this peforth runtime, `run_pwsh` stdout and stderr are each capped at 65,536 bytes. This is a local process-output limit, not an Agents API image-size limit and not a token-window limit.

Because `ai-image-file` transfers image data directly into the API request payload in memory, **it completely bypasses the 65,536-byte stdout bottleneck**. You do not need to downscale, compress, or slice Base64 strings across terminal turns. The full-resolution capture or cropped region can be fed straight into `ai-image-file`.

## What the experiment established

On a 3840x2160 Windows desktop, querying screen bounds before setting DPI awareness yielded 1920x1080. Calling SetProcessDPIAware first exposed the full 3840x2160 dimensions. A full screenshot and a focused crop then made Midnight Commander's left-panel highlight visible. The exact local capture method worked; earlier `view_image` failures and stdout buffer limitations were completely resolved by adopting `ai-image-file` for image delivery.
