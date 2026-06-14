import time
import threading

import Pyro5.api
from PyQt6.QtCore import QObject, pyqtSignal


class NetworkSignals(QObject):
    state_updated     = pyqtSignal(list)
    users_updated     = pyqtSignal(dict)
    response_received = pyqtSignal(dict)


class NetworkClient:
    def __init__(self, signals: NetworkSignals, username: str):
        self.signals  = signals
        self.username = username
        self._grid    = Pyro5.api.Proxy("PYRONAME:gridcity.grid")
        self._session = Pyro5.api.Proxy("PYRONAME:gridcity.session")

    def connect(self):
        self._session.join(self.username)
        threading.Thread(target=self._poll, daemon=True).start()

    def _poll(self):
        grid    = Pyro5.api.Proxy("PYRONAME:gridcity.grid")
        session = Pyro5.api.Proxy("PYRONAME:gridcity.session")
        while True:
            try:
                self.signals.state_updated.emit(grid.get_state())
                self.signals.users_updated.emit(session.get_users())
            except Exception:
                pass
            time.sleep(0.5)

    def place_structure(self, x, y, structure_type):
        try:
            result = self._grid.place_structure(x, y, structure_type, self.username)
            success, message = result[0], result[1]
            self.signals.response_received.emit({
                "success": success,
                "message": message,
                "action": "PLACE",
                "x": x, "y": y,
                "structure_type": structure_type,
            })
        except Exception as e:
            self.signals.response_received.emit({"success": False, "message": str(e)})

    def remove_structure(self, x, y):
        try:
            result = self._grid.remove_structure(x, y)
            success, message = result[0], result[1]
            self.signals.response_received.emit({
                "success": success,
                "message": message,
                "action": "REMOVE",
                "x": x, "y": y,
                "structure_type": "",
            })
        except Exception as e:
            self.signals.response_received.emit({"success": False, "message": str(e)})

    def disconnect(self):
        try:
            self._session.leave(self.username)
        except Exception:
            pass