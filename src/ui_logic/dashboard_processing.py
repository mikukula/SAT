import os
import keyring
from PyQt6.uic import loadUiType
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QIcon

from constants import Constants
from database.main_database import DatabaseManager


#find absolute directory
script_dir = os.path.dirname(os.path.abspath(__file__))
ui_file_path = os.path.join(script_dir, '..', 'ui_design', 'dashboard.ui')

#load ui
DashboardWindow, QDashboardWindow = loadUiType(ui_file_path)

class DashboardWindow(QMainWindow, DashboardWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupUiElements()

    def setupUiElements(self):
        self.setWindowIcon(QIcon(Constants().main_icon_location))
        token = keyring.get_password("SAT", "user_token")
        if(token != None):
            user = DatabaseManager().getUser(token=token)
            self.usernameLabel.setText(user.userID)
            self.roleLabel.setText(user.roleID)

