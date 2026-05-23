import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QButtonGroup, QTextEdit,
    QFrame, QLineEdit, QSizePolicy,
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QCursor

from network import NetworkClient, NetworkSignals
import protocol

HOST = "127.0.0.1"
PORT = 5000
SIZE = 10
CELL = 65   # pixels por célula

# --- Paleta ---
BG_MAIN    = "#EDE9E0"
BG_PANEL   = "#F4F1EB"
BG_HEADER  = "#1A202C"
GRID_EVEN  = "#C5D9A8"
GRID_ODD   = "#B8CF98"
GRID_BORD  = "#A8C07A"
ACCENT     = "#3B82F6"
RED        = "#EF4444"
TEXT_DARK  = "#1A202C"
TEXT_LIGHT = "#FFFFFF"
TEXT_SEC   = "#4A5568"   # labels de seção — mais escuro que antes
TEXT_MUTED = "#718096"
DIVIDER    = "#D1CBC0"
BTN_IDLE   = "#E8E4DC"

# --- Estruturas ---
STRUCTURES = {
    "Casa":    {"emoji": "🏠", "color": "#FEF3C7", "border": "#D97706"},
    "Estrada": {"emoji": "🛣️",  "color": "#E5E7EB", "border": "#6B7280"},
    "Hospital": {"emoji": "🏥", "color": "#FEE2E2", "border": "#DC2626"},
    "Loja":    {"emoji": "🏪", "color": "#DBEAFE", "border": "#2563EB"},
    "Praça":   {"emoji": "⛲", "color": "#ECFDF5", "border": "#10B981"},
    "Escola":  {"emoji": "🏫", "color": "#EDE9FE", "border": "#7C3AED"},
    "Parque":  {"emoji": "🌲", "color": "#CFFAFE", "border": "#0891B2"},
    "Fábrica": {"emoji": "🏭", "color": "#FEE2E2", "border": "#DC2626"},
}
STRUCT_NAMES = list(STRUCTURES.keys())


def _user_color(name: str) -> str:
    h = abs(hash(name)) % 0xFFFFFF
    r = max((h >> 16) & 0xFF, 80)
    g = max((h >> 8)  & 0xFF, 80)
    b = max( h        & 0xFF, 80)
    return f"#{r:02X}{g:02X}{b:02X}"


# =============================================================
# DIALOG DE LOGIN (maior e estilizado)
# =============================================================

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cidade Colaborativa")
        self.setFixedSize(460, 260)
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 36, 40, 36)
        lay.setSpacing(14)

        # título
        title = QLabel("🏙️  Bem-vindo à Cidade Colaborativa")
        title.setFont(QFont("Helvetica", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        # subtítulo
        sub = QLabel("Digite seu nome para entrar no mapa:")
        sub.setFont(QFont("Helvetica", 11))
        sub.setStyleSheet(f"color: {TEXT_SEC}; background: transparent;")
        lay.addWidget(sub)

        # campo de texto
        self.field = QLineEdit()
        self.field.setFont(QFont("Helvetica", 13))
        self.field.setPlaceholderText("Seu nome aqui...")
        self.field.setFixedHeight(44)
        self.field.setStyleSheet(
            f"background: white; color: {TEXT_DARK};"
            "border: 2px solid #C5C0B8; border-radius: 8px; padding: 6px 14px;"
        )
        self.field.returnPressed.connect(self.accept)
        lay.addWidget(self.field)

        # botão
        btn = QPushButton("Entrar na cidade  →")
        btn.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
        btn.setFixedHeight(46)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #2563EB;
            }}
        """)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)

    def get_name(self) -> str:
        return self.field.text().strip()


# =============================================================
# DIALOG GENÉRICO ESTILIZADO
# =============================================================

class StyledDialog(QDialog):
    """Dialog de aviso/erro que segue o visual da aplicação."""

    def __init__(self, parent, title: str, message: str, is_error: bool = False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(380, 190)
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 28, 30, 24)
        lay.setSpacing(14)

        # título com ícone
        icon = "❌" if is_error else "ℹ️"
        title_lbl = QLabel(f"{icon}  {title}")
        title_lbl.setFont(QFont("Helvetica", 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {TEXT_DARK}; background: transparent;")
        lay.addWidget(title_lbl)

        # mensagem
        msg_lbl = QLabel(message)
        msg_lbl.setFont(QFont("Helvetica", 10))
        msg_lbl.setStyleSheet(f"color: {TEXT_SEC}; background: transparent;")
        msg_lbl.setWordWrap(True)
        lay.addWidget(msg_lbl)

        lay.addStretch()

        # botão OK
        color = "#DC2626" if is_error else ACCENT
        btn = QPushButton("OK")
        btn.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        btn.setFixedHeight(40)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 7px;
            }}
            QPushButton:hover {{
                background-color: {'#B91C1C' if is_error else '#2563EB'};
            }}
        """)
        btn.clicked.connect(self.accept)
        lay.addWidget(btn)


