.PHONY: install server client

install:
	pip3 install -r requirements.txt --break-system-packages

server:
	PYTHONPATH=src python3 src/server/server.py

client:
	PYTHONPATH=src python3 src/client/client.py
