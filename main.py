import sys
from PyQt5.QtWidgets import QApplication
from Library_management_system import LibraryManagementSystem

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryManagementSystem()
    window.show()
    sys.exit(app.exec_())
