#external library imports
import sys
from sqlalchemy.exc import OperationalError

#local imports
from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities
from ui_logic.new_setup import NewSetupWindow, DashboardWindow
from ui_logic.login import LoginWindow

#ui imports
from PyQt6.QtWidgets import QApplication




#app starting point
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    constants = ConstantsAndUtilities()

    #if there is no registered database path, wrong path, or no users
    #are found assume a new installation
    #and initialise new setup
    if(constants.getDatabasePath() == ""):
        window = NewSetupWindow()

    #check for a wrong path
    try:
        user = DatabaseManager().getUser()
        if(user == []):
            window = NewSetupWindow()
    except OperationalError:
        window = NewSetupWindow()

    #if not a new install check for session token and if found
    #log in right away
    #if not found open login screen
    else:
        manager = DatabaseManager()
        user = manager.getCurrentUser()
        if(user is None):
            window = LoginWindow()
        else:
            manager.openSessionToken(user.userID)
            window = DashboardWindow()

    window.show()
    app.exec()
    