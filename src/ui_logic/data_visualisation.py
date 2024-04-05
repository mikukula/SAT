from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.uic import loadUi
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

        self.questionBox.addItems([question.text for question in questions])
        self.questionBox.currentIndexChanged.connect(lambda: self.redrawGraph())

        self.categoryBox.addItems(["All"] + [category.name for category in reversed(categories)])
        self.categoryBox.currentIndexChanged.connect(lambda: self.repopulateQuestions())

        self.viewBox.addItems(["Role", "Response", "Technicality"])
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

    def redrawGraph(self):

        #remove the previous graph
        while self.graph_layout.count():
            widget = self.graph_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        self.deleteGraph()

        manager = DatabaseManager()
        current_question = manager.getQuestion(qText=self.questionBox.currentText())

        #check if no survey data available
        if(self.surveyBox.currentText() == ""):
            return
        self.current_graph = MatplotlibWidget(current_question, manager.getSurvey(date=datetime.strptime(self.surveyBox.currentText(), "%Y-%m-%d").date()), 
                                        self.viewBox.currentText())
        self.graph_layout.addWidget(self.current_graph)

    def deleteGraph(self):
        if(self.current_graph is not None):
            plt.close(self.current_graph.current_figure)
            self.current_graph = None

    


        

class MatplotlibWidget(QWidget):
    def __init__(self, question, survey, view_type):
        super().__init__()
        self.current_figure = None
        layout = QVBoxLayout()

        if(view_type == "Role"):
            self.canvas = FigureCanvas(self.plotGraph(question, survey.surveyID))
        elif(view_type == "Response"):
            self.canvas = FigureCanvas(self.plotHorizontalGraph(question, survey.surveyID))
        else:
            self.canvas = FigureCanvas(self.plotHorizontalGraphByTechnicality(question, survey.surveyID))

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
        ax.barh(y, technical_data, height=bar_height, label='Technical Users', color='blue')
        ax.barh(y, non_technical_data, height=bar_height, left=technical_data, label='Non-Technical Users', color='orange')
        
        ax.set_yticks(y)
        ax.set_yticklabels(responses)
        ax.legend(title='User Group', bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.set_xlabel('Number of Responses')
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




