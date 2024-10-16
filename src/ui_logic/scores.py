import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database.main_database import DatabaseManager

class ScoresWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = DatabaseManager()
        self.loadUI()
        self.setupComboBoxes()
        self.current_graph = None
        #start calculation on start
        self.chooseDisplayType()

    def loadUI(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(script_dir, '..', 'ui_design', 'scores.ui')
        loadUi(ui_path, self)

    def setupComboBoxes(self):
        surveys = self.manager.getSurvey()
        self.surveyBox.addItems(str(survey.date) for survey in surveys)
        self.surveyBox.currentTextChanged.connect(lambda: self.chooseDisplayType())

        self.typeBox.addItems(["List", "Graph"])
        self.typeBox.currentTextChanged.connect(lambda: self.chooseDisplayType())

    def chooseDisplayType(self):

        current_type = self.typeBox.currentIndex()
        scores, ratings, overall_score = self.calculateScores()
        if(current_type == 0):
            self.displayList(scores, ratings, overall_score)
        else:
            self.displayGraph(ratings, overall_score)

    def displayList(self, scores, ratings, overall_score):

        #clear the display widget and the graph before switching views
        self.clear_graph()

        #this widget is for the textual list, loaded from a UI file
        display_widget = ScoreListWidget()
        score_strings = [str(score) + '/5' for score in scores]
        rating_strings = ["""<span style=" font-size:12pt; color:#007AFF">""" + f"{rating:.2f}/5" + "</span>"
                           for rating in ratings]
        overall_score_string = ("""<span style=" font-size:16pt; color:#00B5B8">""" + f"{overall_score:.2f}/5" +
                                "</span>")
        
        #set up score labels
        display_widget.tdu_score.setText(score_strings[0])
        display_widget.iab_score.setText(score_strings[1])
        display_widget.spi_score.setText(score_strings[2])
        display_widget.sta_score.setText(score_strings[3])
        display_widget.dsa_score.setText(score_strings[4])

        #set up total ratings
        display_widget.need_score.setText(rating_strings[0])
        display_widget.attitude_score.setText(rating_strings[1])
        display_widget.awareness_score.setText(rating_strings[2])
        display_widget.overall_score.setText(overall_score_string)

        #add the textual list to the display frame
        self.display_frame.layout().addWidget(display_widget)

    def displayGraph(self, ratings, overall_score):
        self.clear_graph()
        # Create and add the graph
        self.current_graph = GraphWidget.create_ratings_graph(ratings, overall_score)
        self.display_frame.layout().addWidget(self.current_graph)

    def clear_graph(self):
        """
        Cleans up and removes the current graph if it exists.
        It also handles clearing up the display_widget so can be called for both uses.
        """
        if self.display_frame.layout():
            # Remove all widgets from the layout
            while self.display_frame.layout().count():
                item = self.display_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Clear the current graph reference
        if self.current_graph:
            plt.close(self.current_graph.figure)  # Close the matplotlib figure
            self.current_graph = None

    def calculateScores(self):
        
        current_surveyid = self.surveyBox.currentIndex() + 1
        responses = self.manager.getResponsesBySurvey(current_surveyid)
        categories = self.manager.getCategories()
        scores = [ThreadedScoreCalculator().calculateScorePerCategory(responses, category.categoryID) for category in categories]
        ratings = [(scores[0]+scores[1])/2,
                           (scores[2]+scores[3])/2, scores[4]]
        overall_score = sum(ratings)/len(ratings)

        return scores, ratings, overall_score

# Small class for loading the list widget
class ScoreListWidget(QWidget):
    def __init__(self):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(script_dir, '..', 'ui_design', 'score_list.ui')
        loadUi(ui_path, self)
        
# Class for multithreaded asynchronous score calculation
class ThreadedScoreCalculator:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.manager = DatabaseManager()
        self.questions = self.manager.getQuestions()
        self.answers = self.manager.getAnswers()

    def getResponsesPerCategory(self, responses, categoryID):
        
        questions = set(q.questionID for q in self.manager.getQuestionsByCategory(categoryID))
        return [r for r in responses if r.questionID in questions]
    
    def getResponseWeight(self, response):

        #retrieve the answer list
        response_text = response.response
        question_response = next((x for x in self.questions if response.questionID == x.questionID), None)
        #return if each response is + or -1
        if(len(question_response.answer_weights) == 2):
            return question_response.answer_weights
        
        answer_response = next((x for x in self.answers if question_response.answerID == x.answerID), None)
        answer_text = answer_response.answer
        answers = answer_text.split(';')
        weights = question_response.answer_weights.split(',')
        return weights[answers.index(response_text)]
        
    def calculateResponseScore(self, response) -> tuple[int, int]:
        """Calculate score for a single response"""
        weight = self.getResponseWeight(response)
        if weight in ["+1", "0", "-1"]:
            return 0, 0
        return int(weight), 1
        
    def calculateScorePerCategory(self, responses, categoryID: int) -> float:
        """Multithreaded version of score calculation"""
        responses = self.getResponsesPerCategory(responses, categoryID)
        
        if not responses:
            return 0.0
            
        total_score = 0
        total_count = 0
        
        # Using ThreadPoolExecutor for asynchronous score calculation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map the score calculation to all responses
            future_scores = list(executor.map(self.calculateResponseScore, responses))
            
            # Aggregate results
            for score, count in future_scores:
                total_score += score
                total_count += count
                
        return round(total_score/total_count, 2) if total_count > 0 else 0.0
    

class GraphWidget:

    def create_ratings_graph(ratings, overall_score):
    
        # Create figure and axis
        fig = Figure(figsize=(8, 6), facecolor='none')
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        
        # Data for plotting
        categories = ['Need', 'Attitude', 'Awareness', 'Overall']
        all_values = list(ratings) + [overall_score]
        colors = [(0/255, 122/255, 255/255, 0.4),  # Blue with transparency
                 (0/255, 122/255, 255/255, 0.4),  # Blue with transparency
                 (0/255, 122/255, 255/255, 0.4),  # Blue with transparency
                 (0/255, 122/255, 255/255, 1.0)]  # Solid blue for the last bar
        
        # Create bars
        bars = ax.bar(categories, all_values, color=colors)
        
        # Customize the graph
        ax.set_ylim(0, 5)  # Set y-axis range from 0 to 5
        ax.set_ylabel('Rating')

        # Make the grid show behind the bars with slight transparency
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        # Create canvas
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background-color:white;")
        
        # Adjust layout to prevent label cutoff
        fig.tight_layout()
        
        return canvas