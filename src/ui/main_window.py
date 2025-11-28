from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from .client_list_view import ClientListView


class MainWindow(QMainWindow):
    # primary window

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("TITLR PLACEHOLDER")
        self.resize(960, 600)

        self._client_list_view = ClientListView(self)
        self._client_list_view.setObjectName("clientListView")

        self._central_container = QWidget(self)
        self._central_container.setObjectName("centralContainer")
        self._central_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        central_layout = QVBoxLayout(self._central_container)
        central_layout.setContentsMargins(24, 24, 24, 24)
        central_layout.addWidget(self._client_list_view)

        self.setCentralWidget(self._central_container)

        self._apply_styling()

    def _apply_styling(self) -> None:
        # styling for the looks
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2C3E50;
            }
            QWidget#centralContainer {
                background-color: #34495E;
            }
            QWidget#clientListView {
                background-color: #ECF0F1;
                border-radius: 12px;
            }
            """
        )
        self.setMinimumSize(800, 500)
        self.setWindowState(Qt.WindowState.WindowActive)

    @property
    def client_list_view(self) -> ClientListView:
        # expose the client list view for controller wiring
        return self._client_list_view
