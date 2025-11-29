import sys

from PyQt6.QtWidgets import QApplication

from models.database import init_database
from  ui.main_window import MainWindow


def main() -> None:
    
    app = QApplication(sys.argv)
    init_database()

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
