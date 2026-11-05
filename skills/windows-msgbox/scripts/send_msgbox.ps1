[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string]$Message,

    [string]$Title = "💡 peforth 提醒",

    [ValidateSet("Information", "Warning", "Error", "Question", "None")]
    [string]$Icon = "Information",

    [switch]$Wait
)

$escapedMsg = $Message.Replace("'", "''")
$escapedTitle = $Title.Replace("'", "''")

$code = "Add-Type -AssemblyName System.Windows.Forms; [void][System.Windows.Forms.MessageBox]::Show('$escapedMsg', '$escapedTitle', 'OK', '$Icon', 'Button1', 'ServiceNotification')"

if ($Wait) {
    Add-Type -AssemblyName System.Windows.Forms
    [void][System.Windows.Forms.MessageBox]::Show($Message, $Title, 'OK', $Icon, 'Button1', 'ServiceNotification')
} else {
    $bytes = [System.Text.Encoding]::Unicode.GetBytes($code)
    $encoded = [Convert]::ToBase64String($bytes)
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList "-NoProfile", "-NonInteractive", "-EncodedCommand", $encoded
}
