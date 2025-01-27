import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

# Create a subclass of QMainWindow (optional but recommended for larger apps)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Peer Tutoring Scheduler")
        self.setGeometry(100, 100, 600, 400)  # x, y, width, height
        
        # Set background color using stylesheet
        self.setStyleSheet("background-color: #efebf7;")  # Light gray color

if __name__ == "__main__":
    # Create the application object
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Execute the application's main loop
    sys.exit(app.exec_())
