import os
from PyQt6.uic import loadUiType, loadUi
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtCore import Qt

from constants import ConstantsAndUtilities
from database.main_database import DatabaseManager
from ui_logic.create_account import CreateAccountWindow
from ui_logic.password_change import PasswordChangeWindow
from ui_logic.question_processing import QuestionWidget, NoQuestionsWidget
from ui_logic.survey_processing import InviteUsersToSurveyWidget
from ui_logic.data_visualisation import GraphWidget
from ui_logic.scores import ScoresWidget


#find absolute directory
script_dir = os.path.dirname(os.path.abspath(__file__))
ui_file_path = os.path.join(script_dir, '..', 'ui_design', 'dashboard.ui')

#load ui
DashboardWindow, QDashboardWindow = loadUiType(ui_file_path)

class DashboardWindow(QMainWindow, DashboardWindow):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.setupUi(self)
        self.setupUiElements()
        self.onStartSurveyClick(None)

    def setupUiElements(self):
        self.setWindowIcon(QIcon(ConstantsAndUtilities().main_icon_location))
        
        user = DatabaseManager().getCurrentUser()
        self.usernameLabel.setText(user.userID.upper())
        self.roleLabel.setText(user.roleID)
        
        self.account_management_frame.mousePressEvent = self.onAccountManagementClick
        self.startSurveyFrame.mousePressEvent = self.onStartSurveyClick
        self.view_stats_frame.mousePressEvent = self.onViewStatsClick
        self.view_scores_frame.mousePressEvent = self.onViewScoresClick
        self.main_frame_layout = QVBoxLayout(self.main_frame)

        #delete unneccessary buttons if not admin (simpler to delete than add)
        if(user.roleID != "UNIVERSAL"):
            self.view_stats_frame.deleteLater()
            self.view_scores_frame.deleteLater()

    #clear the main frame before setting it up with different children
    def clearMainFrame(self):
        #return if there is no layout
        if(self.main_frame.layout() == None):
            return
        #otherwise loop through layout elements and remove them all
        while self.main_frame.layout().count():
            item = self.main_frame.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if(self.graph is not None):
            self.graph.deleteGraph()
        
        

    #temporary start survey handling
    def onStartSurveyClick(self, event: QMouseEvent):
        self.clearMainFrame()
        self.menu_item_label.setText("Survey")
        manager = DatabaseManager()
        if(manager.getCurrentUser().roleID != 'UNIVERSAL'):
            if(manager.getSurveyToCompleteForUser(manager.getCurrentUser().userID) is None):
                self.main_frame_layout.addWidget(NoQuestionsWidget().noQuestionsLabel)
                return
            questionWidget = QuestionWidget(self)
            self.main_frame_layout.addWidget(questionWidget.question_frame)
            return
        invite_to_survey_widget = InviteUsersToSurveyWidget()
        self.main_frame_layout.addWidget(invite_to_survey_widget.invite_frame)
        

    #on frame click handling
    def onAccountManagementClick(self, event: QMouseEvent) -> None:
        
        self.clearMainFrame()
        account_management_widget = QWidget()
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'account_management_widget.ui'), account_management_widget)
        self.menu_item_label.setText(self.accountManagementLabel.text())
        self.main_frame_layout.addWidget(account_management_widget.account_management_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        if(DatabaseManager().getCurrentUser().roleID == "UNIVERSAL"):
            account_management_widget.account_management_frame.layout().insertWidget(1, account_management_widget.invite_user_frame)
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

    def onViewStatsClick(self, event: QMouseEvent):
        self.clearMainFrame()
        self.menu_item_label.setText("Statistics")
        
        if(DatabaseManager().getCurrentUser().roleID == 'UNIVERSAL'):
            self.graph = GraphWidget()
            
            self.main_frame_layout.addWidget(self.graph.frame)

    def onViewScoresClick(self, event: QMouseEvent):
        self.clearMainFrame()
        self.menu_item_label.setText("View Ratings")

        view_stats_widget = ScoresWidget()
        self.main_frame_layout.addWidget(view_stats_widget.scores_frame, alignment=Qt.AlignmentFlag.AlignCenter)