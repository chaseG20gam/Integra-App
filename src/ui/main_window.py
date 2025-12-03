from __future__ import annotations

import os
import shutil
from datetime import datetime
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, pyqtProperty
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout
from PyQt6.QtGui import QAction, QDesktopServices, QIcon
from PyQt6.QtCore import QUrl

from ui.client_list_view import ClientListView
from ui.client_form_dialog import ClientFormDialog
from ui.about_dialog import AboutDialog
from ui.simple_update_dialog import SimpleUpdateDialog
from controllers.client_controller import ClientController
from utils.simple_updater import SimpleUpdateManager
from utils.version import CURRENT_VERSION


class MainWindow(QMainWindow):
    # primary window

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Integra Client Manager")
        self.resize(960, 600)
        
        # set window icon
        self._set_window_icon()

        self._client_list_view = ClientListView(self)
        self._client_list_view.setObjectName("clientListView")

        self._client_controller = ClientController(self)
        
        # initialize update system
        self.update_manager = SimpleUpdateManager(self)
        self.update_button = None
        self._glow_opacity = 1.0
        self._pulse_animation = None
        self.current_update_info = None
        
        self._setup_menu_bar()
        self._setup_update_system()
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
        
        # help menu
        help_menu = menubar.addMenu('&Ayuda')
        
        # check for updates action
        update_check_action = QAction('&Buscar Actualizaciones', self)
        update_check_action.setStatusTip('Comprobar si hay actualizaciones disponibles')
        update_check_action.triggered.connect(self._manual_update_check)
        help_menu.addAction(update_check_action)
        
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
    



    
    def _show_about_dialog(self) -> None:
        # show the About dialog created with Qt Designer
        about_dialog = AboutDialog(self)
        about_dialog.exec()
    
    def _set_window_icon(self) -> None:
        # set the application window icon
        import os
        import sys
        
        # get the correct resource path for both development and bundled executable
        if getattr(sys, 'frozen', False):
            # running as bundled executable
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, 'assets', 'app_icon.ico')
        else:
            # running as script in development
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'app_icon.ico')
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def _setup_update_system(self) -> None:
        # connect update manager signals
        self.update_manager.update_available.connect(self._on_update_available)
        self.update_manager.no_update_available.connect(self._on_no_update_available)
        self.update_manager.update_check_failed.connect(self._on_update_check_failed)
        
        # create update notification button (initially hidden)
        self._create_update_button()
    
    def _create_update_button(self) -> None:
        # create the glowing update notification button
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtCore import QSize
        
        self.update_button = QPushButton("Update")
        self.update_button.setObjectName("updateButton")
        self.update_button.setMaximumSize(QSize(100, 28))
        self.update_button.setVisible(False)
        self.update_button.clicked.connect(self._show_update_dialog)
        
        # add to menu bar
        menubar = self.menuBar()
        menubar.setCornerWidget(self.update_button, Qt.Corner.TopRightCorner)
    
    @pyqtProperty(float)
    def glow_opacity(self) -> float:
        return self._glow_opacity
    
    @glow_opacity.setter
    def glow_opacity(self, value: float) -> None:
        self._glow_opacity = value
        self._update_button_glow()
    
    def _update_button_glow(self) -> None:
        if not self.update_button or not self.update_button.isVisible():
            return
        
        # create faint yellow glowing effect with opacity
        glow_opacity = max(0.3, self._glow_opacity * 0.6)  # keep it faint
        glow_color = f"rgba(245, 158, 11, {glow_opacity})"  # yellow 
        
        self.update_button.setStyleSheet(f"""
            QPushButton#updateButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F59E0B, stop:1 #D97706);
                border: 1px solid {glow_color};
                border-radius: 6px;
                padding: 4px 10px;
                color: #1F2937;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton#updateButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #D97706, stop:1 #B45309);
            }}
            QPushButton#updateButton:pressed {{
                background: #B45309;
            }}
        """)
    
    def _start_glow_animation(self) -> None:
        if self._pulse_animation:
            self._pulse_animation.stop()
        
        # create pulsing glow animation
        self._pulse_animation = QPropertyAnimation(self, b"glow_opacity")
        self._pulse_animation.setDuration(1500)  # 1.5 second pulse
        self._pulse_animation.setStartValue(0.3)
        self._pulse_animation.setEndValue(1.0)
        self._pulse_animation.setLoopCount(-1)  # infinite loop
        
        # start animation
        self._pulse_animation.start()
    
    def _stop_glow_animation(self) -> None:
        # stop the glowing animation
        if self._pulse_animation:
            self._pulse_animation.stop()
            self._pulse_animation = None
        self._glow_opacity = 1.0
        self._update_button_glow()
    
    def _on_update_available(self, update_info) -> None:
        # update handler
        # show the update button with faint yellow glowing effect
        self.update_button.setVisible(True)
        self._start_glow_animation()
        
        # store update info for dialog
        self.current_update_info = update_info
        
        # show a subtle notification
        self.statusBar().showMessage(f"Update available: v{update_info.version}", 3000)
    
    def _on_no_update_available(self) -> None:
        self.statusBar().showMessage("No updates available - you're on the latest version!", 3000)
    
    def _on_update_check_failed(self, error: str) -> None:
        # handle when update check fails
        # show error for manual checks
        self.statusBar().showMessage(f"Update check failed: {error}", 5000)
    
    def _show_update_dialog(self) -> None:
        if hasattr(self, 'current_update_info') and self.current_update_info:
            # stop glowing animation when user interacts
            self._stop_glow_animation()
            
            dialog = SimpleUpdateDialog(self.current_update_info, self)
            result = dialog.exec()
            
            # hide update button after user interaction (regardless of choice)
            self.update_button.setVisible(False)
            self.current_update_info = None
    
    def _manual_update_check(self) -> None:
        self.update_manager.check_for_update()
        self.statusBar().showMessage("Checking for updates...", 3000)

    def _apply_styling(self) -> None:
        # apply theme styling
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

    def _show_edit_client_dialog(self, client_data: dict) -> None:
        # show the edit client form dialog
        dialog = ClientFormDialog(self, client_data)
        if dialog.exec() == dialog.DialogCode.Accepted:
            if dialog.is_valid():
                updated_data = dialog.get_form_data()
                self._client_controller.update_client(
                    client_data['id'],  # use the original ID
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
            else:
                QMessageBox.warning(self, "Datos invalidos", "Nombre y apellidos es un campo obligatorio")

    @property
    def client_list_view(self) -> ClientListView:
        # expose the client list view for controller wiring
        return self._client_list_view
