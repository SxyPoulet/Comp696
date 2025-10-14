@echo off
echo Starting Sales Intelligence Agent Development Environment
echo.

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and start it
    pause
    exit /b 1
)

echo.
echo Starting services with docker-compose...
docker-compose up -d

echo.
echo Services are starting up...
echo.
echo Available URLs:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Flower:    http://localhost:5555
echo.
echo Press Ctrl+C to view logs, or close this window
echo.

docker-compose logs -f
