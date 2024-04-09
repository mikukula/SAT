from PyQt6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QStyledItemDelegate, QLabel
from PyQt6.QtGui import QPalette, QStandardItem, QFontMetrics
from PyQt6.QtCore import Qt, QEvent
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import textwrap
import os

from database.main_database import DatabaseManager

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_graph = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        loadUi(os.path.join(script_dir, '..', 'ui_design', 'graph_widget.ui'), self)
        self.setupUi()

    def setupUi(self):
        manager = DatabaseManager()
        questions = manager.getQuestions()
        surveys = manager.getSurvey()
        categories = manager.getCategories()

        self.surveyBox.addItems([str(survey.date) for survey in surveys])
        self.surveyBox.currentIndexChanged.connect(lambda: self.redrawGraph())

        self.survey_combo_box = self.surveyBox

        self.questionBox.addItems([question.text for question in questions])
        self.questionBox.currentIndexChanged.connect(lambda: self.redrawGraph())

        self.categoryBox.addItems(["All"] + [category.name for category in reversed(categories)])
        self.categoryBox.currentIndexChanged.connect(lambda: self.repopulateQuestions())

        self.viewBox.addItems(["Role", "Response", "Technicality", "Stakeholder"])
        self.viewBox.currentIndexChanged.connect(lambda: self.redrawGraph())

        self.graph_layout = QVBoxLayout(self.graph_frame)
        self.redrawGraph()

    def repopulateQuestions(self):

        self.questionBox.blockSignals(True)
        self.questionBox.clear()
        questions_to_add = DatabaseManager().getQuestionsByCategory(category_name=self.categoryBox.currentText())
        if(questions_to_add == []):
            questions_to_add = DatabaseManager().getQuestions()
        self.questionBox.addItems([question.text for question in questions_to_add])
        self.questionBox.blockSignals(False)
        self.redrawGraph()

    def repopulateSurveys(self, is_multiple: bool):
        surveys = DatabaseManager().getSurvey()
        if(is_multiple):
            self.survey_combo_box = CheckableComboBox()
            
            self.survey_combo_box.addItems([str(survey.date) for survey in surveys])
            self.graph_setting_frame.layout().addWidget(self.survey_combo_box, 1, 0)
            self.survey_combo_box.setCheckedItemsByIndex([i for i in range(0, 5)])
            self.survey_combo_box.setCheckedItemsChangedCallback(self.redrawGraph)
            #adjust the label for multiple surveys
            self.survey_label.setText("<html><head/><body><p><span style=' font-size:12pt;'>Surveys:</span></p></body></html>")
        else:
            self.survey_combo_box = QComboBox()
            self.survey_combo_box.addItems([str(survey.date) for survey in surveys])
            self.survey_combo_box.currentIndexChanged.connect(lambda: self.redrawGraph())
            self.graph_setting_frame.layout().addWidget(self.survey_combo_box, 1, 0)
            #adjust the label for a single survey
            self.survey_label.setText("<html><head/><body><p><span style=' font-size:12pt;'>Survey:</span></p></body></html>")

    def addUserComboBox(self):
        manager = DatabaseManager()
        #add list of users
        self.user_combo_box = QComboBox()
        users = manager.getUser()
        self.user_combo_box.addItems([user.userID for user in users if user.roleID != "UNIVERSAL"])
        self.user_combo_box.currentIndexChanged.connect(lambda: self.redrawGraph())

        #add user label
        user_label = QLabel()
        user_label.setText("<html><head/><body><p><span style=' font-size:12pt;'>User:</span></p></body></html>")
        lay = self.graph_setting_frame.layout()
        lay.addWidget(user_label, 0, 4)
        lay.addWidget(self.user_combo_box, 1, 4)

    def removeUserComboBox(self):
        lay = self.graph_setting_frame.layout()
        lay.itemAtPosition(0, 4).widget().deleteLater()
        lay.itemAtPosition(1, 4).widget().deleteLater()




    def redrawGraph(self):

        #repopulate survey list for multiple or single choice
        if(self.viewBox.currentText() == "Stakeholder" and type(self.survey_combo_box) == QComboBox):
            self.repopulateSurveys(True)
            self.addUserComboBox()
        elif(self.viewBox.currentText() != "Stakeholder" and type(self.survey_combo_box) == CheckableComboBox):
            self.repopulateSurveys(False)
            self.removeUserComboBox()
        #remove the previous graph
        while self.graph_layout.count():
            widget = self.graph_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        self.deleteGraph()

        manager = DatabaseManager()
        current_question = manager.getQuestion(qText=self.questionBox.currentText())

        #check if no survey data available
        if(self.survey_combo_box.currentText() == ""):
            return
        
        if(self.viewBox.currentText() != "Stakeholder"):
            self.current_graph = MatplotlibWidget(current_question, manager.getSurvey(date=datetime.strptime(self.survey_combo_box.currentText(), "%Y-%m-%d").date()), 
                                        self.viewBox.currentText())
        #for stakeholder choice
        else:
            survey_dates = self.survey_combo_box.currentData()
            surveys = []
            for date in survey_dates:
                surveys.append(manager.getSurvey(date=datetime.strptime(date, "%Y-%m-%d").date()))
            self.current_graph = MatplotlibWidget(current_question, surveys[:5], self.viewBox.currentText(), self.user_combo_box.currentText())

        self.graph_layout.addWidget(self.current_graph)

    def deleteGraph(self):
        if(self.current_graph is not None):
            plt.close(self.current_graph.current_figure)
            self.current_graph = None

    


        

