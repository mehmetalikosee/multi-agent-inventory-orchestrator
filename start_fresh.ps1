# Start repo from scratch: one commit, only your identity.
# RUN THIS IN POWERSHELL FROM WINDOWS START (not from Cursor).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$repoUrl = "https://github.com/mehmetalikosee/multi-agent-inventory-orchestrator.git"

Write-Host "Saving remote URL..." -ForegroundColor Cyan
$remoteUrl = $repoUrl
try {
    $existing = git config --get remote.origin.url 2>$null
    if ($existing) { $remoteUrl = $existing }
} catch {}

Write-Host "Removing old git history..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue

Write-Host "Initializing new repo..." -ForegroundColor Cyan
git init
git remote add origin $remoteUrl

Write-Host "Setting your identity (mehmetalikosee)..." -ForegroundColor Cyan
git config user.name "mehmetalikosee"
git config user.email "mehmetalikosee@users.noreply.github.com"

Write-Host "Staging files (respecting .gitignore)..." -ForegroundColor Cyan
git add -A
git status

Write-Host "Creating single initial commit..." -ForegroundColor Cyan
$env:GIT_AUTHOR_NAME = "mehmetalikosee"
$env:GIT_AUTHOR_EMAIL = "mehmetalikosee@users.noreply.github.com"
$env:GIT_COMMITTER_NAME = "mehmetalikosee"
$env:GIT_COMMITTER_EMAIL = "mehmetalikosee@users.noreply.github.com"
git commit -m "Initial commit: Autonomous Business Logic Orchestrator"

git branch -M main

Write-Host ""
Write-Host "Done. One commit, only you:" -ForegroundColor Green
git log -1 --format="Author: %an <%ae> | Committer: %cn <%ce>"
Write-Host ""
Write-Host "Now run (from this same PowerShell):" -ForegroundColor Yellow
Write-Host "  git push -u origin main --force" -ForegroundColor White
Write-Host ""
Write-Host "Then hard-refresh GitHub (Ctrl+F5)." -ForegroundColor Yellow
