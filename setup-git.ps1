# Run from C:\dev\fish-screen-specs in PowerShell.
# Cleans up the half-initialized .git left by the sandbox, then inits git,
# creates a feature branch, and makes the first commit.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Remove the corrupted .git and stray temp file the sandbox could not delete.
if (Test-Path ".git") { Remove-Item -Recurse -Force ".git" }
if (Test-Path "testfile.tmp") { Remove-Item -Force "testfile.tmp" }

git init
git checkout -b feature/project-scaffold
git add .
git commit -m "Initial scaffold: DFO fish-screen spec calculator + task tracker"
git log --oneline -1
git status
