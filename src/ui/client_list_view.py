from __future__ import annotations

from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, pyqtProperty
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
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
        self.search_input.setPlaceholderText("Buscar clientes...") 

        self.client_list = QListWidget(self)
        self.client_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.client_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # make text bigger with white line separators
        self.client_list.setStyleSheet("""
            QListWidget {
                font-size: 20px;
            }
            QListWidget::item {
                border-bottom: 1px solid white;
                padding: 6px;
            }
        """)
        
        # store client data for access when showing details
        self.client_data_map = {}

        self.add_button = QPushButton("Añadir cliente", self)
        self.edit_button = QPushButton("Editar", self)
        self.delete_button = QPushButton("Eliminar", self)
        # create refresh button with SVG icon
        import os
        import sys
        
        # get the correct resource path for both development and bundled executable
        if getattr(sys, 'frozen', False):
            # running as bundled executable
            base_path = sys._MEIPASS
            refresh_icon_path = os.path.join(base_path, 'utils', 'refresh-svgrepo-com.svg')
        else:
            # running as script in development
            refresh_icon_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'refresh-svgrepo-com.svg')
        
        self.refresh_button = QPushButton(self)
        self.refresh_button.setIcon(QIcon(refresh_icon_path))
        self.refresh_button.setToolTip("Actualizar lista de clientes")
        self.refresh_button.setMaximumWidth(40)
        self.refresh_button.setMaximumHeight(40)
        
        # aimation setup for refresh button glow
        self._pulse_animation = None
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._stop_pulse_animation)
        self._glow_opacity = 1.0

        self._build_layout()
        self._populate_placeholder()
        self._connect_signals()

    def _build_layout(self) -> None:
        #c ompose the layout for the list view
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # header with title and refresh button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Clientes", self))
        header_layout.addStretch(1)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
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
        
        self._apply_styling()

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
        self.edit_button.clicked.connect(self._edit_selected_client)
        self.delete_button.clicked.connect(self._confirm_delete)
        self.refresh_button.clicked.connect(self._on_refresh_clicked)
        self.client_list.itemDoubleClicked.connect(self._on_client_double_clicked)
        self.client_list.customContextMenuRequested.connect(self._show_context_menu)
        # connect search input
        self.search_input.textChanged.connect(self._on_search_changed)

    def _confirm_delete(self) -> None:
        # show confirmation dialog before deleting selected client
        current_item = self.client_list.currentItem()
        if not current_item:
            msg = QMessageBox(self)
            msg.setWindowTitle("Nada seleccionado")
            msg.setText("Por favor, selecciona un cliente para eliminar")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet(self._get_message_box_style())
            msg.exec()
            return

        client_name = current_item.text()
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar eliminacion")
        msg.setText(f"Seguro que quieres eliminar a '{client_name}'?\n\nEsta accion es definitiva y no se puede deshacer")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        
        msg.setStyleSheet(self._get_message_box_style())
        
        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            # get controller from main window and delete through it
            main_window = self.window()
            controller = getattr(main_window, '_client_controller', None)
            if controller and client_name in self.client_data_map:
                client_data = self.client_data_map[client_name]
                controller.delete_client(client_data.id)
                msg = QMessageBox(self)
                msg.setWindowTitle("Eliminado")
                msg.setText(f"Cliente '{client_name}' eliminado con exito.")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setStyleSheet(self._get_message_box_style())
                msg.exec()
            else:
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText("No se pudo eliminar el cliente: controlador no disponible.")
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setStyleSheet(self._get_message_box_style())
                msg.exec()

    def _edit_selected_client(self) -> None:
        # edit the selected client
        current_item = self.client_list.currentItem()
        if not current_item:
            msg = QMessageBox(self)
            msg.setWindowTitle("Nada seleccionado")
            msg.setText("Por favor, selecciona un cliente para editar")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet(self._get_message_box_style())
            msg.exec()
            return

        client_name = current_item.text()
        if client_name in self.client_data_map:
            client_data = self.client_data_map[client_name]
            # create client data dictionary for the form dialog
            client_form_data = {
                'id': client_data.id,
                'first_name': client_data.first_name,
                'last_name': client_data.last_name,
                'phone': client_data.phone,
                'email': client_data.email,
                'occupation': client_data.occupation,
                'therapy_price': client_data.therapy_price,
                'sports': client_data.sports,
                'background': client_data.background,
                'observations': client_data.observations
            }
            
            # get main window and call edit method directly
            main_window = self.window()
            if hasattr(main_window, '_show_edit_client_dialog'):
                main_window._show_edit_client_dialog(client_form_data)
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("No se pudo encontrar los datos del cliente.")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setStyleSheet(self._get_message_box_style())
            msg.exec()

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
    
    def _refresh_list(self) -> None:
        # refresh the client list by reloading from database
        main_window = self.window()
        controller = getattr(main_window, '_client_controller', None)
        if controller:
            controller.load_all_clients()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("No se pudo actualizar la lista: controlador no disponible.")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet(self._get_message_box_style())
            msg.exec()
    
    def _on_refresh_clicked(self) -> None:
        # handle refresh button click and stop animation
        self._stop_pulse_animation()
        self._refresh_list()
    
    @pyqtProperty(float)
    def glow_opacity(self) -> float:
        return self._glow_opacity
    
    @glow_opacity.setter
    def glow_opacity(self, value: float) -> None:
        self._glow_opacity = value
        self._update_refresh_button_style()
    
    def _update_refresh_button_style(self) -> None:
        # update refresh button style with current glow opacity
        if self._glow_opacity > 0.0 and self._pulse_animation and self._pulse_animation.state() == QPropertyAnimation.State.Running:
            # pulsing state - orange background
            orange_intensity = int(255 * self._glow_opacity)
            background_color = f"rgb({orange_intensity}, {int(orange_intensity * 0.7)}, 0)"
            
            self.refresh_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {background_color};
                    border: 1px solid #475569;
                    border-radius: 6px;
                    padding: 8px;
                    color: #FFFFFF;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {background_color};
                }}
            """)
        else:
            # normal state - default styling
            self.refresh_button.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    border: 1px solid #475569;
                    border-radius: 6px;
                    padding: 8px;
                    color: #E2E8F0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #475569;
                }
                QPushButton:pressed {
                    background-color: #1E293B;
                }
            """)
    
    def start_pulse_animation(self) -> None:
        # start pulsing animation on refresh button
        if self._pulse_animation:
            self._pulse_animation.stop()
        
        # create pulsing animation
        self._pulse_animation = QPropertyAnimation(self, b"glow_opacity")
        self._pulse_animation.setDuration(800)  # faster pulse cycle
        self._pulse_animation.setStartValue(0.4)
        self._pulse_animation.setEndValue(1.0)
        self._pulse_animation.setLoopCount(-1)  # infinite loop
        
        # start animation
        self._pulse_animation.start()
        
        # let it glow until clicked
    
    def _stop_pulse_animation(self) -> None:
        # stop pulsing animation and return to normal state
        if self._pulse_animation:
            self._pulse_animation.stop()
            self._pulse_animation = None
        self._pulse_timer.stop()
        
        # reset to normal style completely
        self._glow_opacity = 0.0
        self._update_refresh_button_style()
    
    def highlight_refresh_needed(self) -> None:
        # public method to trigger pulse animation (called after deletion)
        self.start_pulse_animation()
    
    def _get_message_box_style(self) -> str:
        # return consistent dark theme styling for message boxes
        return """
            QMessageBox {
                background-color: #0F172A;
                color: #E2E8F0;
            }
            QMessageBox QLabel {
                color: #E2E8F0;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 10px 16px;
                color: #E2E8F0;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #475569;
            }
            QMessageBox QPushButton:pressed {
                background-color: #1E293B;
            }
        """
    
    def _apply_styling(self) -> None:
        # apply theme styling
        self.setStyleSheet("""
            QWidget {
                color: #E2E8F0;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #E2E8F0;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QListWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #E2E8F0;
                alternate-background-color: #334155;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #334155;
            }
            QListWidget::item:selected {
                background-color: #475569;
            }
            QListWidget::item:hover {
                background-color: #334155;
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
        """)

    def _on_search_changed(self, text: str) -> None:
        # handle search input changes
        # get controller from main window
        main_window = self.window()
        controller = getattr(main_window, '_client_controller', None)
        
        if controller:
            if text.strip():
                # search with the entered text
                controller.search_clients(text.strip())
            else:
                # if search is empty, load all clients
                controller.load_all_clients()
        else:
            print("Error de busqueda o controlador")
