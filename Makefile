all : .venv/touchfile
	.venv/bin/python main.py

.venv/touchfile : requirements.txt
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	touch .venv/touchfile
