@echo off
echo ========================================
echo  LoL Data Analyzer - Mode Selection
echo ========================================
echo.
echo Choose interface mode:
echo [1] Terminal Mode (default)
echo [2] Streamlit Web Mode
echo [3] Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting in Terminal mode...
    set LOL_INTERFACE_MODE=terminal
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo Starting in Streamlit mode...
    echo The web interface will open in your browser at http://localhost:8501
    echo Press Ctrl+C to stop the server
    echo.
    set LOL_INTERFACE_MODE=streamlit
    python main.py
) else if "%choice%"=="3" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice, starting in Terminal mode...
    set LOL_INTERFACE_MODE=terminal
    python main.py
)

pause
