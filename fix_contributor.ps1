# Run this in PowerShell started from Windows Start menu (NOT from Cursor).
# This fixes the "cursoragent" contributor by re-creating the commit with only your identity.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Current git config (should be YOU, not cursoragent):" -ForegroundColor Cyan
git config user.name
git config user.email
Write-Host ""

# Set YOUR identity for this repo (use your real GitHub email if you prefer)
git config user.name "mehmetalikosee"
git config user.email "mehmetalikosee@users.noreply.github.com"

# Rewrite the last commit with you as both author AND committer
$env:GIT_AUTHOR_NAME = "mehmetalikosee"
$env:GIT_AUTHOR_EMAIL = "mehmetalikosee@users.noreply.github.com"
$env:GIT_COMMITTER_NAME = "mehmetalikosee"
$env:GIT_COMMITTER_EMAIL = "mehmetalikosee@users.noreply.github.com"

git commit --amend --reset-author --no-edit

Write-Host ""
Write-Host "Commit is now only you. Verifying:" -ForegroundColor Green
git log -1 --format="Author: %an <%ae> | Committer: %cn <%ce>"
Write-Host ""
Write-Host "Now run:  git push origin main --force" -ForegroundColor Yellow
Write-Host "Then hard-refresh the GitHub page (Ctrl+F5)." -ForegroundColor Yellow
