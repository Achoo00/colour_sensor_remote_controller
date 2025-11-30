import os
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

def setup_environment():
    """Set up environment variables and check for required components."""
    # Add current directory to PATH for MPV DLLs
    os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ["PATH"]
    
    # Set Qt DPI awareness
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

def check_deluge_connection():
    """Check if Deluge daemon is running and accessible."""
    try:
        from config.deluge_config import get_deluge_client
        client = get_deluge_client()
        if client:
            try:
                # Test a simple RPC call
                client.call('daemon.info')
                print("✅ Successfully connected to Deluge")
                return True
            except Exception as e:
                print(f"⚠️ Deluge RPC error: {str(e)}")
                return False
        return False
    except ImportError:
        print("⚠️ deluge-client package not found. Install it with: pip install deluge-client")
    except Exception as e:
        print(f"⚠️ Deluge connection error: {str(e)}")
    
    print("\nTo set up Deluge authentication:")
    print("1. Make sure Deluge is installed and running")
    print("2. Check if the Web UI is accessible at http://localhost:8112")
    print("3. Default credentials: username=deluge, password=deluge")
    print("4. Check if port 58846 is not blocked by firewall")
    print("\nRunning in simulation mode for Deluge operations...\n")
    return False

def main():
    # Set up environment first
    setup_environment()
    
    # Check Deluge connection
    if not check_deluge_connection():
        print("⚠️ Running in simulation mode for Deluge operations")
    
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        # Run the main Qt loop
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(
            None,
            "Application Error",
            f"An error occurred: {str(e)}\n\nThe application will now exit."
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
