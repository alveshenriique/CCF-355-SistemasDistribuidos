import Pyro5.api

from grid_manager import GridManager
from session_manager import SessionManager


def start_server():
    grid    = GridManager(size=7)
    session = SessionManager()

    with Pyro5.api.Daemon() as daemon:
        grid_uri    = daemon.register(grid,    "gridcity.grid")
        session_uri = daemon.register(session, "gridcity.session")

        with Pyro5.api.locate_ns() as ns:
            ns.register("gridcity.grid",    grid_uri)
            ns.register("gridcity.session", session_uri)

        print("[SERVIDOR] GridCity registrado no Name Server")
        print(f"[SERVIDOR] Grade   -> {grid_uri}")
        print(f"[SERVIDOR] Sessão  -> {session_uri}")
        daemon.requestLoop()


if __name__ == "__main__":
    start_server()
