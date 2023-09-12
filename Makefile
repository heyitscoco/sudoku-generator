setup: compile install

compile:
	python -m pip install pip-tools
	python -m piptools compile requirements.in

install:
	python -m pip install -r requirements.txt
