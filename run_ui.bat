@echo off
REM Start the Interview Agent UI with Streamlit

echo Starting NCO Interview Agent UI...
echo.

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1

if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo Opening Interview Agent in your browser...
python -m streamlit run app.py

pause
