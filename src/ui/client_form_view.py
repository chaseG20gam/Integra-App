from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ClientFormView(QWidget):
    # form for entering or editing client details

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.occupation_input = QLineEdit(self)
        self.therapy_price_input = QDoubleSpinBox(self)
        self.sports_input = QLineEdit(self)
        self.sports_none_checkbox = QCheckBox("Ninguno", self)
        self.background_input = QTextEdit(self)
        self.observations_input = QTextEdit(self)

        self.save_button = QPushButton("Guardar", self)
        self.cancel_button = QPushButton("Cancelar", self)

        self._build_layout()

    def _build_layout(self) -> None:
        # layout
        form_layout = QFormLayout()
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        self.first_name_input.setPlaceholderText("Nombre")
        self.last_name_input.setPlaceholderText("Apellidos")
        self.phone_input.setPlaceholderText("Telefono")
        self.email_input.setPlaceholderText("Correo electronico")
        self.occupation_input.setPlaceholderText("Profesion")
        self.therapy_price_input.setPrefix("€")
        self.therapy_price_input.setMaximum(9999.99)
        self.therapy_price_input.setDecimals(2)
        self.therapy_price_input.setSpecialValueText("")
        self.therapy_price_input.setValue(0)
        self.sports_input.setPlaceholderText("Deporte")
        self._setup_sports_logic()
        self.background_input.setPlaceholderText("Antecedentes previos")
        self.observations_input.setPlaceholderText("Notas y observaciones")

        form_layout.addRow("Nombre", self.first_name_input)
        form_layout.addRow("Apellidos", self.last_name_input)
        form_layout.addRow("Telefono", self.phone_input)
        form_layout.addRow("Correo electronico", self.email_input)
        form_layout.addRow("Profesion", self.occupation_input)
        form_layout.addRow("Precio", self.therapy_price_input)
        
        # sports field with checkbox
        sports_container = QWidget()
        sports_layout = QVBoxLayout(sports_container)
        sports_layout.setContentsMargins(0, 0, 0, 0)
        sports_layout.setSpacing(4)
        sports_layout.addWidget(self.sports_none_checkbox)
        sports_layout.addWidget(self.sports_input)
        
        form_layout.addRow("Deporte", sports_container)
        form_layout.addRow("Antecedentes previos", self.background_input)
        form_layout.addRow("Notas y observaciones", self.observations_input)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch(1)

        form_layout.addRow(button_row)
        self.setLayout(form_layout)
        
        self._apply_styling()

    def _setup_sports_logic(self) -> None: 
        # when checkbox is checked, clear and disable text field
        self.sports_none_checkbox.toggled.connect(self._on_sports_none_toggled)
        # when text is entered, uncheck checkbox
        self.sports_input.textChanged.connect(self._on_sports_text_changed)

    def _on_sports_none_toggled(self, checked: bool) -> None:
        if checked:
            self.sports_input.clear()
            self.sports_input.setEnabled(False)
        else:
            self.sports_input.setEnabled(True)

    def _on_sports_text_changed(self, text: str) -> None:
        if text.strip() and self.sports_none_checkbox.isChecked():
            self.sports_none_checkbox.setChecked(False)
    
    def _apply_styling(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: #E2E8F0;
            }
            QLabel {
                color: #E2E8F0;
                font-weight: bold;
            }
            QLineEdit, QDoubleSpinBox, QTextEdit {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #E2E8F0;
                font-size: 13px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #3B82F6;
            }
            QPushButton {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 10px 16px;
                color: #E2E8F0;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:pressed {
                background-color: #1E293B;
            }
            QCheckBox {
                color: #E2E8F0;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #475569;
                border-radius: 3px;
                background-color: #1E293B;
            }
            QCheckBox::indicator:checked {
                background-color: #3B82F6;
                border-color: #3B82F6;
            }
        """)
