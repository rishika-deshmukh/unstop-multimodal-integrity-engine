#!/usr/bin/env bash
# ==============================================================================
# Cross-Platform Setup Script for Linux and macOS
# Multimodal Submission Integrity & Plagiarism Detection Engine
# ==============================================================================
set -e

echo "=== Setting up Unstop Multimodal Integrity Engine ==="

# 1. Detect Python 3.10+
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 not found. Please install Python 3.10+."
    exit 1
fi

echo "[INFO] Using Python: $($PYTHON_CMD --version)"

# 2. Create virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment at ./venv..."
    $PYTHON_CMD -m venv venv
else
    echo "[INFO] Existing virtual environment found at ./venv."
fi

# 3. Upgrade pip and install pinned requirements
echo "[INFO] Installing dependencies from requirements.txt..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Download NLTK tokenizers
echo "[INFO] Downloading NLTK tokenizer models..."
./venv/bin/python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

echo "=== Setup complete! ==="
echo "To run the pipeline:"
echo "  ./venv/bin/python run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports"
echo "To run empirical evaluation:"
echo "  ./venv/bin/python evaluate.py"
echo "To run test suite:"
echo "  ./venv/bin/python -m pytest tests/ -v"
