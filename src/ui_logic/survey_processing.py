import os

from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QHBoxLayout, QCheckBox, QMessageBox
from PyQt6.uic import loadUi

from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities

class InviteUsersToSurveyWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui_design', 'invite_user_to_survey.ui'), self)
        self.setupUI()

    def setupUI(self):
        #set up the layout for the scroll box and other ui elements
        self.user_frames = []
        scroll_layout = self.scrollAreaWidgetContents.layout()
        self.checkBox.stateChanged.connect(lambda: self.selectAllPressed(self.checkBox))
        self.startSurveyButton.clicked.connect(self.onStartSurveyClicked)
        
        for user in DatabaseManager().getUser():
            if(user.roleID != 'UNIVERSAL'):
                frame_to_add = SingleUserFrame(user.userID)
                self.user_frames.append(frame_to_add)
                scroll_layout.insertWidget(scroll_layout.count() - 1, frame_to_add)

    def selectAllPressed(self, button):
        for frame in self.user_frames:
            if(button.isChecked()):
                frame.check_box.setChecked(True)
            else:
                frame.check_box.setChecked(False)
    
    def onStartSurveyClicked(self):
        manager = DatabaseManager()
        survey_id = manager.createSurvey()
        for frame in self.user_frames:
            manager.inviteUserToSurvey(frame.username, manager.getSurvey(survey_id).surveyID)

        submitted_box = QMessageBox()
        submitted_box.setWindowTitle("Survey created")
        submitted_box.setText("The survey has been created.")
        submitted_box.addButton(QMessageBox.StandardButton.Ok)
        submitted_box.exec()

#a frame for a single user
#similar to SingleAnswerFrame in question_processing module
#could be potentially refactored to one class
class SingleUserFrame(QFrame):
    def __init__(self, username):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.username = username
        self.check_box = QCheckBox()
        self.check_box.setStyleSheet("""QCheckBox::indicator {
                                        width: 20px;
                                        height: 20px;
                                    }""")
        self.layout.addWidget(self.check_box)
        
        self.answer_label = QLabel()
        self.answer_label.setMinimumWidth(310)
        self.answer_label.setWordWrap(True)
        self.answer_label.setText(ConstantsAndUtilities().formatHTML(username))
        self.layout.addWidget(self.answer_label)
        self.layout.addStretch()