
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.client_form_dialog import ClientFormDialog


class ClientDetailsDialog(QDialog):
    # dialog for displaying detailed client information

    def __init__(self, parent=None, client_data=None, controller=None) -> None:
        super().__init__(parent)
        self.client_data = client_data
        self.controller = controller
        self.setWindowTitle(f"Detalles del Cliente - {client_data.first_name} {client_data.last_name}")
        self.setModal(True)
        self.resize(500, 600)

        self.edit_button = QPushButton("Editar Cliente", self)
        self.delete_button = QPushButton("Eliminar Cliente", self)
        self.close_button = QPushButton("Cerrar", self)
        
        # style delete button to make VERY red
        self.delete_button.setStyleSheet("QPushButton { background-color: #E74C3C; color: white; font-weight: bold; }")

        self._build_layout()
        self._connect_signals()

    def _build_layout(self) -> None:
        # build the details layout
        main_layout = QVBoxLayout(self)

        # scroll area for client details
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        details_widget = QWidget()
        form_layout = QFormLayout(details_widget)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(16, 16, 16, 16)

        # client information fields
        self._add_field(form_layout, "Nombre:", self.client_data.first_name or "")
        self._add_field(form_layout, "Apellidos:", self.client_data.last_name or "")
        self._add_field(form_layout, "Teléfono:", self.client_data.phone or "No proporcionado")
        self._add_field(form_layout, "Correo electrónico:", self.client_data.email or "No proporcionado")
        self._add_field(form_layout, "Profesión:", self.client_data.occupation or "No especificado")
        
        price_text = f"${self.client_data.therapy_price:.2f}" if self.client_data.therapy_price else "No establecido"
        self._add_field(form_layout, "Precio de terapia:", price_text)
        
        self._add_field(form_layout, "Deportes:", self.client_data.sports or "Ninguno")
        self._add_field(form_layout, "Antecedentes:", self.client_data.background or "No proporcionado", multiline=True)
        self._add_field(form_layout, "Observaciones:", self.client_data.observations or "No hay observaciones", multiline=True)

        scroll_area.setWidget(details_widget)
        main_layout.addWidget(scroll_area)

        # buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def _add_field(self, form_layout: QFormLayout, label: str, value: str, multiline: bool = False) -> None:
        # add a field to the form layout
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-weight: bold; color: #2C3E50;")

        value_widget = QLabel(value if value.strip() else "(No especificado)")
        if multiline:
            value_widget.setWordWrap(True)
            value_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
            value_widget.setMinimumHeight(80)
            value_widget.setStyleSheet("QLabel { background-color: #F8F9FA; padding: 8px; border: 1px solid #DEE2E6; border-radius: 4px; color: #495057; }")
        else:
            value_widget.setStyleSheet("color: #495057;")

        form_layout.addRow(label_widget, value_widget)

    def _connect_signals(self) -> None:
        # connect button signals
        self.edit_button.clicked.connect(self._open_edit_dialog)
        self.delete_button.clicked.connect(self._confirm_delete_client)
        self.close_button.clicked.connect(self.accept)

    def _open_edit_dialog(self) -> None:
        # open the edit dialog for this client
        edit_dialog = ClientFormDialog(self, self.client_data)
        if edit_dialog.exec() == edit_dialog.DialogCode.Accepted:
            if edit_dialog.is_valid():
                # get updated data from form
                updated_data = edit_dialog.get_form_data()
                
                # update client through controller
                if self.controller:
                    print(f"Calling controller.update_client for ID: {self.client_data.id}")
                    self.controller.update_client(
                        self.client_data.id,
                        updated_data["first_name"],
                        updated_data["last_name"],
                        updated_data["phone"],
                        updated_data["email"],
                        updated_data["occupation"],
                        updated_data["therapy_price"],
                        updated_data["sports"],
                        updated_data["background"],
                        updated_data["observations"]
                    )
                    print("Update completed, closing dialog")
                else:
                    print("No controller available")
                        
                self.accept()  # close details dialog after edit

    def _confirm_delete_client(self) -> None:
        """Show confirmation dialog before deleting client."""
        client_name = f"{self.client_data.first_name} {self.client_data.last_name}"
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Seguro que quieres eliminar permanentemente a '{client_name}'?\n\nEsta acción es definitiva y no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.controller:
                print(f"Deleting client ID: {self.client_data.id}")
                self.controller.delete_client(self.client_data.id)
                QMessageBox.information(self, "Eliminado", f"Cliente '{client_name}' eliminado con éxito.")
                self.accept()  # Close dialog after successful deletion
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el cliente: controlador no disponible.")