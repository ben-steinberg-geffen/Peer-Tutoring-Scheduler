import pandas as pd

"""
TO-DO
HOME PAGE
ROUND BUTTONS
CHECK IF UPLOADS ACTUALLY WORK
SEARCH HISTORY
BACK BUTTON
STUDENT STATUS
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QLineEdit, QTextEdit, QStackedWidget, QTableWidget, QTableWidgetItem
    #QGridLayout?
    #QCheckBox once user is dont searching for student
    

)
from PyQt5.QtCore import Qt #for alignments IF NEEDED


class PeerTutoringApp(QMainWindow):
    def __init__(self):
        super().__init__() 
        # calls constructor of parent class
        #creating a class from a parent class, so have to initialize parent code.

        self.setWindowTitle("Peer Tutoring Scheduler")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("background-color: #e8ecee;")

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.page_stack = QStackedWidget()
        self.layout.addWidget(self.page_stack)

        self.create_home_page()
        self.create_upload_page()
        self.create_search_page()
        self.create_navigation()

        #self.layout.addWidget(self.home_page)
        self.page_stack.addWidget(self.home_page)
        self.page_stack.setCurrentWidget(self.home_page)

        self.peer_tutors = None
        self.students_classes = None

    def create_home_page(self):
        self.home_page = QWidget()
        layout = QVBoxLayout(self.home_page)

        welcome_label = QLabel('<h2>Welcome to the Peer Tutoring Schedule!</h2>')
        welcome_label.setStyleSheet("font-weight: bold; font-size: 20px;")
        layout.addWidget(welcome_label, alignment=Qt.AlignCenter)

        self.page_stack.addWidget(self.home_page)

    def create_upload_page(self): #creating a widget, accessing self.
       
        self.upload_page = QWidget()
        layout = QVBoxLayout(self.upload_page) #creates a horizontal layout

        layout.addWidget(QLabel('<h2 padding: 0px 3px 0px 3px; font-weight: bold; border-radius: 5px;">Upload Documents</h2>'))

        #1.
        self.peer_tutors_btn = QPushButton("Upload Peer Tutors File") #adds button to layout
        self.peer_tutors_btn.clicked.connect(self.upload_peer_tutors)   
        self.peer_tutors_btn.setStyleSheet("padding: 7px 10px 7px 10px; border: 1px solid #667c89; border-radius: 5px;") #top right bottom left
        layout.addWidget(self.peer_tutors_btn, alignment=Qt.AlignCenter)

        #2.
        self.students_classes_btn = QPushButton("Upload Students and Classes File")
        self.students_classes_btn.clicked.connect(self.upload_students_classes)
        self.students_classes_btn.setStyleSheet("padding: 7px 10px 7px 10px; border: 1px solid #667c89; border-radius: 5px;")
        layout.addWidget(self.students_classes_btn, alignment=Qt.AlignCenter)

        self.upload_status = QTextEdit()
        self.upload_status.setReadOnly(True)
        layout.addWidget(self.upload_status)

        self.page_stack.addWidget(self.upload_page)

    def create_search_page(self):

        self.search_page = QWidget()
        layout = QVBoxLayout(self.search_page)

        layout.addWidget(QLabel("<h2 font-style: bold; >Search Students or Tutors</h2>"))

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit() 
        self.search_input.setPlaceholderText("Enter name of student or peer tutor")
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_person)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)

        self.page_stack.addWidget(self.search_page)

    def create_navigation(self):

        nav_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload")
        upload_btn.setStyleSheet("padding: 5px 15px; border: 1px solid #667c89; border-radius: 8px; font-size: 15px;")
        
        #REVIEW and fix up
        upload_btn.clicked.connect(lambda: self.page_stack.setCurrentWidget(self.upload_page))
        nav_layout.addWidget(upload_btn)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet("padding: 5px 15px; border: 1px solid #667c89; border-radius: 8px; font-size: 15px;")
        search_btn.clicked.connect(lambda: self.page_stack.setCurrentWidget(self.search_page))
        nav_layout.addWidget(search_btn)

        self.layout.addLayout(nav_layout)

    def upload_peer_tutors(self):

        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Peer Tutors File", "", "CSV Files (*.csv)")
        # _ is for second return type, contains file type filter. ignored.
        # first argument refers to class instance
        # second argument is title/reference. doesn't do much but needed or else error!
        # third argument to go to default file dialog
        # fourth argument to only allow csv files

        if file_path:
            self.peer_tutors = pd.read_csv(file_path)
            self.upload_status.append("Peer tutors file uploaded successfully!")

    def upload_students_classes(self):
   
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Students and Classes File", "", "CSV Files (*.csv)")
        if file_path:
            self.students_classes = pd.read_csv(file_path)
            self.upload_status.append("Students and classes file uploaded successfully!")

    def search_person(self):
  
        #I WANT TO EDIT THE TEXTBOX DIMENSIONS. DO I HAVE TO MAKE IT A PUSHBUTTON?
        self.search_input.setStyleSheet("padding: 5px 15px; border: 1px solid #667c89; border-radius: 5px; height: 10px; width: 40px;")
        
        name = self.search_input.text().strip()
        if not name:
            self.results_area.setText("Please enter a name to search.")
            return

        results = []
        if self.peer_tutors is not None and name in self.peer_tutors.values:
            results.append(f"Peer Tutor Found: {name}")

        if self.students_classes is not None:
            student_data = self.students_classes[self.students_classes['Student\'s name: '] == name]
            if not student_data.empty:
                classes = ", ".join(student_data['Subject (and level if applicable) that the student needs tutoring in: '])
                results.append(f"Student Found: {name}\nClasses: {classes}")

        self.results_area.setText("\n\n".join(results) if results else "No results found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PeerTutoringApp() #set layout for window
    window.show()
    sys.exit(app.exec_())
