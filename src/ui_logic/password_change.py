import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QMessageBox

from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities

class PasswordChangeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'change_password.ui'), self)
        self.setupUi()

    def setupUi(self):
        self.oldPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.newPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.retypeNewPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.showAllButton.clicked.connect(self.onShowAllClicked)
        self.changePasswordButton.clicked.connect(self.changePasswordClicked)

    def onShowAllClicked(self):
        #check for echo modes
        if(self.oldPasswordEdit.echoMode() == QLineEdit.EchoMode.Password or
           self.newPasswordEdit.echoMode() == QLineEdit.EchoMode.Password or
           self.retypeNewPasswordEdit.echoMode() == QLineEdit.EchoMode.Password):
        #change to plain if hidden and button to hide
            self.oldPasswordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.newPasswordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.retypeNewPasswordEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.showAllButton.setText("Hide All")
        else:
            self.oldPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.newPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.retypeNewPasswordEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.showAllButton.setText("Show All")

    def changePasswordClicked(self):
        manager = DatabaseManager()
        utils = ConstantsAndUtilities()
        currentUser = manager.getCurrentUser()
        new_password = self.newPasswordEdit.text()

        #check if the old password is correct
        if(not manager.verifyUserByPassword(currentUser.userID, self.oldPasswordEdit.text())):
            passwordAlert = QMessageBox()
            passwordAlert.setWindowTitle("Password Alert")
            passwordAlert.setText("The old password is incorrect")
            passwordAlert.setIcon(QMessageBox.Icon.Information)
            passwordAlert.addButton(QMessageBox.StandardButton.Ok)
            passwordAlert.exec()
        elif(new_password != self.retypeNewPasswordEdit.text()):
            passwordAlert = QMessageBox()
            passwordAlert.setWindowTitle("Password Alert")
            passwordAlert.setText("New passwords don't match")
            passwordAlert.setIcon(QMessageBox.Icon.Information)
            passwordAlert.addButton(QMessageBox.StandardButton.Ok)
            passwordAlert.exec()
        elif(not utils.checkPasswordStrength(new_password)):
            passwordAlert = QMessageBox()
            passwordAlert.setWindowTitle("Password Alert")
            passwordAlert.setText("The new password does not fulfill the requirements")
            passwordAlert.setIcon(QMessageBox.Icon.Information)
            passwordAlert.addButton(QMessageBox.StandardButton.Ok)
            passwordAlert.exec()
        else:
            manager.updatePassword(currentUser.userID, new_password)
            passwordAlert = QMessageBox()
            passwordAlert.setWindowTitle("Password Alert")
            passwordAlert.setText("Your password has been changed successfully")
            passwordAlert.setIcon(QMessageBox.Icon.Information)
            passwordAlert.addButton(QMessageBox.StandardButton.Ok)
            passwordAlert.exec()
            self.close()

        