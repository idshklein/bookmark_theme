param(
    [string]$PluginName = "bookmark_theme",
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$OutputPath = Join-Path $Root $OutputDir

if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
}

$Version = "0.1.0"
$Metadata = Join-Path $Root "metadata.txt"
if (Test-Path $Metadata) {
    $versionLine = Get-Content $Metadata | Where-Object { $_ -match '^version\s*=\s*' } | Select-Object -First 1
    if ($versionLine) {
        $Version = ($versionLine -split '=', 2)[1].Trim()
    }
}

$ZipPath = Join-Path $OutputPath "$PluginName-$Version.zip"
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

$TempRoot = Join-Path $env:TEMP ("{0}_{1}" -f $PluginName, [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempRoot | Out-Null
$Staging = Join-Path $TempRoot $PluginName
New-Item -ItemType Directory -Path $Staging | Out-Null

$Exclude = @(".git", "__pycache__", "dist", "build", ".vscode", ".idea")

Get-ChildItem -Path $Root -Force | Where-Object {
    $name = $_.Name
    $Exclude -notcontains $name
} | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $Staging -Recurse -Force
}

Compress-Archive -Path (Join-Path $TempRoot "$PluginName\*") -DestinationPath $ZipPath -Force
Remove-Item $TempRoot -Recurse -Force

Write-Host "Created package: $ZipPath"