class MatplotlibWidget(QWidget):
    def __init__(self, question, survey, view_type, user=None):
        super().__init__()
        self.current_figure = None
        layout = QVBoxLayout()

        if(view_type == "Role"):
            self.canvas = FigureCanvas(self.plotGraph(question, survey.surveyID))
        elif(view_type == "Response"):
            self.canvas = FigureCanvas(self.plotHorizontalGraph(question, survey.surveyID))
        elif(view_type == "Technicality"):
            self.canvas = FigureCanvas(self.plotHorizontalGraphByTechnicality(question, survey.surveyID))
        else:
            self.canvas = FigureCanvas(self.plotHorizontalGraphByStakeholder(question, [s.surveyID for s in survey], user))

        self.canvas.figure.set_facecolor('none')
        self.canvas.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setMinimumSize(self.canvas.size())

    def plotGraph(self, question, surveyID):

        manager = DatabaseManager()
        answers = question.answer.answer.split(';')
        # Stakeholder types
        users = [user for user in manager.getUser() if user.roleID != 'UNIVERSAL']

        # Create a DataFrame
        df = pd.DataFrame(self.getResponseArray(surveyID, question, answers, users), columns=answers, index=[user.userID for user in users])

        # Create the figure and axis objects
        fig, ax = plt.subplots(figsize=(8, 4))

        # Plot the stacked bar chart
        bar_width = 0.5
        index = np.arange(len(users))
        bottom = np.zeros(len(users))
        for i, answer in enumerate(answers):
            ax.bar(index, df[answer], bar_width, label=answer, bottom=bottom)
            bottom += df[answer]

        # Customize the plot
        ax.set_xticks(index)
        ax.set_xticklabels([user.roleID for user in users])
        ax.set_yticklabels([])
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
        #set up title
        title = question.text
        ax.set_title(textwrap.fill(title, width=30))

        # Adjust the layout and display the plot
        plt.tight_layout()
        self.current_figure = fig
        return self.current_figure
    
    def plotHorizontalGraph(self, question, surveyID):

        responses = question.answer.answer.split(';')
        users = [user for user in DatabaseManager().getUser() if user.roleID != 'UNIVERSAL']
        data = self.getResponseArray(surveyID, question, responses, users)
        num_responses = len(responses)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        bar_height = 0.4
        y = np.arange(num_responses)
        
        left = np.zeros(num_responses)
        for i, category in enumerate([user.userID for user in users]):
            values = data[i]
            ax.barh(y, values, left=left, height=bar_height, label=category)
            left += values
        
        ax.set_yticks(y)
        ax.set_yticklabels(responses)
        
        ax.legend(title='Role', bbox_to_anchor=(1.02, 1), loc='upper left')
        
        ax.set_xlabel('Number of Responses')
        ax.set_title(textwrap.fill(question.text, width=40))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        plt.tight_layout()
        self.current_figure = fig
        return self.current_figure
    
    def plotHorizontalGraphByTechnicality(self, question, surveyID):

        responses = question.answer.answer.split(';')
        users = [user for user in DatabaseManager().getUser() if user.roleID != 'UNIVERSAL']
        data = self.getResponseArray(surveyID, question, responses, users)
        num_responses = len(responses)
        fig, ax = plt.subplots(figsize=(8, 4))
        bar_height = 0.4
        y = np.arange(num_responses)
        
        
        technical_roles = [user.roleID for user in DatabaseManager().getUsersByTechnicality(True)]
        non_technical_roles = [user.roleID for user in DatabaseManager().getUsersByTechnicality(False)]
        
        # Combine responses for each user group
        technical_data = np.sum([data[i] for i, user in enumerate(users) if user.roleID in technical_roles], axis=0)
        non_technical_data = np.sum([data[i] for i, user in enumerate(users) if user.roleID in non_technical_roles], axis=0)
        
        # Plot the combined data for each user group
        ax.barh(y, technical_data, height=bar_height, label='Technical Stakeholders', color='blue')
        ax.barh(y, non_technical_data, height=bar_height, left=technical_data, label='Business Stakeholders', color='orange')
        
        ax.set_yticks(y)
        ax.set_yticklabels(responses)
        ax.legend(title='User Group', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.set_xlabel('Number of Responses')
        ax.set_title(textwrap.fill(question.text, width=40))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.tight_layout()
        self.current_figure = fig
        return self.current_figure
    
    def plotHorizontalGraphByStakeholder(self, question, surveyIDs, userID):
        manager = DatabaseManager()
        user = manager.getUser(userID)
        responses = question.answer.answer.split(';')
        data = []
        for surveyID in surveyIDs:
            survey_data = self.getResponseArray(surveyID, question, responses, [user])
            data.append(survey_data[0])

        num_surveys = len(surveyIDs)
        fig, ax = plt.subplots(figsize=(8, 4))
        bar_height = 0.4
        y = np.arange(num_surveys)
        left = np.zeros(num_surveys)
        for i, response in enumerate(responses):
            values = [data[j][i] for j in range(num_surveys)]
            ax.barh(y, values, left=left, height=bar_height, label=response)
            left += values

        ax.set_yticks(y)

        surveys = []
        for surveyID in surveyIDs:
            surveys.append(manager.getSurvey(surveyID))

        ax.set_yticklabels([str(survey.date) for survey in surveys])
        ax.legend(title='Response', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.set_xlabel("Number of Answers\n" + r"$\bf{USER}$: " + userID)
        ax.set_title(textwrap.fill(question.text, width=40))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.tight_layout()
        self.current_figure = fig
        return self.current_figure
    
    def getResponseArray(self, surveyID, question, answers, users):

        manager = DatabaseManager()

        #initialise response data
        #one row per user, one row per possible answers
        #1 means the user chose the answer, 0 the answer was not chosen
        response_data = []
        for user in users:
            responses = [response.response for response in manager.getResponse(user.roleID, surveyID, question.questionID)]
            responses_to_add = []
            for answer in answers:
                if(answer in responses):
                    responses_to_add.append(1)
                else:
                    responses_to_add.append(0)
            response_data.append(responses_to_add)
        
        return response_data


#checkable combo box implementation from
#https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
#originally written for PyQt5, changes were made to make it work with PyQt6
#setCheckedItemsByIndex and callback handling are own additions
class CheckableComboBox(QComboBox):

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumWidth(100)
        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

        #for callback support
        self.checked_items_changed_callback = None

    def setCheckedItemsChangedCallback(self, callback):
        self.checked_items_changed_callback = callback

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                index = self.view().indexAt(event.position().toPoint())
                item = self.model().item(index.row())
                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True
            return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

        # Call the checked items changed callback if provided
        if self.checked_items_changed_callback:
            self.checked_items_changed_callback()

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                res.append(self.model().item(i).data())
        return res
    ########################################################
    def setCheckedItemsByIndex(self, indexes):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if i in indexes:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
        self.updateText()