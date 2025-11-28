# AI Learning Coach - Startup Script for Windows
# This script helps you start all services easily

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Learning Coach - Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "env\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv env
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\env\Scripts\Activate.ps1

# Check if .env file exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "Environment file not found. Creating from example..." -ForegroundColor Yellow
    Copy-Item backend\env.example backend\.env
    Write-Host "Please edit backend\.env with your configuration!" -ForegroundColor Red
    Write-Host "Press any key to continue after editing .env file..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$depsInstalled = python -c "import django; import streamlit" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Choose what to start:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Django Backend only (port 8000)"
Write-Host "2. Streamlit Dashboard only (port 8501)"
Write-Host "3. Both Django Backend and Streamlit Dashboard"
Write-Host "4. All services (Django + Streamlit + MCP Server)"
Write-Host "5. Exit"
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "Starting Django Backend..." -ForegroundColor Green
        Set-Location backend
        python manage.py runserver 8000
    }
    "2" {
        Write-Host "Starting Streamlit Dashboard..." -ForegroundColor Green
        Set-Location dashboard
        streamlit run main.py --server.port 8501
    }
    "3" {
        Write-Host "Starting Django Backend and Streamlit Dashboard..." -ForegroundColor Green
        Write-Host ""
        Write-Host "Opening Django Backend in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\..\env\Scripts\Activate.ps1; python manage.py runserver 8000"
        Start-Sleep -Seconds 2
        Write-Host "Opening Streamlit Dashboard in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\dashboard'; .\..\env\Scripts\Activate.ps1; streamlit run main.py --server.port 8501"
        Write-Host ""
        Write-Host "Both services are starting in separate windows!" -ForegroundColor Green
        Write-Host "Django: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Streamlit: http://localhost:8501" -ForegroundColor Cyan
    }
    "4" {
        Write-Host "Starting all services..." -ForegroundColor Green
        Write-Host ""
        Write-Host "Opening Django Backend in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\..\env\Scripts\Activate.ps1; python manage.py runserver 8000"
        Start-Sleep -Seconds 2
        Write-Host "Opening Streamlit Dashboard in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\dashboard'; .\..\env\Scripts\Activate.ps1; streamlit run main.py --server.port 8501"
        Start-Sleep -Seconds 2
        Write-Host "Opening MCP Server in new window..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\mcp_server'; .\..\env\Scripts\Activate.ps1; python main.py"
        Write-Host ""
        Write-Host "All services are starting in separate windows!" -ForegroundColor Green
        Write-Host "Django: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Streamlit: http://localhost:8501" -ForegroundColor Cyan
    }
    "5" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit
    }
}

