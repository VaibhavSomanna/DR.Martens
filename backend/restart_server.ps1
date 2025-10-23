# Dr. Martens Backend Server Restart Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dr. Martens Backend Server Restart" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes using port 5000
Write-Host "Checking for processes using port 5000..." -ForegroundColor Yellow

$connections = netstat -ano | Select-String ":5000" | Select-String "LISTENING"

if ($connections) {
    foreach ($connection in $connections) {
        $parts = $connection -split '\s+' | Where-Object { $_ -ne '' }
        $processId = $parts[-1]
        
        if ($processId -and $processId -match '^\d+$') {
            try {
                Write-Host "Killing process $processId..." -ForegroundColor Red
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            } catch {
                Write-Host "Could not kill process $processId" -ForegroundColor DarkRed
            }
        }
    }
    
    Write-Host ""
    Write-Host "Waiting 2 seconds for port to be released..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
} else {
    Write-Host "No processes found using port 5000" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Flask server..." -ForegroundColor Green
Write-Host ""

# Start the Flask application
python app.py
