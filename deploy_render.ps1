# ARTHA AI — Render Blueprint deploy helper
# Opens Render deploy flow for https://github.com/Blackbebertex/Nanda

$RepoUrl = "https://github.com/Blackbebertex/Nanda"
$DeployUrl = "https://render.com/deploy?repo=$RepoUrl"
$BlueprintUrl = "https://dashboard.render.com/blueprint/new"
$HealthUrl = "https://artha-api.onrender.com/health"

Write-Host ""
Write-Host "ARTHA AI — Render Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repo:  $RepoUrl"
Write-Host "Deploy: $DeployUrl"
Write-Host ""

Write-Host "Opening Render deploy page in your browser..." -ForegroundColor Yellow
Start-Process $DeployUrl

Write-Host ""
Write-Host "After login, Render will detect render.yaml and create:" -ForegroundColor Green
Write-Host "  - artha-api      (Python FastAPI — agent endpoints + SKILL.md)"
Write-Host "  - artha-frontend (static UI)"
Write-Host ""
Write-Host "Required env var (set when prompted or in dashboard):" -ForegroundColor Yellow
Write-Host "  GEMINI_API_KEY = your Google Gemini API key"
Write-Host ""
Write-Host "Optional overrides:" -ForegroundColor DarkGray
Write-Host "  GEMINI_MODEL   = gemini-1.5-flash"
Write-Host "  ALLOWED_ORIGINS = auto-wired from frontend service"
Write-Host ""
Write-Host "After deploy, verify:" -ForegroundColor Cyan
Write-Host "  curl https://YOUR-API-URL.onrender.com/health"
Write-Host "  curl https://YOUR-API-URL.onrender.com/skill.md"
Write-Host "  curl -X POST https://YOUR-API-URL.onrender.com/recommend -H ""Content-Type: application/json"" -d ""{\""age\"":28,\""monthly_income\"":80000,\""monthly_expenses\"":45000,\""risk_profile\"":\""Moderate\"",\""goal\"":\""House\""}"""
Write-Host ""
Write-Host "NANDA Town skill URL (use your API host):" -ForegroundColor Magenta
Write-Host "  https://YOUR-API-URL.onrender.com/skill.md"
Write-Host ""

$check = Read-Host "Press Enter after deploy finishes to test health endpoint (or Ctrl+C to skip)"
if ($check -ne $null) {
    try {
        $r = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 30
        Write-Host "Health check ($HealthUrl): $($r.StatusCode)" -ForegroundColor Green
        Write-Host $r.Content
    } catch {
        Write-Host "Health check failed (service may still be building or URL differs):" -ForegroundColor Red
        Write-Host $_.Exception.Message
        Write-Host "Check your actual API URL in Render dashboard -> artha-api -> Settings"
    }
}
