from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from mainwindow import Ui_MainWindow


class Login(QDialog):
    """Login window is a independence window, username and passwd are both unchangeable"""
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowTitle("Login")
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        if self.textName.text() == 'foo' and self.textPass.text() == 'bar':
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Bad user or password')

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    login = Login()

    if login.exec_() == QDialog.Accepted:
        print("xxxxR")
        # window = Window()
        # window.show()
        sys.exit(app.exec_())