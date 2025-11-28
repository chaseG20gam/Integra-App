from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
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
        self.client_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # store client data for access when showing details
        self.client_data_map = {}

        self.add_button = QPushButton("Añadir cliente", self)
        self.edit_button = QPushButton("Editar", self)
        self.delete_button = QPushButton("Eliminar", self)

        self._build_layout()
        self._populate_placeholder()
        self._connect_signals()

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
        self.client_data_map.clear()

    def add_client_to_list(self, client_name: str, client_data=None) -> None:
        # add a client to the list widget        
        item = QListWidgetItem(client_name)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.client_list.addItem(item)
        
        # store client data for details view
        if client_data:
            self.client_data_map[client_name] = client_data

    def _connect_signals(self) -> None:
        # connect button signals to their handlers
        self.delete_button.clicked.connect(self._confirm_delete)
        self.client_list.itemDoubleClicked.connect(self._on_client_double_clicked)
        self.client_list.customContextMenuRequested.connect(self._show_context_menu)

    def _confirm_delete(self) -> None:
        # show confirmation dialog before deleting selected client
        current_item = self.client_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Nada seleccionado", "Porfavor, selecciona un cliente para eliminar")
            return

        client_name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirmar eliminacion",
            f"Seguro que quieres eliminar a '{client_name}'?\n\nEsta accion es definitiva y no se puede deshacer",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # cnnect to controller to actually delete
            self.client_list.takeItem(self.client_list.row(current_item))
            # remove from data map
            if client_name in self.client_data_map:
                del self.client_data_map[client_name]
            QMessageBox.information(self, "Eliminado", f"Cliente '{client_name}' eliminado con exito.")

    def _on_client_double_clicked(self, item: QListWidgetItem) -> None:
        # handle double-click on client item
        self._show_client_details(item)

    def _show_context_menu(self, position) -> None:
        # show context menu for client list
        item = self.client_list.itemAt(position)
        if item:
            menu = QMenu(self)
            view_action = menu.addAction("Ver Cliente")
            view_action.triggered.connect(lambda: self._show_client_details(item))
            menu.exec(self.client_list.mapToGlobal(position))

    def _show_client_details(self, item: QListWidgetItem) -> None:
        # show client details dialog
        client_name = item.text()
        if client_name in self.client_data_map:
            from ui.client_details_dialog import ClientDetailsDialog
            client_data = self.client_data_map[client_name]
            # get controller from main window
            main_window = self.window()
            controller = getattr(main_window, '_client_controller', None)
            dialog = ClientDetailsDialog(self, client_data, controller)
            dialog.exec()
