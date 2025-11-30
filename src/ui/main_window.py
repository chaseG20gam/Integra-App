from __future__ import annotations

import os
import shutil
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QAction, QDesktopServices
from PyQt6.QtCore import QUrl

from ui.client_list_view import ClientListView
from ui.client_form_dialog import ClientFormDialog
from ui.about_dialog import AboutDialog
from controllers.client_controller import ClientController


class MainWindow(QMainWindow):
    # primary window

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Integra Client Manager")
        self.resize(960, 600)

        self._client_list_view = ClientListView(self)
        self._client_list_view.setObjectName("clientListView")

        self._client_controller = ClientController(self)
        self._is_dark_theme = True  # start with dark theme
        self._setup_menu_bar()
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

    def _setup_menu_bar(self) -> None:
        # menu bar
        menubar = self.menuBar()
        
        # tools menu
        tools_menu = menubar.addMenu('&Herramientas')
        
        # backup database action
        backup_action = QAction('&Copia de seguridad', self)
        backup_action.triggered.connect(self._backup_database)
        tools_menu.addAction(backup_action)
        
        # export clients action
        export_action = QAction('&Exportar clientes a CSV', self)
        export_action.triggered.connect(self._export_clients)
        tools_menu.addAction(export_action)
        
        tools_menu.addSeparator()
        
        # open data folder action
        data_folder_action = QAction('Abrir Carpeta de &Datos', self)
        data_folder_action.setStatusTip('Abrir la carpeta donde se guardan los datos')
        data_folder_action.triggered.connect(self._open_data_folder)
        tools_menu.addAction(data_folder_action)
        
        # view menu for theme options
        view_menu = menubar.addMenu('&Ver')
        
        # theme toggle action
        self.theme_action = QAction('Cambiar a Tema &Claro', self)
        self.theme_action.setStatusTip('Alternar entre tema oscuro y claro')
        self.theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(self.theme_action)
        
        # help menu
        help_menu = menubar.addMenu('&Ayuda')
        
        # keyboard shortcuts action
        shortcuts_action = QAction('&Atajos de Teclado', self)
        shortcuts_action.setStatusTip('Ver lista de atajos de teclado disponibles')
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        # about action
        about_action = QAction('&Acerca de...', self)
        about_action.setStatusTip('Mostrar información sobre la aplicación')
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _backup_database(self) -> None:
        
        # create a backup of the database file
        try:
            # get the database file path
            from models.database import DEFAULT_DB_PATH
            
            if not os.path.exists(DEFAULT_DB_PATH):
                QMessageBox.warning(self, "Error", "No se encontró la base de datos para respaldar.")
                return
            
            # create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"database_backup_{timestamp}.db"
            
            # choose backup location
            backup_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar copia de seguridad",
                backup_name,
                "Base de datos (*.db);;Todos los archivos (*)"
            )
            
            if backup_path:
                shutil.copy2(DEFAULT_DB_PATH, backup_path)
                QMessageBox.information(
                    self, 
                    "Copia de seguridad completada", 
                    f"Base de datos respaldada exitosamente en:\n{backup_path}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error de copia de seguridad", f"Error al crear copia de seguridad:\n{str(e)}")
    
    def _export_clients(self) -> None:
        # export clients to CSV file
        try:
            # get export file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_name = f"clientes_export_{timestamp}.csv"
            
            export_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar clientes",
                export_name,
                "CSV files (*.csv);;Todos los archivos (*)"
            )
            
            if export_path:
                # get all clients from database
                from models.database import session_scope
                from models.client import Client
                
                with session_scope() as session:
                    clients = session.query(Client).all()
                    
                    if not clients:
                        QMessageBox.information(self, "Sin Datos", "No hay clientes para exportar.")
                        return
                    
                    # write to CSV
                    import csv
                    with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        
                        # write header
                        writer.writerow([
                            'ID', 'Nombre', 'Apellidos', 'Teléfono', 'Email', 
                            'Profesión', 'Precio Terapia', 'Deportes', 'Antecedentes', 'Observaciones'
                        ])
                        
                        # write client data
                        for client in clients:
                            writer.writerow([
                                client.id,
                                client.first_name or '',
                                client.last_name or '',
                                client.phone or '',
                                client.email or '',
                                client.occupation or '',
                                client.therapy_price or '',
                                client.sports or '',
                                client.background or '',
                                client.observations or ''
                            ])
                    
                    QMessageBox.information(
                        self, 
                        "Exportación Completa", 
                        f"Se exportaron {len(clients)} clientes a:\n{export_path}"
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"Error al exportar clientes:\n{str(e)}")
    
    def _open_data_folder(self) -> None:
        # open the data folder in file explorer
        try:
            from models.database import DEFAULT_DB_PATH
            data_folder = os.path.dirname(DEFAULT_DB_PATH)
            
            # create folder if it doesnt exist
            os.makedirs(data_folder, exist_ok=True)
            
            # open in file explorer
            QDesktopServices.openUrl(QUrl.fromLocalFile(data_folder))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la carpeta de datos:\n{str(e)}")
    
    def _show_shortcuts(self) -> None:
        # show keyboard shortcuts dialog
        shortcuts_text = """
        <h3>Atajos de Teclado Disponibles:</h3>
        <table style="color: #E2E8F0;">
        <tr><td><b>Ctrl + N</b></td><td>Nuevo cliente</td></tr>
        <tr><td><b>Ctrl + F</b></td><td>Buscar cliente</td></tr>
        <tr><td><b>Ctrl + R</b></td><td>Actualizar lista</td></tr>
        <tr><td><b>Delete</b></td><td>Eliminar cliente seleccionado</td></tr>
        <tr><td><b>Enter</b></td><td>Ver detalles del cliente</td></tr>
        <tr><td><b>Ctrl + B</b></td><td>Respaldar base de datos</td></tr>
        <tr><td><b>Ctrl + E</b></td><td>Exportar clientes</td></tr>
        <tr><td><b>F1</b></td><td>Mostrar esta ayuda</td></tr>
        </table>
        <br>
        <p><i>Tip: Haz doble clic en un cliente para ver sus detalles</i></p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Atajos de Teclado")
        msg.setText(shortcuts_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0F172A;
                color: #E2E8F0;
            }
            QMessageBox QLabel {
                color: #E2E8F0;
                font-size: 13px;
            }
        """)
        msg.exec()

    def _toggle_theme(self) -> None:
        # toggle between dark and light themes
        self._is_dark_theme = not self._is_dark_theme
        self._apply_styling()
        
        # update menu text
        if self._is_dark_theme:
            self.theme_action.setText('Cambiar a Tema &Claro')
        else:
            self.theme_action.setText('Cambiar a Tema &Oscuro')
    
    def _show_about_dialog(self) -> None:
        # show the About dialog created with Qt Designer
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def _apply_styling(self) -> None:
        # styling for the looks
        if self._is_dark_theme:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
        
        self.setMinimumSize(800, 500)
        self.setWindowState(Qt.WindowState.WindowActive)
    
    def _apply_dark_theme(self) -> None:
        # apply dark theme styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0F172A;
            }
            QMenuBar {
                background-color: #1E293B;
                color: #E2E8F0;
                border-bottom: 1px solid #334155;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #334155;
            }
            QMenu {
                background-color: #1E293B;
                color: #E2E8F0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #334155;
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
        # apply dark theme to client list view
        if hasattr(self._client_list_view, '_apply_dark_theme'):
            self._client_list_view._apply_dark_theme()
    
    def _apply_light_theme(self) -> None:
        # apply beautiful light theme styling
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F1F5F9, stop:1 #E2E8F0);
            }
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                color: #1E293B;
                border-bottom: 2px solid #CBD5E1;
                padding: 6px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 14px;
                border-radius: 6px;
                margin: 2px;
            }
            QMenuBar::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EFF6FF, stop:1 #DBEAFE);
                color: #1E40AF;
            }
            QMenu {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                color: #1E293B;
                border: 2px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 10px 18px;
                border-radius: 6px;
                margin: 1px;
            }
            QMenu::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EFF6FF, stop:1 #DBEAFE);
                color: #1E40AF;
            }
            QWidget#centralContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border: 2px solid #CBD5E1;
                border-radius: 8px;
            }
            QWidget#clientListView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8FAFC, stop:1 #F1F5F9);
                border-radius: 12px;
                border: 2px solid #94A3B8;
            }
            """
        )
        # apply light theme to client list view
        if hasattr(self._client_list_view, '_apply_light_theme'):
            self._client_list_view._apply_light_theme()

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
