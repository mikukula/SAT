#local imports
from database.main_database import DatabaseManager
from constants import Constants
from ui_logic.new_setup import *
import sys

#ui imports
from PyQt6.QtWidgets import QApplication

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    constants = Constants()
    #DatabaseManager().initialise_database()
    #if(constants.getDatabasePath() == ""):
    #this will be inside the if statement
    window = NewSetupWindow()

    window.show()
    app.exec()