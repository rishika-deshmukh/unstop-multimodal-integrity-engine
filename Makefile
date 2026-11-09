.PHONY: setup download test run evaluate clean

setup:
	python -m venv venv
	.\venv\Scripts\python.exe -m pip install --upgrade pip
	.\venv\Scripts\python.exe -m pip install -r requirements.txt
	.\venv\Scripts\python.exe -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

download:
	.\venv\Scripts\python.exe scripts\download_models.py

generate-data:
	.\venv\Scripts\python.exe scripts\generate_synthetic_dataset.py

test:
	.\venv\Scripts\python.exe -m pytest tests/ -v

run:
	.\venv\Scripts\python.exe run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports

evaluate:
	.\venv\Scripts\python.exe evaluate.py

clean:
	rmdir /s /q reports 2>nul || true
	rmdir /s /q .pytest_cache 2>nul || true
