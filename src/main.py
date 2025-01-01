#external library imports
import sys
import os
from sqlalchemy.exc import OperationalError

#local imports
from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities
from ui_logic.new_setup import NewSetupWindow, DashboardWindow
from ui_logic.login import LoginWindow

#ui imports
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QIcon

def enforce_light_mode(app):
    # Force light palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    app.setPalette(palette)

#app starting point
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application-wide icon
    app.setWindowIcon(QIcon(os.path.join('src', 'resources', 'logos', 'favicon.png')))
    
    # Enforce light mode
    enforce_light_mode(app)
    app.setStyle('Fusion')  # Use Fusion style for consistent look
    
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