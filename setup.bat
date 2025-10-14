@echo off
REM Sales Intelligence Agent - Windows Setup Script

echo ============================================================
echo Sales Intelligence Agent - Setup Script
echo ============================================================
echo.

REM Check if Docker is installed
echo Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker is installed

echo.
echo Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed

echo.
echo ============================================================
echo Step 1: Environment Configuration
echo ============================================================

REM Check if .env exists
if not exist "backend\.env" (
    echo Creating .env file from template...
    copy "backend\.env.example" "backend\.env"
    echo.
    echo [IMPORTANT] Please edit backend\.env and add your API keys:
    echo   - ANTHROPIC_API_KEY (Required)
    echo   - CLEARBIT_API_KEY (Optional)
    echo   - HUNTER_API_KEY (Optional)
    echo.
    echo Press any key to open .env file in notepad...
    pause >nul
    notepad "backend\.env"
) else (
    echo [OK] .env file already exists
)

echo.
echo ============================================================
echo Step 2: Building Docker Containers
echo ============================================================
echo This may take several minutes on first run...
echo.

docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build containers
    pause
    exit /b 1
)

echo.
echo [OK] Containers built successfully

echo.
echo ============================================================
echo Step 3: Starting Services
echo ============================================================
echo.

docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

echo.
echo [OK] Services started successfully

echo.
echo Waiting for services to initialize (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo ============================================================
echo Step 4: Verifying Setup
echo ============================================================
echo.

REM Check if services are running
docker-compose ps

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Your services are now running:
echo   - Backend API:     http://localhost:8000
echo   - API Docs:        http://localhost:8000/docs
echo   - Flower Monitor:  http://localhost:5555
echo.
echo Useful commands:
echo   docker-compose logs -f     - View logs
echo   docker-compose down        - Stop services
echo   docker-compose restart     - Restart services
echo.
echo Press any key to open the API documentation in your browser...
pause >nul

start http://localhost:8000/docs

echo.
echo Done! Press any key to exit...
pause >nul
