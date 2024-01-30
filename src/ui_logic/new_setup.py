from PyQt6.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QMessageBox
from PyQt6.uic import loadUiType, loadUi
from PyQt6.QtGui import QIcon
import os
import re
from constants import Constants
from database.main_database import DatabaseManager

#find absolute directory
script_dir = os.path.dirname(os.path.abspath(__file__))
ui_file_path = os.path.join(script_dir, '..', 'ui_design', 'new_setup.ui')

#load ui
NewSetupWindow, QNewSetupWindowBase = loadUiType(ui_file_path)

class NewSetupWindow(QMainWindow, NewSetupWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setupUiElements()
        

    def setupUiElements(self):
        self.browseButton.clicked.connect(self.onBrowseButtonClick)
        self.nextButton.clicked.connect(self.onNextButtonClick)
        self.fileTextEdit.setPlainText(Constants().getDatabasePath())
        self.setWindowIcon(QIcon(Constants().main_icon_location))

    def onBrowseButtonClick(self):

        file_dialog = QFileDialog()

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

        constants = Constants()

        if ((self.radioButtonExistingDatabase.isChecked() or self.radioButtonNewDatabase.isChecked()) and
            constants.validatePath(self.fileTextEdit.toPlainText())):

            constants.setDatabasePath(self.fileTextEdit.toPlainText())
            self.setupRegistrationScreen()
            
    
    def setupRegistrationScreen(self):
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'create_account.ui'), self)
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.createAccountButton.clicked.connect(self.onCreateAccountClick)
        self.backButton.clicked.connect(self.onBackClick)
        self.showButton.clicked.connect(self.onShowClick)

        roles = DatabaseManager().getRole()
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
        role = DatabaseManager().getRole(text)
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
        
        if(self.checkUsernameUnique(self.usernameEdit.text()) != True):
            usernameAlert = QMessageBox()
            usernameAlert.setWindowTitle("Username alert")
            usernameAlert.setText("Your username has already been used. Please choose a different one")
            usernameAlert.setIcon(QMessageBox.Icon.Information)
            usernameAlert.addButton(QMessageBox.StandardButton.Ok)
            usernameAlert.exec()
            return
        
        if(self.checkUsernameReq(self.usernameEdit.text()) != True):
            usernameAlert = QMessageBox()
            usernameAlert.setWindowTitle("Username alert")
            usernameAlert.setText("Your username does not fulfill the requirements. Please refer to the guidance below.")
            usernameAlert.setIcon(QMessageBox.Icon.Information)
            usernameAlert.addButton(QMessageBox.StandardButton.Ok)
            usernameAlert.exec()
            return
        
        if(self.checkPasswordStrength(self.passwordEdit.text()) != True):
            passwordAlert = QMessageBox()
            passwordAlert.setWindowTitle("Password alert")
            passwordAlert.setText("Your password is not strong enough. Please refer to the guidence below to create a strong password")
            passwordAlert.setIcon(QMessageBox.Icon.Information)
            passwordAlert.addButton(QMessageBox.StandardButton.Ok)
            passwordAlert.exec()
            return
        
        databaseManager = DatabaseManager()
        print(databaseManager.getRole('CEO').roleID)
        userID = self.usernameEdit.text()
        password = self.passwordEdit.text()
        role = self.roleList.currentText()
        admin_rights = True
        databaseManager.addUser(userID, role, password, admin_rights)
        

    
    def checkPasswordStrength(self, password):
        # Check if the password has at least 12 characters
        if len(password) < 12:
            return False

        # Check if the password contains at least 1 symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False

        # Check if the password contains at least 1 uppercase letter
        if not any(char.isupper() for char in password):
            return False

        # If all conditions are met, the password is strong
        return True
    
    def checkUsernameUnique(self, username):
        users = DatabaseManager().getUser()
        usernames = []
        for user in users:
            usernames.append(user.userID)

        for u in usernames:
            if(u == username):
                return False
            
        return True
    
    def checkUsernameReq(self, username):
        if(len(username) < 5):
            return False
        
        if not re.match("^[a-zA-Z0-9]+$", username):
            return False
        
        return True


        
        