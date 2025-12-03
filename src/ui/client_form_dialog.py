from __future__ import annotations

from PyQt6.QtWidgets import QDialog

from ui.client_form_view import ClientFormView



class ClientFormDialog(QDialog):
    # dialog wrapper for the client form

    def __init__(self, parent=None, client_data=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Añadir cliente" if client_data is None else "Editar Cliente")
        self.setModal(True)
        self.resize(400, 500)

        self.form_view = ClientFormView(self)
        
        # if editing, populate fields
        if client_data:
            self._populate_form(client_data)

        self._setup_dialog()

    def _setup_dialog(self) -> None:
        
        # setup dialog layout and connections
        # the form view already has its own layout
        self.form_view.save_button.clicked.connect(self.accept)
        self.form_view.cancel_button.clicked.connect(self.reject)
        
        # set the form as the dialogs main widget
        self.setLayout(self.form_view.layout())        
        # apply theming
        self._apply_styling()
    
    def _apply_styling(self) -> None:
        # apply professional theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
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
    


    def _populate_form(self, client_data) -> None:
        # populate form fields with existing client data
        # handle both object attributes and dictionary keys
        def get_value(data, key):
            if isinstance(data, dict):
                return data.get(key)
            else:
                return getattr(data, key, None)
        
        self.form_view.first_name_input.setText(get_value(client_data, 'first_name') or "")
        self.form_view.last_name_input.setText(get_value(client_data, 'last_name') or "")
        self.form_view.phone_input.setText(get_value(client_data, 'phone') or "")
        self.form_view.email_input.setText(get_value(client_data, 'email') or "")
        self.form_view.occupation_input.setText(get_value(client_data, 'occupation') or "")
        
        therapy_price = get_value(client_data, 'therapy_price')
        self.form_view.therapy_price_input.setValue(float(therapy_price or 0))
        
        # handle sports field and checkbox
        sports = get_value(client_data, 'sports')
        if sports:
            self.form_view.sports_input.setText(sports)
            self.form_view.sports_none_checkbox.setChecked(False)
        else:
            self.form_view.sports_input.setText("")
            self.form_view.sports_none_checkbox.setChecked(True)
            
        self.form_view.background_input.setPlainText(get_value(client_data, 'background') or "")
        self.form_view.observations_input.setPlainText(get_value(client_data, 'observations') or "")

    def get_form_data(self) -> dict:
        # extract form data as a dictionary
        # handle sports field: if checkbox is checked, sports should be None
        sports_value = None
        if hasattr(self.form_view, 'sports_none_checkbox') and self.form_view.sports_none_checkbox.isChecked():
            sports_value = None
        else:
            sports_value = self.form_view.sports_input.text().strip() or None
            
        return {
            "first_name": self.form_view.first_name_input.text().strip(),
            "last_name": self.form_view.last_name_input.text().strip(),
            "phone": self.form_view.phone_input.text().strip() or None,
            "email": self.form_view.email_input.text().strip() or None,
            "occupation": self.form_view.occupation_input.text().strip() or None,
            "therapy_price": self.form_view.therapy_price_input.value() if self.form_view.therapy_price_input.value() > 0 else None,
            "sports": sports_value,
            "background": self.form_view.background_input.toPlainText().strip() or None,
            "observations": self.form_view.observations_input.toPlainText().strip() or None,
        }

    def is_valid(self) -> bool:
        # validate form data
        data = self.get_form_data()
        return bool(data["first_name"] and data["last_name"])