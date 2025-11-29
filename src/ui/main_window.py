from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget

from ui.client_list_view import ClientListView
from ui.client_form_dialog import ClientFormDialog
from controllers.client_controller import ClientController


class MainWindow(QMainWindow):
    # primary window

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("TITLR PLACEHOLDER")
        self.resize(960, 600)

        self._client_list_view = ClientListView(self)
        self._client_list_view.setObjectName("clientListView")

        self._client_controller = ClientController(self)
        self._connect_controller_signals()
        self._connect_ui_signals()

        self._central_container = QWidget(self)
        self._central_container.setObjectName("centralContainer")
        self._central_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        central_layout = QVBoxLayout(self._central_container)
        central_layout.setContentsMargins(24, 24, 24, 24)
        central_layout.addWidget(self._client_list_view)

        self.setCentralWidget(self._central_container)

        self._apply_styling()
        self._load_initial_data()

    def _apply_styling(self) -> None:
        # styling for the looks
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0F172A;
            }
            QWidget#centralContainer {
                background-color: #1E293B;
                border: 1px solid #334155;
            }
            QWidget#clientListView {
                background-color: #334155;
                border-radius: 12px;
                border: 1px solid #475569;
            }
            """
        )
        self.setMinimumSize(800, 500)
        self.setWindowState(Qt.WindowState.WindowActive)

    def _connect_controller_signals(self) -> None:
        # connect controller signals to UI updates
        self._client_controller.clients_loaded.connect(self._on_clients_loaded)
        self._client_controller.client_added.connect(self._on_client_added)
        self._client_controller.client_updated.connect(self._on_client_updated)
        self._client_controller.client_deleted.connect(self._on_client_deleted)
        self._client_controller.error_ocurred.connect(self._on_error)

    def _connect_ui_signals(self) -> None:
        # connect UI button signals
        self._client_list_view.add_button.clicked.connect(self._show_add_client_dialog)

    def _load_initial_data(self) -> None:
        # load clients from database on startup
        self._client_controller.load_all_clients()

    def _on_clients_loaded(self, clients) -> None:
        # handle loaded clients from controller
        self._client_list_view.clear_placeholder()
        # populate with real client data
        for client in clients:
            self._client_list_view.add_client_to_list(f"{client.first_name} {client.last_name}", client)

    def _on_client_added(self, client) -> None:
        # handle new client added
        self._client_list_view.add_client_to_list(f"{client.first_name} {client.last_name}", client)

    def _on_client_updated(self, client) -> None:
        # handle client updated - refresh the entire list
        self._load_initial_data()
    
    def _on_client_deleted(self, client_id: int) -> None:
        # handle client deleted - show pulse animation to encourage manual refresh
        # note: auto-refresh disabled to show user-friendly pulse animation
        self._client_list_view.highlight_refresh_needed()

    def _on_error(self, error_message: str) -> None:
        # handle controller errors
        QMessageBox.critical(self, "Error", error_message)

    def _show_add_client_dialog(self) -> None:
        # show the add client form dialog
        dialog = ClientFormDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            if dialog.is_valid():
                data = dialog.get_form_data()
                self._client_controller.add_client(
                    data["first_name"],
                    data["last_name"],
                    data["phone"],
                    data["email"],
                    data["occupation"],
                    data["therapy_price"],
                    data["sports"],
                    data["background"],
                    data["observations"]
                )
            else:
                QMessageBox.warning(self, "Datos invalidos", "Nombre y apellidos es un campo obligatorio")

    @property
    def client_list_view(self) -> ClientListView:
        # expose the client list view for controller wiring
        return self._client_list_view
