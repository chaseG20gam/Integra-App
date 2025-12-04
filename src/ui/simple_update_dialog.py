
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QMessageBox, QGroupBox
)

from utils.version import CURRENT_VERSION


class SimpleUpdateDialog(QDialog):
    
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.downloader = None
        self.setWindowTitle("Actualizacion disponible")
        self.setModal(True)
        self.resize(450, 350)
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        # set up the dialog ui
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # header
        header_label = QLabel("Actualizacion disponible!")
        header_label.setObjectName("headerLabel")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # version info
        version_text = f"Nueva version {self.update_info.version} disponible\n(Current: {CURRENT_VERSION})"
        version_label = QLabel(version_text)
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # release notes (if available)
        if self.update_info.release_notes:
            notes_group = QGroupBox("Novedades")
            notes_layout = QVBoxLayout(notes_group)
            
            self.notes_text = QTextEdit()
            self.notes_text.setPlainText(self.update_info.release_notes)
            self.notes_text.setReadOnly(True)
            self.notes_text.setMaximumHeight(120)
            notes_layout.addWidget(self.notes_text)
            
            layout.addWidget(notes_group)
        
        # progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # buttons
        button_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Si, actualizar")
        self.update_button.setObjectName("updateButton")
        self.update_button.clicked.connect(self._start_update)
        button_layout.addWidget(self.update_button)
        
        self.skip_button = QPushButton("No, Omitir version")
        self.skip_button.clicked.connect(self._skip_version)
        button_layout.addWidget(self.skip_button)
        
        layout.addLayout(button_layout)
    
    def _start_update(self):
        from utils.simple_updater import SimpleUpdateManager
        
        # get update manager from main window
        main_window = self.parent()
        if hasattr(main_window, 'update_manager'):
            self.downloader = main_window.update_manager.download_update(self.update_info)
            
            if self.downloader:
                # connect all signals
                self.downloader.download_progress.connect(self._on_download_progress)
                self.downloader.extraction_started.connect(self._on_extraction_started)
                self.downloader.installation_started.connect(self._on_installation_started)
                self.downloader.update_completed.connect(self._on_update_completed)
                self.downloader.download_failed.connect(self._on_download_failed)
                
                # update ui for download state
                self.update_button.setEnabled(False)
                self.update_button.setText("Actualizando...")
                self.skip_button.setEnabled(False)
                self.progress_bar.setVisible(True)
                self.progress_label.setVisible(True)
                self.progress_label.setText("Descarga iniciada...")
                
                # start download and installation
                self.downloader.start()
            else:
                QMessageBox.warning(self, "Error", "La actualizacion ya esta en curso.")
        else:
            QMessageBox.critical(self, "Error", "Actualizador no disponible.")
    
    def _on_download_progress(self, downloaded: int, total: int):
        # handle download progress updates
        if total > 0:
            progress = int((downloaded / total) * 100)
            self.progress_bar.setValue(progress)
            
            # format file sizes
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            self.progress_label.setText(f"Descargando: {downloaded_mb:.1f} / {total_mb:.1f} MB ({progress}%)")
    
    def _on_extraction_started(self):
        # handle extraction phase
        self.progress_bar.setRange(0, 0)  # indeterminate progress
        self.progress_label.setText("Extrayendo archivos...")
    
    def _on_installation_started(self):
        # handle installation phase
        self.progress_label.setText("Instalando...")
    
    def _on_update_completed(self):
        # handle successful update completion
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Actualizacion completada!")
        
        # show completion message with restart info
        QMessageBox.information(
            self,
            "Actualizacion completada",
            "La actualizacion se ha completado satisfactoriamente!\n\n"
            "La aplicacion se reiniciara.\n\n"
            "Los datos se preservaran."
        )
        
        # close the application so the update script can restart it
        from PyQt6.QtCore import QTimer, QCoreApplication
        import sys
        
        # close the dialog first
        self.accept()
        
        # ensure all file handles are closed and app shuts down cleanly
        def shutdown_app():
            QCoreApplication.instance().quit()
            sys.exit(0)
        
        # use a short delay to ensure everything is closed properly
        QTimer.singleShot(500, shutdown_app)
    
    def _on_download_failed(self, error: str):
        # handle update errors
        self.progress_label.setText("Descarga sin exito!")
        self.update_button.setEnabled(True)
        self.update_button.setText("Reintentar descarga")
        self.skip_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        QMessageBox.critical(
            self,
            "Descarga sin exito",
            f"Fallo al descargar actualizacion:\n{error}"
        )
    
    def _skip_version(self):
        # SKIP UPDATE
        # mark version as skipped in update manager
        main_window = self.parent()
        if hasattr(main_window, 'update_manager'):
            main_window.update_manager.skip_version(self.update_info.version)
        
        QMessageBox.information(
            self,
            "Version omitida",
            f"Version {self.update_info.version} se omitira.\n"
            "No se volvera a mostrar esta version."
        )
        
        self.reject()  # close dialog
    
    def _apply_styling(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #E2E8F0;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 13px;
            }
            QLabel#headerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #F59E0B;
                padding: 10px;
            }
            QLabel#versionLabel {
                font-size: 14px;
                color: #94A3B8;
                padding: 5px;
            }
            QGroupBox {
                color: #E2E8F0;
                font-weight: bold;
                border: 1px solid #334155;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #F59E0B;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #E2E8F0;
            }
            QProgressBar {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                text-align: center;
                color: #E2E8F0;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #F59E0B;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 12px 20px;
                color: #E2E8F0;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:pressed {
                background-color: #1E293B;
            }
            QPushButton:disabled {
                background-color: #1E293B;
                color: #6B7280;
                border-color: #374151;
            }
            QPushButton#updateButton {
                background-color: #F59E0B;
                border-color: #D97706;
                color: #1F2937;
            }
            QPushButton#updateButton:hover {
                background-color: #D97706;
            }
            QPushButton#updateButton:pressed {
                background-color: #B45309;
            }
        """)