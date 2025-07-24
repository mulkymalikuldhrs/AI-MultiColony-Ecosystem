@echo off
setlocal enabledelayedexpansion

:: ╔══════════════════════════════════════════════════════════════╗
:: ║                🚀 AI-MultiColony-Ecosystem v7.2.4            ║
:: ║                     Unified Installer System                 ║
:: ║          🇮🇩 Made with ❤️ by Mulky Malikul Dhaher 🇮🇩        ║
:: ╚══════════════════════════════════════════════════════════════╝

:: Set colors for output
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: Function to print section headers
:print_header
echo.
echo %BLUE%╔════════════════════════════════════════════════════════════════════════════╗%NC%
echo %BLUE%║ %YELLOW%%~1%BLUE% ║%NC%
echo %BLUE%╚════════════════════════════════════════════════════════════════════════════╝%NC%
goto :eof

:: Check if Python 3.8+ is installed
:check_python
call :print_header "Checking Python Installation"

python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%❌ Python is not installed. Please install Python 3.8+ and try again.%NC%
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "python_version=%%a"
echo %GREEN%✅ Python %python_version% is installed%NC%

for /f "tokens=1,2 delims=." %%a in ("%python_version%") do (
    set "major=%%a"
    set "minor=%%b"
)

if %major% geq 3 (
    if %minor% geq 8 (
        echo %GREEN%✅ Python version is 3.8+%NC%
    ) else (
        echo %RED%❌ Python version must be 3.8+. Please upgrade Python and try again.%NC%
        exit /b 1
    )
) else (
    echo %RED%❌ Python version must be 3.8+. Please upgrade Python and try again.%NC%
    exit /b 1
)
goto :eof

:: Install core dependencies
:install_core_dependencies
call :print_header "Installing Core Dependencies"

echo %YELLOW%ℹ️ Installing Flask, Flask-SocketIO, Flask-CORS, PyYAML, Requests, and other core packages...%NC%
pip install flask flask-socketio flask-cors pyyaml requests aiofiles fastapi uvicorn

if %ERRORLEVEL% equ 0 (
    echo %GREEN%✅ Core dependencies installed successfully%NC%
) else (
    echo %RED%❌ Failed to install core dependencies%NC%
    exit /b 1
)
goto :eof

:: Install optional dependencies
:install_optional_dependencies
call :print_header "Installing Optional Dependencies"

echo %YELLOW%ℹ️ Installing additional packages for extended functionality...%NC%

:: Network and system packages
pip install netifaces paramiko asyncpg dnspython

:: AI and data science packages
pip install arxiv nltk scikit-learn seaborn spacy

:: Security and utilities
pip install pyotp whois python-nmap qrcode

:: Image processing
pip install opencv-python-headless pillow

:: Cryptography
pip install cryptography

:: Docker support (if available)
pip install docker

echo %GREEN%✅ Optional dependencies installed successfully%NC%
goto :eof

:: Download NLTK data
:download_nltk_data
call :print_header "Downloading NLTK Data"

echo %YELLOW%ℹ️ Downloading NLTK data for natural language processing...%NC%
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

echo %GREEN%✅ NLTK data downloaded successfully%NC%
goto :eof

:: Download spaCy model
:download_spacy_model
call :print_header "Downloading spaCy Model"

echo %YELLOW%ℹ️ Downloading spaCy English model...%NC%
python -m spacy download en_core_web_sm

echo %GREEN%✅ spaCy model downloaded successfully%NC%
goto :eof

:: Create necessary directories
:create_directories
call :print_header "Creating System Directories"

if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\task_queue mkdir data\task_queue
if not exist agent_output mkdir agent_output
if not exist projects mkdir projects

echo %GREEN%✅ System directories created successfully%NC%
goto :eof

:: Configure system
:configure_system
call :print_header "Configuring System"

:: Create a default configuration if it doesn't exist
if not exist config mkdir config
if not exist config\system_config.yaml (
    echo system: > config\system_config.yaml
    echo   name: "AI MultiColony Ecosystem" >> config\system_config.yaml
    echo   version: "7.2.4" >> config\system_config.yaml
    echo   owner: "Mulky Malikul Dhaher" >> config\system_config.yaml
    echo   owner_id: "1108151509970001" >> config\system_config.yaml
    echo. >> config\system_config.yaml
    echo web_interface: >> config\system_config.yaml
    echo   enabled: true >> config\system_config.yaml
    echo   port: 8080 >> config\system_config.yaml
    echo   host: "0.0.0.0" >> config\system_config.yaml
    echo   debug: false >> config\system_config.yaml
    echo. >> config\system_config.yaml
    echo agents: >> config\system_config.yaml
    echo   auto_discover: true >> config\system_config.yaml
    echo   agents_dir: "colony/agents" >> config\system_config.yaml
    echo   default_status: "inactive" >> config\system_config.yaml
    echo. >> config\system_config.yaml
    echo llm: >> config\system_config.yaml
    echo   provider: "llm7" >> config\system_config.yaml
    echo   api_key: "" >> config\system_config.yaml
    echo   endpoint: "https://api.llm7.io/v1" >> config\system_config.yaml
    
    echo %GREEN%✅ Default configuration created%NC%
) else (
    echo %YELLOW%ℹ️ Configuration file already exists, skipping%NC%
)
goto :eof

:: Run system analyzer
:run_system_analyzer
call :print_header "Running System Analyzer"

echo %YELLOW%ℹ️ Analyzing system health...%NC%
if exist system_analyzer.py (
    python system_analyzer.py
) else (
    echo %YELLOW%ℹ️ System analyzer not found, skipping%NC%
)
goto :eof

:: Launch the system
:launch_system
call :print_header "Launching AI-MultiColony-Ecosystem"

echo %YELLOW%ℹ️ Starting the system with web UI...%NC%
python main.py --web-ui
goto :eof

:: Main installation process
:main
cls
echo %YELLOW%
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                🚀 AI-MultiColony-Ecosystem v7.2.4            ║
echo ║                     Unified Installer System                 ║
echo ║          🇮🇩 Made with ❤️ by Mulky Malikul Dhaher 🇮🇩        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo %NC%

echo %YELLOW%This installer will set up the AI-MultiColony-Ecosystem with all dependencies.%NC%
echo %YELLOW%The process may take several minutes depending on your internet connection.%NC%
echo.

set /p choice="Do you want to continue? (y/n): "
if /i not "%choice%"=="y" (
    echo Installation cancelled.
    exit /b 0
)

:: Run installation steps
call :check_python
call :install_core_dependencies
call :install_optional_dependencies
call :download_nltk_data
call :download_spacy_model
call :create_directories
call :configure_system
call :run_system_analyzer

echo.
echo %GREEN%╔══════════════════════════════════════════════════════════════╗%NC%
echo %GREEN%║                🎉 Installation Complete! 🎉                  ║%NC%
echo %GREEN%╚══════════════════════════════════════════════════════════════╝%NC%
echo.
echo %YELLOW%To launch the system, run:%NC%
echo %BLUE%python main.py --web-ui%NC%
echo.
echo %YELLOW%Or you can launch it now:%NC%
set /p launch_choice="Launch the system now? (y/n): "
if /i "%launch_choice%"=="y" (
    call :launch_system
) else (
    echo %GREEN%Installation completed successfully. You can launch the system later.%NC%
)
goto :eof

:: Start the main function
call :main
endlocal