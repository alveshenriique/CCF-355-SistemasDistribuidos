import json

class ClientHandler:
    def __init__(self, conn, addr, state_manager, clients):
        self.conn = conn
        self.addr = addr
        self.state_manager = state_manager
        self.clients = clients
        # fallback: garante identidade nos logs mesmo se o JOIN nunca chegar
        self.username = str(addr)

    def handle(self):
        print(f"[CONNECT] {self.addr}")

        try:
            data = self.conn.recv(4096).decode()
            msg = json.loads(data)
            if msg.get("type") == "JOIN":
                self.username = msg.get("username", str(self.addr))
        except:
            pass

        # append após o JOIN para que broadcast_users já envie o username correto
        self.clients.append(self)
        self.broadcast_users()

        self.send({
            "type": "UPDATE",
            "state": self.state_manager.get_state()
        })

        while True:
            try:
                data = self.conn.recv(4096).decode()
                if not data:
                    break

                msg = json.loads(data)
                response = self.process_message(msg)

                self.send(response)

                if response["success"]:
                    self.broadcast_state()

            except:
                break

        self.conn.close()
        self.clients.remove(self)
        self.broadcast_users()

        print(f"[DISCONNECT] {self.addr} ({self.username})")

    def process_message(self, msg):
        action = msg.get("type")
        x = msg.get("x")
        y = msg.get("y")

        if action == "PLACE":
            success, message = self.state_manager.place_structure(
                x, y, msg["structure_type"], msg["author"]
            )
        elif action == "REMOVE":
            success, message = self.state_manager.remove_structure(x, y)
        else:
            return {"type": "RESPONSE", "success": False, "message": "Ação inválida"}

        return {
            "type": "RESPONSE",
            "success": success,
            "message": message,
            "action": action,
            "x": x,
            "y": y,
            "structure_type": msg.get("structure_type", "")
        }

    def send(self, data):
        try:
            self.conn.send(json.dumps(data).encode())
        except:
            pass

    def broadcast_state(self):
        data = json.dumps({
            "type": "UPDATE",
            "state": self.state_manager.get_state()
        }).encode()

        for handler in self.clients:
            try:
                handler.conn.send(data)
            except:
                pass

    def broadcast_users(self):
        usernames = [h.username for h in self.clients]
        data = json.dumps({
            "type": "USERS",
            "count": len(self.clients),
            "usernames": usernames
        }).encode()

        for handler in self.clients:
            try:
                handler.conn.send(data)
            except:
                pass
