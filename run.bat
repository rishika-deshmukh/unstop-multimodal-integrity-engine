@echo off
echo ========================================================
echo Unstop AI Integrity Engine: Execution Runner
echo ========================================================

if not exist "venv" (
    echo [INFO] Initializing virtual environment...
    python -m venv venv
    call .\venv\Scripts\python.exe -m pip install --upgrade pip
    call .\venv\Scripts\python.exe -m pip install -r requirements.txt
    call .\venv\Scripts\python.exe -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
)

echo [INFO] Running full integrity check pipeline...
.\venv\Scripts\python.exe run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports

echo [INFO] Computing evaluation metrics against ground truth...
.\venv\Scripts\python.exe evaluate.py

echo ========================================================
echo Verification Complete. Reports saved to ./reports/
echo ========================================================
pause
