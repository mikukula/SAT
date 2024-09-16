import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget

from database.main_database import DatabaseManager

class ScoresWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = DatabaseManager()
        self.loadUI()
        self.setupSurveyBox()
        #start calculation on start
        self.calculateScores()

    def loadUI(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(script_dir, '..', 'ui_design', 'scores.ui')
        loadUi(ui_path, self)

    def setupSurveyBox(self):
        surveys = DatabaseManager().getSurvey()
        self.surveyBox.addItems(str(survey.date) for survey in surveys)
        self.surveyBox.currentTextChanged.connect(lambda: self.calculateScores())

    def calculateScores(self):
        
        current_surveyid = self.surveyBox.currentIndex() + 1
        responses = self.manager.getResponsesBySurvey(current_surveyid)
        categories = self.manager.getCategories()
        scores = [self.calculateScorePerCategory(responses, category.categoryID) for category in categories]
        #set up score labels
        self.tdu_score.setText(str(scores[0]))
        self.iab_score.setText(str(scores[1]))
        self.spi_score.setText(str(scores[2]))
        self.dsa_score.setText(str(scores[3]))
        

    def getResponseWeight(self, response):

        #retrieve the answer list
        response_text = response.response
        manager = DatabaseManager()
        question_response = manager.getQuestion(response.questionID)
        #return if each response is + or -1
        if(len(question_response.answer_weights) == 2):
            return question_response.answer_weights
        
        answer_response = manager.getAnswer(question_response.answerID)
        answer_text = answer_response.answer
        answers = answer_text.split(';')
        weights = question_response.answer_weights.split(',')
        return weights[answers.index(response_text)]
    
    def getResponsesPerCategory(self, responses, categoryID):
        questions = set(q.questionID for q in DatabaseManager().getQuestionsByCategory(categoryID))
        return [r for r in responses if r.questionID in questions]
    
    def calculateScorePerCategory(self, responses, categoryID):
        
        score = 0
        #number of responses that count towards the score
        num_count = 0
        responses = self.getResponsesPerCategory(responses, categoryID)
        for response in responses:
            weight = self.getResponseWeight(response)
            #pass if there are multiple answers
            if(weight in ["+1", "0", "-1"]):
                continue
            score += int(weight)
            num_count += 1
        return round(score/num_count, 2)