def show_info(parent, title: str, message: str):
    StyledDialog(parent, title, message, is_error=False).exec()


def show_error(parent, title: str, message: str):
    StyledDialog(parent, title, message, is_error=True).exec()


# =============================================================
# WIDGET DO MAPA (desenho via QPainter)
# =============================================================

class CityGrid(QWidget):
    def __init__(self, on_left_click, on_right_click):
        super().__init__()
        self._on_left   = on_left_click
        self._on_right  = on_right_click
        self.grid_state = [[None] * SIZE for _ in range(SIZE)]
        self.hovered    = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(SIZE * CELL, SIZE * CELL)
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    # --- Geometria dinâmica ---
    # O grid é sempre quadrado e centralizado dentro do widget,
    # independente de o frame ser mais largo ou mais alto.

    @property
    def cs(self) -> int:
        """Tamanho de cada célula, recalculado a cada resize."""
        return min(self.width(), self.height()) // SIZE

    @property
    def ox(self) -> int:
        """Offset horizontal para centralizar o grid no widget."""
        return (self.width()  - self.cs * SIZE) // 2

    @property
    def oy(self) -> int:
        """Offset vertical para centralizar o grid no widget."""
        return (self.height() - self.cs * SIZE) // 2

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()

    def set_state(self, state):
        self.grid_state = state
        self.update()

    def _cell(self, pos):
        cs = self.cs
        x = pos.x() - self.ox
        y = pos.y() - self.oy
        col, row = x // cs, y // cs
        if 0 <= row < SIZE and 0 <= col < SIZE:
            return row, col
        return None, None

    def mousePressEvent(self, event):
        row, col = self._cell(event.pos())
        if row is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_left(row, col)
        elif event.button() == Qt.MouseButton.RightButton:
            self._on_right(row, col)

    def mouseMoveEvent(self, event):
        rc = self._cell(event.pos())
        if rc != self.hovered:
            self.hovered = rc
            self.update()

    def leaveEvent(self, event):
        self.hovered = None
        self.update()

    def paintEvent(self, _event):
        cs, ox, oy = self.cs, self.ox, self.oy
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for row in range(SIZE):
            for col in range(SIZE):
                self._draw_cell(painter, row, col, cs, ox, oy)
        if self.hovered and self.hovered[0] is not None:
            row, col = self.hovered
            empty = self.grid_state[row][col] is None
            self._draw_hover(painter, row, col, cs, ox, oy, ACCENT if empty else RED)

    def _draw_cell(self, painter, row, col, cs, ox, oy):
        x1 = ox + col * cs + 2
        y1 = oy + row * cs + 2
        w  = cs - 4
        h  = cs - 4
        cell = self.grid_state[row][col]

        if cell:
            info = STRUCTURES.get(cell["type"],
                                  {"emoji": "?", "color": "#EEE", "border": "#999"})
            painter.setBrush(QBrush(QColor(info["color"])))
            painter.setPen(QPen(QColor(info["border"]), 2))
            painter.drawRect(x1, y1, w, h)

            font = QFont()
            font.setPointSize(max(8, cs // 4))
            painter.setFont(font)
            painter.setPen(QPen(QColor("#000000")))
            painter.drawText(
                QRect(x1, y1, w, h - cs // 3),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                info["emoji"]
            )

            font.setPointSize(max(5, cs // 9))
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#374151")))
            painter.drawText(QRect(x1, y1 + h - cs // 3, w, cs // 5),
                             Qt.AlignmentFlag.AlignCenter, cell["type"])

            font.setPointSize(max(4, cs // 11))
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QPen(QColor("#6B7280")))
            painter.drawText(QRect(x1, y1 + h - cs // 6, w, cs // 6),
                             Qt.AlignmentFlag.AlignCenter, cell["author"][:10])
        else:
            bg = QColor(GRID_EVEN) if (row + col) % 2 == 0 else QColor(GRID_ODD)
            painter.setBrush(QBrush(bg))
            painter.setPen(QPen(QColor(GRID_BORD), 1))
            painter.drawRect(x1, y1, w, h)

    def _draw_hover(self, painter, row, col, cs, ox, oy, color):
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(color), 3))
        painter.drawRect(ox + col * cs + 2, oy + row * cs + 2, cs - 4, cs - 4)


# =============================================================
# JANELA PRINCIPAL
# =============================================================

class MainWindow(QMainWindow):
    def __init__(self, author: str):
        super().__init__()
        self.author          = author
        self.last_action     = None
        self.grid_state      = [[None] * SIZE for _ in range(SIZE)]
        self.selected_struct = STRUCT_NAMES[0]

        self.setWindowTitle("Cidade Colaborativa")
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        # Rede
        self.signals = NetworkSignals()
        self.signals.state_updated.connect(self._on_state_updated)
        self.signals.users_updated.connect(self._on_users_updated)
        self.signals.response_received.connect(self._on_response)

        self.net = NetworkClient(HOST, PORT, self.signals)
        self.net.connect()
        self.net.send(protocol.create_join(self.author))

        self._build_ui()

        self.setMinimumSize(SIZE * CELL + 310, SIZE * CELL + 80)
        self.resize(1050, 810)

    # =========================================================
    # CONSTRUÇÃO DA UI
    # =========================================================

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(self._make_header())

        body = QWidget()
        body.setStyleSheet(f"background-color: {BG_MAIN};")
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(14, 14, 14, 14)
        body_lay.setSpacing(14)
        body_lay.addWidget(self._make_grid_frame())
        body_lay.addWidget(self._make_panel())
        lay.addWidget(body)

    def _make_header(self):
        hdr = QWidget()
        hdr.setFixedHeight(62)
        hdr.setStyleSheet(f"background-color: {BG_HEADER};")
        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(22, 0, 22, 0)

        title = QLabel("🏙️  Cidade Colaborativa")
        title.setFont(QFont("Helvetica", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent;")
        lay.addWidget(title)
        lay.addStretch()

        self.badge = QLabel("👥  0 online")
        self.badge.setFont(QFont("Helvetica", 11, QFont.Weight.Bold))
        self.badge.setStyleSheet(
            f"color: {TEXT_LIGHT}; background-color: {ACCENT};"
            "padding: 6px 16px; border-radius: 5px;"
        )
        lay.addWidget(self.badge)
        return hdr

    def _make_grid_frame(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: #9DBD85; border-radius: 6px;")
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(4, 4, 4, 4)
        self.city_grid = CityGrid(self._on_left_click, self._on_right_click)
        lay.addWidget(self.city_grid)
        return frame

    def _section(self, layout, text):
            lbl = QLabel(text)
            lbl.setFont(QFont("Helvetica", 9, QFont.Weight.Bold))
            lbl.setStyleSheet(
                f"color: {TEXT_SEC}; background: transparent; padding: 12px 16px 4px 16px;"
            )
            layout.addWidget(lbl)

    def _line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {DIVIDER}; border: none;")
        return line
    
    # =========================================================
    # EVENTOS DO USUÁRIO
    # =========================================================

    def _on_left_click(self, row, col):
        cell = self.grid_state[row][col]
        if cell is not None:
            info = STRUCTURES.get(cell["type"], {})
            show_info(
                self, "Posição ocupada",
                f"{info.get('emoji', '')} {cell['type']}\n"
                f"Alocado por: {cell['author']} às {cell['time']}"
            )
            return
        self.last_action = {"op": "PLACE", "row": row, "col": col,
                            "structure": self.selected_struct}
        self.net.send(protocol.create_place(row, col, self.selected_struct, self.author))

    def _on_right_click(self, row, col):
        if self.grid_state[row][col] is None:
            return
        self.last_action = {"op": "REMOVE", "row": row, "col": col}
        self.net.send(protocol.create_remove(row, col))
