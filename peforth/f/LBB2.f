code lcd-backlight
    import json
    level = vm.pop()
    if isinstance(level, bool) or not isinstance(level, (int, float)) or int(level) != level:
        raise ValueError("lcd-backlight expects an integer brightness from 0 to 100.")
    level = int(level)
    if not 0 <= level <= 100:
        raise ValueError("lcd-backlight brightness must be from 0 to 100.")
    script = (
        "$method = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods; "
        f"$result = Invoke-CimMethod -InputObject $method -MethodName WmiSetBrightness -Arguments @{{Timeout=1; Brightness={level}}}; "
        "$current = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness | Select-Object -ExpandProperty CurrentBrightness; "
        "[pscustomobject]@{CurrentBrightness=$current} | ConvertTo-Json -Compress"
    )
    vm.push(script)
    yield from vm.call(vm.tick("run_pwsh"))
    result = vm.pop()
    if not isinstance(result, dict) or result.get("exit_code") != 0:
        detail = result.get("stderr", repr(result)) if isinstance(result, dict) else repr(result)
        raise RuntimeError("lcd-backlight failed: " + detail)
    try:
        confirmed = json.loads(result.get("stdout", "").strip()).get("CurrentBrightness")
    except Exception as exc:
        raise RuntimeError("Could not verify lcd-backlight result: " + str(exc))
    if confirmed != level:
        raise RuntimeError(f"Requested {level}%, but Windows reports {confirmed}%.")
    print(f"LCD backlight set to {confirmed}%.")
    end-code
    // ( n -- ) Set the laptop LCD backlight to an integer percentage from 0 to 100.
    /// Uses Windows WMI and verifies the reported brightness; reports an error if the setting fails.

code audio-status(LBB2)
    import json

    script = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$src = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

[ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
    [PreserveSig] int EnumAudioEndpoints(int flow, int stateMask, out IntPtr devices);
    [PreserveSig] int GetDefaultAudioEndpoint(int flow, int role, out IMMDevice device);
    [PreserveSig] int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string id, out IMMDevice device);
}
[ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
    [PreserveSig] int Activate(ref Guid iid, int cls, IntPtr parameters, out IntPtr ppv);
    [PreserveSig] int OpenPropertyStore(int access, out IntPtr props);
    [PreserveSig] int GetId(out IntPtr id);
    [PreserveSig] int GetState(out int state);
}
[ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioEndpointVolume {
    [PreserveSig] int RegisterControlChangeNotify(IntPtr notify);
    [PreserveSig] int UnregisterControlChangeNotify(IntPtr notify);
    [PreserveSig] int GetChannelCount(out uint count);
    [PreserveSig] int SetMasterVolumeLevel(float level, ref Guid context);
    [PreserveSig] int SetMasterVolumeLevelScalar(float level, ref Guid context);
    [PreserveSig] int GetMasterVolumeLevel(out float level);
    [PreserveSig] int GetMasterVolumeLevelScalar(out float level);
    [PreserveSig] int SetChannelVolumeLevel(uint channel, float level, ref Guid context);
    [PreserveSig] int SetChannelVolumeLevelScalar(uint channel, float level, ref Guid context);
    [PreserveSig] int GetChannelVolumeLevel(uint channel, out float level);
    [PreserveSig] int GetChannelVolumeLevelScalar(uint channel, out float level);
    [PreserveSig] int SetMute([MarshalAs(UnmanagedType.Bool)] bool mute, ref Guid context);
    [PreserveSig] int GetMute([MarshalAs(UnmanagedType.Bool)] out bool mute);
}
[ComImport, Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionManager2 {
    [PreserveSig] int GetAudioSessionControl(ref Guid guid, int flags, out IntPtr control);
    [PreserveSig] int GetSimpleAudioVolume(ref Guid guid, int flags, out IntPtr volume);
    [PreserveSig] int GetSessionEnumerator(out IAudioSessionEnumerator sessions);
    [PreserveSig] int RegisterSessionNotification(IntPtr notification);
    [PreserveSig] int UnregisterSessionNotification(IntPtr notification);
    [PreserveSig] int RegisterDuckNotification([MarshalAs(UnmanagedType.LPWStr)] string id, IntPtr notification);
    [PreserveSig] int UnregisterDuckNotification(IntPtr notification);
}
[ComImport, Guid("E2F5BB11-0570-40CA-ACDD-3AA01277DEE8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionEnumerator {
    [PreserveSig] int GetCount(out int count);
    [PreserveSig] int GetSession(int index, out IntPtr control);
}
[ComImport, Guid("BFB7FF88-7239-4FC9-8FA2-07C950BE9C6D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionControl2 {
    [PreserveSig] int GetState(out int state);
    [PreserveSig] int GetDisplayName(out IntPtr name);
    [PreserveSig] int SetDisplayName([MarshalAs(UnmanagedType.LPWStr)] string name, ref Guid context);
    [PreserveSig] int GetIconPath(out IntPtr path);
    [PreserveSig] int SetIconPath([MarshalAs(UnmanagedType.LPWStr)] string path, ref Guid context);
    [PreserveSig] int GetGroupingParam(out Guid grouping);
    [PreserveSig] int SetGroupingParam(ref Guid grouping, ref Guid context);
    [PreserveSig] int RegisterAudioSessionNotification(IntPtr notification);
    [PreserveSig] int UnregisterAudioSessionNotification(IntPtr notification);
    [PreserveSig] int GetSessionIdentifier(out IntPtr id);
    [PreserveSig] int GetSessionInstanceIdentifier(out IntPtr id);
    [PreserveSig] int GetProcessId(out uint pid);
    [PreserveSig] int IsSystemSoundsSession();
}
[ComImport, Guid("87CE5498-68D6-44E5-9215-6DA47EF883D8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface ISimpleAudioVolume {
    [PreserveSig] int SetMasterVolume(float volume, ref Guid context);
    [PreserveSig] int GetMasterVolume(out float volume);
    [PreserveSig] int SetMute([MarshalAs(UnmanagedType.Bool)] bool mute, ref Guid context);
    [PreserveSig] int GetMute([MarshalAs(UnmanagedType.Bool)] out bool mute);
}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumerator {}

public class AudioSessionInfo {
    public uint ProcessId { get; set; }
    public int State { get; set; }
    public float Volume { get; set; }
    public bool Muted { get; set; }
    public string DisplayName { get; set; }
}
public class AudioEndpointInfo {
    public float Volume { get; set; }
    public bool Muted { get; set; }
}
public static class AudioStatusReader {
    public static string DefaultId(int role) {
        var enumerator = (IMMDeviceEnumerator)new MMDeviceEnumerator();
        IMMDevice device;
        if (enumerator.GetDefaultAudioEndpoint(0, role, out device) < 0) return "";
        IntPtr pointer;
        if (device.GetId(out pointer) < 0) return "";
        string id = Marshal.PtrToStringUni(pointer);
        Marshal.FreeCoTaskMem(pointer);
        return id;
    }
    public static AudioEndpointInfo ReadEndpoint(string id) {
        var enumerator = (IMMDeviceEnumerator)new MMDeviceEnumerator();
        IMMDevice device;
        if (enumerator.GetDevice(id, out device) < 0) return null;
        Guid iid = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A");
        IntPtr pointer;
        if (device.Activate(ref iid, 23, IntPtr.Zero, out pointer) < 0) return null;
        var volume = (IAudioEndpointVolume)Marshal.GetObjectForIUnknown(pointer);
        Marshal.Release(pointer);
        float level;
        bool muted;
        if (volume.GetMasterVolumeLevelScalar(out level) < 0 || volume.GetMute(out muted) < 0) return null;
        return new AudioEndpointInfo { Volume = level, Muted = muted };
    }
    public static List<AudioSessionInfo> ReadSessions(string id) {
        var rows = new List<AudioSessionInfo>();
        var enumerator = (IMMDeviceEnumerator)new MMDeviceEnumerator();
        IMMDevice device;
        if (enumerator.GetDevice(id, out device) < 0) return rows;
        Guid iid = new Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F");
        IntPtr pointer;
        if (device.Activate(ref iid, 23, IntPtr.Zero, out pointer) < 0) return rows;
        var manager = (IAudioSessionManager2)Marshal.GetObjectForIUnknown(pointer);
        Marshal.Release(pointer);
        IAudioSessionEnumerator sessions;
        if (manager.GetSessionEnumerator(out sessions) < 0) return rows;
        int count;
        if (sessions.GetCount(out count) < 0) return rows;
        for (int i = 0; i < count; i++) {
            IntPtr controlPointer;
            if (sessions.GetSession(i, out controlPointer) < 0) continue;
            var control = (IAudioSessionControl2)Marshal.GetObjectForIUnknown(controlPointer);
            Marshal.Release(controlPointer);
            int state;
            if (control.GetState(out state) < 0 || state != 1) continue;
            uint pid;
            if (control.GetProcessId(out pid) < 0) continue;
            var simpleVolume = (ISimpleAudioVolume)control;
            float level;
            bool muted;
            if (simpleVolume.GetMasterVolume(out level) < 0 || simpleVolume.GetMute(out muted) < 0) continue;
            IntPtr namePointer = IntPtr.Zero;
            control.GetDisplayName(out namePointer);
            string name = namePointer == IntPtr.Zero ? "" : Marshal.PtrToStringUni(namePointer);
            if (namePointer != IntPtr.Zero) Marshal.FreeCoTaskMem(namePointer);
            rows.Add(new AudioSessionInfo { ProcessId = pid, State = state, Volume = level, Muted = muted, DisplayName = name });
        }
        return rows;
    }
}
'@
Add-Type -TypeDefinition $src
$defaultIds = @{
    Console = [AudioStatusReader]::DefaultId(0)
    Multimedia = [AudioStatusReader]::DefaultId(1)
    Communications = [AudioStatusReader]::DefaultId(2)
}
$playback = @()
$pnps = @(Get-PnpDevice -Class AudioEndpoint -ErrorAction Stop)
foreach ($device in $pnps) {
    if (-not $device.InstanceId.StartsWith('SWD\MMDEVAPI\{0.0.0.00000000}', [StringComparison]::OrdinalIgnoreCase)) { continue }
    $id = $device.InstanceId.Substring(13)
    $roles = @()
    foreach ($role in @('Console', 'Multimedia', 'Communications')) {
        if ($defaultIds[$role] -eq $id) { $roles += $role }
    }
    $endpointVolume = $null
    $endpointMuted = $null
    $apps = @()
    if ($device.Status -eq 'OK') {
        $volume = [AudioStatusReader]::ReadEndpoint($id)
        if ($null -ne $volume) {
            $endpointVolume = [math]::Round($volume.Volume * 100)
            $endpointMuted = $volume.Muted
        }
        foreach ($session in [AudioStatusReader]::ReadSessions($id)) {
            $processName = 'System'
            if ($session.ProcessId -ne 0) {
                try { $processName = (Get-Process -Id ([int]$session.ProcessId) -ErrorAction Stop).ProcessName }
                catch { $processName = "PID $($session.ProcessId)" }
            }
            $apps += [pscustomobject]@{
                name = $processName
                pid = $session.ProcessId
                volumePercent = [math]::Round($session.Volume * 100)
                muted = $session.Muted
                sessionName = $session.DisplayName
            }
        }
    }
    $playback += [pscustomobject]@{
        name = $device.FriendlyName
        status = [string]$device.Status
        defaultRoles = $roles
        volumePercent = $endpointVolume
        muted = $endpointMuted
        activeApps = $apps
    }
}
$json = ConvertTo-Json -InputObject ([pscustomobject]@{ playbackDevices = $playback }) -Depth 8 -Compress
[Console]::Out.WriteLine($json)
[Console]::Out.Flush()
Write-Output 'AUDIO_STATUS_DONE'
"""
    script += chr(10) + "Write-Output 'AUDIO_STATUS_TRAILER'" + chr(10)
    vm.push(script)
    yield from vm.call(vm.tick("run_pwsh"))
    result = vm.pop()
    if not isinstance(result, dict) or result.get("exit_code") != 0:
        detail = result.get("stderr", repr(result)) if isinstance(result, dict) else repr(result)
        raise RuntimeError("audio-status(LBB2) failed: " + detail)
    try:
        output_lines = [line for line in result.get("stdout", "").splitlines() if line.strip()]
        if not output_lines:
            raise ValueError("PowerShell returned no output lines")
        report = json.loads(output_lines[0])
    except (TypeError, ValueError) as exc:
        raise RuntimeError("audio-status(LBB2) returned invalid JSON: " + str(exc) + "; raw PowerShell result: " + repr(result))
    devices = report.get("playbackDevices", [])
    report["defaultOutputByRole"] = {
        role: next(
            (item.get("name") for item in devices if role in item.get("defaultRoles", [])),
            None,
        )
        for role in ("Console", "Multimedia", "Communications")
    }
    vm.push(report)
    end-code
    // ( -- dict ) Show Windows playback defaults, endpoint volume/mute, and active app audio sessions.
    /// Read-only: does not change devices, volume levels, or mute state.
    /// Uses Windows Core Audio through PowerShell; reports Console, Multimedia, and Communications defaults.

code audio-volume!
    import json

    percent = vm.pop()
    if isinstance(percent, bool) or not isinstance(percent, (int, float)) or int(percent) != percent:
        raise ValueError("audio-volume! expects an integer percentage from 0 to 100.")
    percent = int(percent)
    if not 0 <= percent <= 100:
        raise ValueError("audio-volume! percentage must be from 0 to 100.")

    csharp = r"""
using System;
using System.Runtime.InteropServices;
[ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
    [PreserveSig] int EnumAudioEndpoints(int flow, int stateMask, out IntPtr devices);
    [PreserveSig] int GetDefaultAudioEndpoint(int flow, int role, out IMMDevice device);
    [PreserveSig] int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string id, out IMMDevice device);
}
[ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
    [PreserveSig] int Activate(ref Guid iid, int cls, IntPtr parameters, out IntPtr ppv);
    [PreserveSig] int OpenPropertyStore(int access, out IntPtr props);
    [PreserveSig] int GetId(out IntPtr id);
    [PreserveSig] int GetState(out int state);
}
[ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioEndpointVolume {
    [PreserveSig] int RegisterControlChangeNotify(IntPtr notify);
    [PreserveSig] int UnregisterControlChangeNotify(IntPtr notify);
    [PreserveSig] int GetChannelCount(out uint count);
    [PreserveSig] int SetMasterVolumeLevel(float level, ref Guid context);
    [PreserveSig] int SetMasterVolumeLevelScalar(float level, ref Guid context);
    [PreserveSig] int GetMasterVolumeLevel(out float level);
    [PreserveSig] int GetMasterVolumeLevelScalar(out float level);
    [PreserveSig] int SetChannelVolumeLevel(uint channel, float level, ref Guid context);
    [PreserveSig] int SetChannelVolumeLevelScalar(uint channel, float level, ref Guid context);
    [PreserveSig] int GetChannelVolumeLevel(uint channel, out float level);
    [PreserveSig] int GetChannelVolumeLevelScalar(uint channel, out float level);
    [PreserveSig] int SetMute([MarshalAs(UnmanagedType.Bool)] bool mute, ref Guid context);
    [PreserveSig] int GetMute([MarshalAs(UnmanagedType.Bool)] out bool mute);
}
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumerator {}
public static class AudioVolumeSetter {
    public static float SetDefault(float value) {
        var enumerator = (IMMDeviceEnumerator)new MMDeviceEnumerator();
        IMMDevice device;
        Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out device));
        Guid iid = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A");
        IntPtr pointer;
        Marshal.ThrowExceptionForHR(device.Activate(ref iid, 23, IntPtr.Zero, out pointer));
        var volume = (IAudioEndpointVolume)Marshal.GetObjectForIUnknown(pointer);
        Marshal.Release(pointer);
        Guid context = Guid.Empty;
        Marshal.ThrowExceptionForHR(volume.SetMasterVolumeLevelScalar(value, ref context));
        float actual;
        Marshal.ThrowExceptionForHR(volume.GetMasterVolumeLevelScalar(out actual));
        return actual;
    }
}
"""

    scalar = format(percent / 100.0, ".17g")
    script = r"""
$ErrorActionPreference = 'Stop'
$src = @'
""" + csharp + r"""
'@
Add-Type -TypeDefinition $src
$actual = [AudioVolumeSetter]::SetDefault([single]__SCALAR__)
$report = [pscustomobject]@{ VolumePercent = [math]::Round($actual * 100) }
$json = ConvertTo-Json -InputObject $report -Compress
[Console]::Out.WriteLine($json)
[Console]::Out.Flush()
"""
    script = script.replace("__SCALAR__", scalar)
    script += chr(10) + "Write-Output 'AUDIO_VOLUME_TRAILER'" + chr(10)
    vm.push(script)
    yield from vm.call(vm.tick("run_pwsh"))
    result = vm.pop()
    if not isinstance(result, dict) or result.get("exit_code") != 0:
        detail = result.get("stderr", repr(result)) if isinstance(result, dict) else repr(result)
        raise RuntimeError("audio-volume! failed: " + detail)
    try:
        output_lines = [line for line in result.get("stdout", "").splitlines() if line.strip()]
        if not output_lines:
            raise ValueError("PowerShell returned no output lines")
        confirmed = json.loads(output_lines[0])["VolumePercent"]
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Could not verify audio-volume!: " + str(exc))
    if confirmed != percent:
        raise RuntimeError(f"Requested {percent}%, but Windows reports {confirmed}%.")
    print(f"Default playback volume set to {confirmed}%.")
    end-code
    // ( n -- ) Set the default Multimedia playback volume to an integer percentage from 0 to 100.
    /// Uses Windows Core Audio and verifies the resulting endpoint volume; does not change mute state or per-app volumes.
