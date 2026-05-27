import socket
import threading
import json

from PyQt6.QtCore import QObject, pyqtSignal


class NetworkSignals(QObject):
    state_updated     = pyqtSignal(list)
    users_updated     = pyqtSignal(dict)
    response_received = pyqtSignal(dict)


class NetworkClient:
    def __init__(self, host, port, signals: NetworkSignals):
        self.host    = host
        self.port    = port
        self.signals = signals
        self.sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.host, self.port))
        # daemon=True: thread encerra automaticamente quando a janela fechar
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data
                while buffer:
                    try:
                        # raw_decode permite extrair um objeto JSON por vez do buffer,
                        # necessário porque um único recv pode conter múltiplas mensagens
                        msg, idx = json.JSONDecoder().raw_decode(buffer)
                        buffer = buffer[idx:].lstrip()
                        self._dispatch(msg)
                    except json.JSONDecodeError:
                        break
            except Exception:
                break

    def _dispatch(self, msg):
        t = msg.get("type")
        if t == "UPDATE":
            self.signals.state_updated.emit(msg["state"])
        elif t == "USERS":
            self.signals.users_updated.emit(msg)
        elif t == "RESPONSE":
            self.signals.response_received.emit(msg)

    def send(self, msg):
        try:
            self.sock.send(json.dumps(msg).encode("utf-8"))
        except Exception:
            pass
