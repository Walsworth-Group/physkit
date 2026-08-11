#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install PhysKit skills into a vendor-neutral location shared by Codex, OpenCode, and Gemini CLI.

.DESCRIPTION
    PhysKit's skills are written to the open Agent Skills standard (SKILL.md). This script projects
    every skill from this kit's canonical ./skills/ directory into ~/.agents/skills/ (the user-scope
    location that Codex, OpenCode, and Gemini CLI all scan), so those harnesses auto-discover them the
    same way Claude Code does through its plugin.

    This script does NOT touch Claude Code. Install PhysKit on Claude Code the usual way:
        claude plugin marketplace add <path-to-kit>
        claude plugin install physkit@physkit

    The kit's ./skills/ directory remains the single source of truth; this only copies (or links) it
    outward. Re-run after updating the kit to refresh the installed copy.

.PARAMETER Target
    Destination skills directory. Default: ~/.agents/skills

.PARAMETER Link
    Create directory symlinks instead of copies (live-linked, never drifts). On Windows this needs
    Developer Mode or an elevated shell.

.PARAMETER Uninstall
    Remove the PhysKit skills previously installed to Target (only the skills this kit provides).

.EXAMPLE
    ./install-skills.ps1
    Copy all PhysKit skills into ~/.agents/skills

.EXAMPLE
    ./install-skills.ps1 -Target ~/.config/opencode/skills
    Install into OpenCode's own global skills directory instead

.EXAMPLE
    ./install-skills.ps1 -Uninstall
    Remove PhysKit skills from ~/.agents/skills
#>
param(
    [string]$Target = (Join-Path (Join-Path $HOME ".agents") "skills"),
    [switch]$Link,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

$src = Resolve-Path (Join-Path (Join-Path $PSScriptRoot "..") "skills")
$skills = Get-ChildItem -Path $src -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } |
    Sort-Object Name

if (-not $Uninstall) {
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
}

$count = 0
foreach ($skill in $skills) {
    $dest = Join-Path $Target $skill.Name

    if ($Uninstall) {
        if (Test-Path $dest) {
            Remove-Item -Recurse -Force $dest
            Write-Host "removed  $($skill.Name)"
            $count++
        }
        continue
    }

    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    if ($Link) {
        New-Item -ItemType SymbolicLink -Path $dest -Target $skill.FullName | Out-Null
        Write-Host "linked   $($skill.Name)"
    } else {
        Copy-Item -Recurse -Path $skill.FullName -Destination $dest
        Write-Host "copied   $($skill.Name)"
    }
    $count++
}

Write-Host ""
if ($Uninstall) {
    Write-Host "Uninstalled $count PhysKit skills from $Target"
} else {
    Write-Host "Installed $count PhysKit skills at $Target"
    Write-Host "Codex, OpenCode, and Gemini CLI will discover them on next launch."
}
