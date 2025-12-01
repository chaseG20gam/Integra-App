from __future__ import annotations

import os
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPixmap
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout



class AboutDialog(QDialog):
    # about dialog

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._create_dialog()
        self._setup_connections()
        self._apply_styling()

    def _create_dialog(self) -> None:
        self.setWindowTitle("Acerca de Integra")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # icon and title section
        header_layout = QHBoxLayout()
        
        # developer icon/avatar
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(80, 80)
        self.iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.iconLabel.setObjectName("iconLabel")
        self._load_developer_icon()
        header_layout.addStretch()
        header_layout.addWidget(self.iconLabel)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # title label
        self.titleLabel = QLabel("Integra Client Manager", self)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        layout.addWidget(self.titleLabel)
        
        # description label
        self.descriptionLabel = QLabel(
            "Sistema de gestión de clientes desarrollado para Integra\n\n"
            "Versión 1.0\n" 
            "Desarrollado por ChaseG20GAM\n\n"
            "© 2025 Integra",
            self
        )
        self.descriptionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setObjectName("descriptionLabel")
        layout.addWidget(self.descriptionLabel)
        
        # developer link
        self.linkLabel = QLabel('<a href="#">página del desarrollador</a>', self)
        self.linkLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.linkLabel.setObjectName("linkLabel")
        self.linkLabel.setOpenExternalLinks(False)
        layout.addWidget(self.linkLabel)
        
        # add vertical space
        layout.addStretch()
        
        # close button
        self.closeButton = QPushButton("Cerrar", self)
        self.closeButton.setMaximumWidth(100)
        layout.addWidget(self.closeButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_connections(self) -> None:
        # connect signals to slots
        self.closeButton.clicked.connect(self._close_dialog)
        self.linkLabel.linkActivated.connect(self._open_developer_page)
    
    def _close_dialog(self) -> None:
        # debug and close the dialog
        print("Close button clicked!")  # Debug
        self.done(0)  # Alternative to close/accept
        
    def _load_developer_icon(self) -> None:
        # load ico
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'developer_icon.png')
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # scale the image to fit while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    80, 80, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.iconLabel.setPixmap(scaled_pixmap)
                return
        
        # fallback: create a simple placeholder with initials
        self.iconLabel.setText("CG")
        self._apply_icon_fallback_style()
    
    def _apply_icon_fallback_style(self) -> None:
        # apply fallback styling for icon when no image is found
        self.iconLabel.setStyleSheet("""
            QLabel#iconLabel {
                background-color: #3B82F6;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 8px;
                border: 2px solid #1E40AF;
            }
        """)

    def _open_developer_page(self) -> None:
        # open developer page in default browser
        url = "https://github.com/chaseG20gam"
        QDesktopServices.openUrl(QUrl(url))

    def _apply_styling(self) -> None:
        # apply theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #E2E8F0;
            }
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
                padding: 10px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #3B82F6;
                padding: 20px;
            }
            QLabel#descriptionLabel {
                color: #94A3B8;
                line-height: 1.5;
            }
            QLabel#linkLabel {
                color: #3B82F6;
                font-size: 13px;
                padding: 5px;
            }
            QLabel#linkLabel a {
                color: #3B82F6;
                text-decoration: none;
            }
            QLabel#linkLabel a:hover {
                color: #60A5FA;
                text-decoration: underline;
            }
            QLabel#iconLabel {
                background-color: #334155;
                border: 2px solid #475569;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #334155;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 10px 20px;
                color: #E2E8F0;
                font-weight: bold;
                margin: 10px 50px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:pressed {
                background-color: #1E293B;
            }
        """)
    
