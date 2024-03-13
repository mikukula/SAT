import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QMessageBox

from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities

class CreateAccountWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.constants = ConstantsAndUtilities()
        self.database_manager = DatabaseManager()
        loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui_design', 'create_account_new_user.ui'), self)
        self.setupUi()

    def setupUi(self):
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.inviteButton.clicked.connect(self.onCreateAccountClick)
        self.showButton.clicked.connect(self.onShowClick)

        roles = self.database_manager.getRole()
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
        role = self.database_manager.getRole(text)
        self.roleDescription.setPlainText(role.description)


    def onShowClick(self):
        if(self.passwordEdit.echoMode() == QLineEdit.EchoMode.Password):
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showButton.setText("Hide")
        else:
            self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showButton.setText("Show")

    def onCreateAccountClick(self):
        
        if(self.database_manager.checkUsernameUnique(self.usernameEdit.text()) != True):
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
        admin_rights = self.adminCheckBox.isChecked()
        self.database_manager.addUser(userID, role, password, admin_rights)
        accountCreatedInfo = QMessageBox()
        accountCreatedInfo.setWindowTitle("Account Created")
        accountCreatedInfo.setText("The account with username " + userID + " has been created successfully.\n" +
                                   "Please let the user know and inform them to change the default password you have created.")
        accountCreatedInfo.setIcon(QMessageBox.Icon.Information)
        accountCreatedInfo.addButton(QMessageBox.StandardButton.Ok)
        accountCreatedInfo.exec()
        self.close()