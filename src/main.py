import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from models.database import init_database
from  ui.main_window import MainWindow


def main() -> None:
    
    app = QApplication(sys.argv)
    
    # set application properties for proper Windows taskbar integration
    app.setApplicationName("Integra Client Manager")
    app.setApplicationDisplayName("Integra Client Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Integra")
    
    # set application icon BEFORE setting app user model id
    ico_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.ico")
    png_path = os.path.join(os.path.dirname(__file__), "assets", "developer_icon.png")
    
    icon = None
    if os.path.exists(ico_path):
        icon = QIcon(ico_path)
    elif os.path.exists(png_path):
        icon = QIcon(png_path)
    
    if icon and not icon.isNull():
        app.setWindowIcon(icon)
    
    # force windows taskbar to use our icon with more aggressive approach
    try:
        import ctypes
        from ctypes import wintypes
        
        # set app user model id to separate from python
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Integra.ClientManager.1.0")
        
        # additional windows-specific icon forcing
        if icon and not icon.isNull():
            # get the window handle after creating the app but before showing
            import ctypes.wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            # this will be applied after window is created
            pass
            
    except:
        pass  # ignore if not on windows or if ctypes fails
    
    init_database()

    window = MainWindow()
    
    # ensure the icon is set on the window as well
    if icon and not icon.isNull():
        window.setWindowIcon(icon)
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
