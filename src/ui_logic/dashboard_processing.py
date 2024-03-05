import os
import keyring
from PyQt6.uic import loadUiType, loadUi
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QLineEdit
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtCore import Qt

from constants import ConstantsAndUtilities
from database.main_database import DatabaseManager
from ui_logic.create_account import CreateAccountWindow
from ui_logic.password_change import PasswordChangeWindow


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
        self.setWindowIcon(QIcon(ConstantsAndUtilities().main_icon_location))
        
        user = DatabaseManager().getCurrentUser()
        self.usernameLabel.setText(user.userID.upper())
        self.roleLabel.setText(user.roleID)
        self.account_management_frame.mousePressEvent = self.onAccountManagementClick

    #on frame click handling
    def onAccountManagementClick(self, event: QMouseEvent) -> None:
        account_management_widget = QWidget()
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'account_management_widget.ui'), account_management_widget)

        layout = QGridLayout(self.main_frame)
        layout.addWidget(account_management_widget.account_management_frame, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

        account_management_widget.invite_user_frame.mousePressEvent = self.onInviteUserClick
        account_management_widget.logout_frame.mousePressEvent = self.onLogoutClick
        account_management_widget.change_password_frame.mousePressEvent = self.onChangePasswordClick

    def onChangePasswordClick(self, event: QMouseEvent):
        self.change_password_window = PasswordChangeWindow()
        self.change_password_window.show()

    def onInviteUserClick(self, event: QMouseEvent) -> None:
        self.createAccountWindow = CreateAccountWindow()
        self.createAccountWindow.show()

    def onLogoutClick(self, event: QMouseEvent) -> None:
        #delete the token from the database and the machine
        DatabaseManager().closeSessionToken()
        #show the login window
        from ui_logic.login import LoginWindow
        self.loginWindow = LoginWindow()
        self.loginWindow.show()
        self.close()


