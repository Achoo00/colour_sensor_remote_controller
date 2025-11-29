import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the main Qt loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
