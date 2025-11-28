from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)


class ClientFormView(QWidget):
    # form for entering or editing client details

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)
        self.notes_input = QTextEdit(self)

        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)

        self._build_layout()

    def _build_layout(self) -> None:
        # layout
        form_layout = QFormLayout()
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        self.first_name_input.setPlaceholderText("First name")
        self.last_name_input.setPlaceholderText("Last name")
        self.email_input.setPlaceholderText("Email")
        self.phone_input.setPlaceholderText("Phone")
        self.notes_input.setPlaceholderText("Notes")

        form_layout.addRow("First Name", self.first_name_input)
        form_layout.addRow("Last Name", self.last_name_input)
        form_layout.addRow("Email", self.email_input)
        form_layout.addRow("Phone", self.phone_input)
        form_layout.addRow("Notes", self.notes_input)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch(1)

        form_layout.addRow(button_row)
        self.setLayout(form_layout)
