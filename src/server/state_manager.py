import sqlite3
import threading
import time
from models.structure import Structure

DB_PATH = "cidade.db"

class StateManager:
    def __init__(self, size=10):
        self.size = size
        self.lock = threading.Lock()
        self._init_db()
        self.grid = self._load_grid()

    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS estruturas (
                    x         INTEGER NOT NULL,
                    y         INTEGER NOT NULL,
                    tipo      TEXT    NOT NULL,
                    autor     TEXT    NOT NULL,
                    horario   TEXT    NOT NULL,
                    PRIMARY KEY (x, y)             
                )
            """)
            conn.commit()

    def _load_grid(self):
        """Carrega o estado persistido no banco para a memória ao iniciar"""
        grid = [[None] * self.size for _ in range(self.size)]
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT x, y, tipo, autor, horario FROM estruturas"
            ).fetchall()
        for x, y, tipo, autor, horario in rows:
            if 0 <= x < self.size and 0 <= y < self.size:
                grid[x][y] = Structure(tipo, autor, horario)
        return grid
    
    def _db_insert(self, x, y, tipo, autor, horario):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO estruturas (x, y, tipo, autor, horario) VALUES (?, ?, ?, ?, ?)",
                (x, y, tipo, autor, horario)
            )
            conn.commit()

    def _db_delete(self, x, y):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM estruturas WHERE x=? AND y=?", (x,y))
            conn.commit()
    

    def place_structure(self, x, y, structure_type, author):
        with self.lock:
            if self.grid[x][y] is not None:
                return False, "Posição já ocupada"
            timestamp = time.strftime("%H:%M:%S")
            self.grid[x][y] = Structure(structure_type, author, timestamp)

        self._db_insert(x, y, structure_type, author, timestamp)
        return True, "Estrutura alocada"
    
    def remove_structure(self, x, y):
        with self.lock:
            if self.grid[x][y] is None:
                return False, "Posição já está vazia."
            self.grid[x][y] = None

        self._db_delete(x, y)
        return True, "Estrutura removida"
    
    def get_state(self):
        with self.lock:
            return [
                [cell.to_dict() if cell else None for cell in row]
                for row in self.grid
            ]