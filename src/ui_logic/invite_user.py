import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow, QLineEdit

class InviteUserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui_design', 'create_account_new_user.ui'), self)
        self.setupUi()