ifeq ($(OS),Windows_NT)
    VENV_BIN = venv\Scripts
    PYTHON = $(VENV_BIN)\python.exe
    PIP = $(VENV_BIN)\pip.exe
    RM = rmdir /s /q
else
    VENV_BIN = venv/bin
    PYTHON = $(VENV_BIN)/python
    PIP = $(VENV_BIN)/pip
    RM = rm -rf
endif

.PHONY: setup download test run evaluate benchmark clean

setup:
	python3 -m venv venv || python -m venv venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

download:
	$(PYTHON) scripts/download_models.py

test:
	$(PYTHON) -m pytest tests/ -v

run:
	$(PYTHON) run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports

evaluate:
	$(PYTHON) evaluate.py

benchmark:
	$(PYTHON) scripts/benchmark.py

clean:
	$(RM) reports 2>/dev/null || $(RM) reports 2>nul || true
	$(RM) .pytest_cache 2>/dev/null || $(RM) .pytest_cache 2>nul || true
