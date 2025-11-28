from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ClientListView(QWidget):
    # displays clients with search and action controls

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search clients...")

        self.client_list = QListWidget(self)
        self.client_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.add_button = QPushButton("Add Client", self)
        self.edit_button = QPushButton("Edit", self)
        self.delete_button = QPushButton("Delete", self)

        self._build_layout()
        self._populate_placeholder()

    def _build_layout(self) -> None:
        #c ompose the layout for the list view
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Clients", self))
        layout.addWidget(self.search_input)
        layout.addWidget(self.client_list, stretch=1)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.delete_button)
        button_row.addStretch(1)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def _populate_placeholder(self) -> None:
        # data tests
        placeholder_clients = [
            "Ana Smith",
            "Brad Johnson",
            "Carla Gómez",
        ]
        for name in placeholder_clients:
            item = QListWidgetItem(name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.client_list.addItem(item)

    def clear_placeholder(self) -> None:
        # remove the data placeholderfs when real data is added
        self.client_list.clear()
