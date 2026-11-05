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

$innerCode = @"
Add-Type -AssemblyName System.Windows.Forms
`$form = New-Object System.Windows.Forms.Form -Property @{ TopMost = `$true }
[void][System.Windows.Forms.MessageBox]::Show(`$form, '$escapedMsg', '$escapedTitle', 'OK', '$Icon')
`$form.Dispose()
"@

if ($Wait) {
    Add-Type -AssemblyName System.Windows.Forms
    $form = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }
    [void][System.Windows.Forms.MessageBox]::Show($form, $Message, $Title, 'OK', $Icon)
    $form.Dispose()
} else {
    $bytes = [System.Text.Encoding]::Unicode.GetBytes($innerCode)
    $encoded = [Convert]::ToBase64String($bytes)
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList "-NoProfile", "-NonInteractive", "-EncodedCommand", $encoded
}
