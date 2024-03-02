#external library imports
import sys
import keyring

#local imports
from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities
from ui_logic.new_setup import *
from ui_logic.login import LoginWindow

#ui imports
from PyQt6.QtWidgets import QApplication

#app starting point
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    constants = ConstantsAndUtilities()

    #if no registered database path found assume a new installation
    #and initialise new setup
    if(constants.getDatabasePath() == ""):
        window = NewSetupWindow()

    #if not a new install check for session token and if found
    #log in right away
    #if not found open login screen
    else:
        manager = DatabaseManager()
        user = manager.getUser(token=keyring.get_password(constants.keyring_service_name, constants.keyring_user_name))
        if(user is None):
            window = LoginWindow()
        else:
            manager.openSessionToken(user.userID)
            window = DashboardWindow()

    window.show()
    app.exec()
    