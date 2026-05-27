import socket
import threading
from state_manager import StateManager
from client_handler import ClientHandler

HOST = "0.0.0.0"
PORT = 5000

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVIDOR] Cidade Colaborativa rodando em {HOST}:{PORT}")

    state_manager = StateManager(size=7)
    clients = []

    while True:
        conn, addr = server.accept() 

        handler = ClientHandler(conn, addr, state_manager, clients)
        thread = threading.Thread(target=handler.handle, daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()