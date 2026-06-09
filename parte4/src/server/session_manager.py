import threading

import Pyro5.api


@Pyro5.api.expose
class SessionManager:
    def __init__(self):
        self.lock   = threading.Lock()
        self._users = {}

    def join(self, username):
        with self.lock:
            self._users[username] = True

    def leave(self, username):
        with self.lock:
            self._users.pop(username, None)

    def get_users(self):
        with self.lock:
            names = list(self._users.keys())
        return {"count": len(names), "usernames": names}
