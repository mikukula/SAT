#new setup process logic

from PyQt6.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QMessageBox
from PyQt6.uic import loadUiType, loadUi
from PyQt6.QtGui import QIcon
import os

#local imports
from constants import ConstantsAndUtilities
from database.main_database import DatabaseManager
from ui_logic.dashboard_processing import DashboardWindow
from ui_logic.login import LoginWindow

#find absolute directory
script_dir = os.path.dirname(os.path.abspath(__file__))
ui_file_path = os.path.join(script_dir, '..', 'ui_design', 'new_setup.ui')

#load ui
NewSetupWindow, QNewSetupWindowBase = loadUiType(ui_file_path)

class NewSetupWindow(QMainWindow, NewSetupWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.constants = ConstantsAndUtilities()
        self.setupUiElements()
        
    
    def setupUiElements(self):
        self.browseButton.clicked.connect(self.onBrowseButtonClick)
        self.nextButton.clicked.connect(self.onNextButtonClick)
        self.fileTextEdit.setPlainText(self.constants.getDatabasePath())
        self.setWindowIcon(QIcon(self.constants.main_icon_location))

    def onBrowseButtonClick(self):

        file_dialog = QFileDialog()
        #process when an existing database is accessible
        if(self.radioButtonExistingDatabase.isChecked()):
            
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            file_dialog.setNameFilter("Database Files (*.db)")
        
        elif(self.radioButtonNewDatabase.isChecked()):
            file_dialog.setFileMode(QFileDialog.FileMode.Directory)

        else:
            return
            
        if file_dialog.exec() != QFileDialog.DialogCode.Accepted:
            return
            
        selected_file = file_dialog.selectedFiles()[0]
        self.fileTextEdit.setPlainText(selected_file)

    #move on to registration screen and set the path where the database will be created
    def onNextButtonClick(self):

        if(not self.constants.validatePath(self.fileTextEdit.toPlainText())):
            usernameAlert = QMessageBox()
            usernameAlert.setWindowTitle("Path invalid")
            usernameAlert.setText("Please choose a correct path")
            usernameAlert.setIcon(QMessageBox.Icon.Warning)
            usernameAlert.addButton(QMessageBox.StandardButton.Ok)
            usernameAlert.exec()
            return

        if (self.radioButtonNewDatabase.isChecked()):

            self.constants.setDatabasePath(self.fileTextEdit.toPlainText())
            self.manager = DatabaseManager()
            self.manager.initialise_database()
            self.setupRegistrationScreen()

        elif (self.radioButtonExistingDatabase.isChecked()):
            self.constants.setDatabasePath(self.fileTextEdit.toPlainText())
            self.loginScreen = LoginWindow()
            self.loginScreen.show()
            self.close()


    ################################# 
    #registration screen is displayed
    def setupRegistrationScreen(self):
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'create_admin_account.ui'), self)
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.createAccountButton.clicked.connect(self.onCreateAccountClick)
        self.backButton.clicked.connect(self.onBackClick)
        self.showButton.clicked.connect(self.onShowClick)

        roles = self.manager.getRole()
        roleIDs = []

        for role in roles:
            roleIDs.append(role.roleID)
        
        self.roleList.addItems(roleIDs)
        self.roleList.currentTextChanged.connect(self.onRoleIDChange)
        try:
            self.roleDescription.setPlainText(roles[0].description)
        except IndexError as e:
            print("Can't get description")

    def onRoleIDChange(self, text):
        role = self.manager.getRole(text)
        self.roleDescription.setPlainText(role.description)


    def onShowClick(self):
        if(self.passwordEdit.echoMode() == QLineEdit.EchoMode.Password):
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showButton.setText("Hide")
        else:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showButton.setText("Show")

    def onBackClick(self):
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'new_setup.ui'), self)
        self.setupUiElements()

    def onCreateAccountClick(self):
        
        if(self.manager.checkUsernameUnique(self.usernameEdit.text()) != True):
            usernameAlert = QMessageBox()
            usernameAlert.setWindowTitle("Username alert")
            usernameAlert.setText("Your username has already been used. Please choose a different one")
            usernameAlert.setIcon(QMessageBox.Icon.Information)
            usernameAlert.addButton(QMessageBox.StandardButton.Ok)
            usernameAlert.exec()
            return
        
        if(self.constants.checkUsernameReq(self.usernameEdit.text()) != True):
            usernameAlert = QMessageBox()
            usernameAlert.setWindowTitle("Username alert")
            usernameAlert.setText("Your username does not fulfill the requirements. Please refer to the guidance below.")
            usernameAlert.setIcon(QMessageBox.Icon.Information)
            usernameAlert.addButton(QMessageBox.StandardButton.Ok)
            usernameAlert.exec()
            return
        
        if(self.constants.checkPasswordStrength(self.passwordEdit.text()) != True):
            passwordAlert = QMessageBox()
            passwordAlert.setWindowTitle("Password alert")
            passwordAlert.setText("Your password is not strong enough. Please refer to the guidence below to create a strong password")
            passwordAlert.setIcon(QMessageBox.Icon.Information)
            passwordAlert.addButton(QMessageBox.StandardButton.Ok)
            passwordAlert.exec()
            return
        
        userID = self.usernameEdit.text()
        password = self.passwordEdit.text()
        role = self.roleList.currentText()
        admin_rights = True
        self.manager.addUser(userID, role, password, admin_rights)
        self.manager.openSessionToken(userID)
        self.dashboard_window = DashboardWindow()
        self.dashboard_window.show()
        self.close()


        
        