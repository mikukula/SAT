import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow, QLineEdit

from database.main_database import DatabaseManager
from ui_logic.dashboard_processing import DashboardWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui_design', 'log_in.ui'), self)
        self.setupUi()

    def setupUi(self):
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.showButton.clicked.connect(self.onShowClick)
        self.loginButton.clicked.connect(self.onLoginClick)

    def onShowClick(self):
        if(self.passwordEdit.echoMode() == QLineEdit.EchoMode.Password):
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showButton.setText("Hide")
        else:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showButton.setText("Show")

    def onLoginClick(self):
        manager = DatabaseManager()
        username = self.usernameEdit.text()
        password = self.passwordEdit.text()

        if(manager.verifyUserByPassword(username, password)):
            manager.openSessionToken(username)
            self.dashboard_window = DashboardWindow()
            self.dashboard_window.show()
            self.close()