.PHONY: install nameserver server client

install:
	pip3 install -r requirements.txt --break-system-packages

nameserver:
	python3 -m Pyro5.nameserver

server:
	PYTHONPATH=src python3 src/server/server.py

client:
	PYTHONPATH=src python3 src/client/client.py
