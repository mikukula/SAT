import os
import keyring
from PyQt6.uic import loadUiType, loadUi
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtCore import Qt

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
        #if dashboard is called without a valid session open quit and open login screen
        if(token is None):
            from ui_logic.login import LoginWindow
            self.loginWindow = LoginWindow()
            self.loginWindow.show()
            self.close()
            return
        
        user = DatabaseManager().getUser(token=token)
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

    
    def onInviteUserClick(self, event: QMouseEvent) -> None:
        self.invite_window = QMainWindow()
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'create_account_new_user.ui'), self.invite_window)
        self.invite_window.show()

    def onLogoutClick(self, event: QMouseEvent) -> None:
        #delete the token from the database and the machine
        DatabaseManager().closeSessionToken()
        print(keyring.get_password(Constants().keyring_service_name, Constants().keyring_user_name))
        #show the login window
        from ui_logic.login import LoginWindow
        self.loginWindow = LoginWindow()
        self.loginWindow.show()
        self.close()


