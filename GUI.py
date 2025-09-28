# fixed_chat_ui.py
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QFrame
)
from PyQt5.QtGui import (
    QIcon, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
)
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
from pathlib import Path

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Directory paths
current_dir = Path.cwd()
TempDirPath = current_dir / "Frontend" / "Files"
GraphicsDirPath = current_dir / "Frontend" / "Graphics"

# Ensure temp directory exists
TempDirPath.mkdir(parents=True, exist_ok=True)

# ---------------- Helper functions ----------------
def graphics_path(filename: str) -> str:
    p = GraphicsDirPath / filename
    return str(p) if p.exists() else ""

def temp_path(filename: str) -> str:
    return str(TempDirPath / filename)

def safe_read(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def safe_write(file_path: str, text: str) -> None:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass

def AnswerModifier(answer: str) -> str:
    lines = answer.splitlines()
    non_empty = [ln for ln in lines if ln.strip()]
    return "\n".join(non_empty)

def QueryModifier(query: str) -> str:
    if not query:
        return ""
    new_query = query.strip()
    question_words = {
        "how", "what", "who", "where", "when", "why", "which",
        "whose", "whom", "can you", "what's", "where's", "how's"
    }
    lower = new_query.lower()
    if any(lower.startswith(w) for w in question_words) or lower.endswith("?"):
        if not new_query.endswith("?"):
            new_query = new_query.rstrip(".!?") + "?"
    else:
        if not new_query.endswith("."):
            new_query = new_query.rstrip(".!?") + "."
    return new_query[0].upper() + new_query[1:] if new_query else new_query

def SetMicrophoneStatus(command: str):
    safe_write(temp_path("Mic.data"), command)

def GetMicrophoneStatus() -> str:
    return safe_read(temp_path("Mic.data"))

def SetAssistantStatus(status: str):
    safe_write(temp_path("Status.data"), status)

def GetAssistantStatus() -> str:
    return safe_read(temp_path("Status.data"))

def ShowTextToScreen(text: str):
    safe_write(temp_path("Responses.data"), text)

# Initialize files if missing
if not Path(temp_path("Mic.data")).exists():
    SetMicrophoneStatus("False")
if not Path(temp_path("Status.data")).exists():
    SetAssistantStatus("Idle")
if not Path(temp_path("Responses.data")).exists():
    ShowTextToScreen("")

# ---------------- UI Classes ----------------
class ChatSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setStyleSheet("background-color: black; color: white;")
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.gif_label = QLabel()
        gif_file = graphics_path("javis.gif.gif")
        if gif_file:
            movie = QMovie(gif_file)
            movie.setScaledSize(QSize(300, 300))
            self.gif_label.setMovie(movie)
            movie.start()
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        layout.addWidget(self.chat_text_edit)
        layout.addWidget(self.gif_label, alignment=Qt.AlignRight)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.start(500)

        self._last_messages = ""

    def loadMessages(self):
        content = safe_read(temp_path("Responses.data"))
        if content and content != self._last_messages:
            modified = AnswerModifier(content)
            self.chat_text_edit.clear()
            cursor = self.chat_text_edit.textCursor()
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("cyan"))
            block_fmt = QTextBlockFormat()
            block_fmt.setTopMargin(6)
            for line in modified.splitlines():
                cursor.setBlockFormat(block_fmt)
                cursor.setCharFormat(fmt)
                cursor.insertText(line + "\n")
            self.chat_text_edit.setTextCursor(cursor)
            self._last_messages = content

# ---------- Home screen with mic toggle ----------
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.gif_label = QLabel()
        gif_file = graphics_path("javis.gif.gif")
        if gif_file:
            movie = QMovie(gif_file)
            movie.setScaledSize(QSize(500, 500))
            self.gif_label.setMovie(movie)
            movie.start()

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white; font-size:16px;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Mic toggle
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: none;")
        self.icon_label.mousePressEvent = self.toggle_icon

        self.toggled = (GetMicrophoneStatus().lower() == "true")
        self.update_mic_icon()

        content_layout.addStretch(1)
        content_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.addStretch(2)

        self.setLayout(content_layout)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(500)

    def refresh_ui(self):
        self.status_label.setText(GetAssistantStatus())
        current_state = (GetMicrophoneStatus().lower() == "true")
        if current_state != self.toggled:
            self.toggled = current_state
            self.update_mic_icon()

    def update_mic_icon(self):
        mic_file = graphics_path("mic.png.png") if self.toggled else graphics_path("mute.png.png")
        if mic_file:
            pixmap = QPixmap(mic_file).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        self.toggled = not self.toggled
        SetMicrophoneStatus("True" if self.toggled else "False")
        self.update_mic_icon()

# ---------- Chat screen (no mic here) ----------
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white; font-size:16px;")
        self.status_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        self.chat_section = ChatSection()
        layout.addWidget(self.chat_section)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

    def update_status(self):
        self.status_label.setText(GetAssistantStatus())

# ---------- Top bar ----------
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget: QStackedWidget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()
        self.offset = None

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        title_label = QLabel(f" {Assistantname.capitalize()} AI")
        title_label.setStyleSheet("color: white; font-size: 18px; background-color: black; padding: 6px;")

        home_button = QPushButton(" Home")
        home_button.setIcon(QIcon(graphics_path("home.png.png")))
        home_button.setStyleSheet("background-color: black; color: white;")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        message_button = QPushButton(" Chat")
        message_button.setIcon(QIcon(graphics_path("chat.png.png")))
        message_button.setStyleSheet("background-color: black; color: white;")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(graphics_path("minimize 1.png.png")))
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(graphics_path("maximize 2.png.png"))
        self.restore_icon = QIcon(graphics_path("restore.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_button.setIcon(QIcon(graphics_path("close.png.png")))
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.setStyleSheet("background-color: white;")

    def minimizeWindow(self):
        if self.parent():
            self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent():
            if self.parent().isMaximized():
                self.parent().showNormal()
                self.maximize_button.setIcon(self.maximize_icon)
            else:
                self.parent().showMaximized()
                self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        if self.parent():
            self.parent().close()

    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset and self.parent():
            self.parent().move(event.globalPos() - self.offset)

# ---------- Main window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

        self.resize(1000, 700)
        self.setStyleSheet("background-color: black;")

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
