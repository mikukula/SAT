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
        score_strings = [str(score) + '/5' for score in scores]
        ratings = [(scores[0]+scores[1])/2,
                           (scores[2]+scores[3])/2, scores[4]]
        rating_strings = ["""<span style=" font-size:12pt; color:#007AFF">""" + f"{rating:.2f}/5" + "</span>"
                           for rating in ratings]
        overall_score = sum(ratings)/len(ratings)
        overall_score_string = ("""<span style=" font-size:16pt; color:#00B5B8">""" + f"{overall_score:.2f}/5" +
                                "</span>")

        #set up score labels
        self.tdu_score.setText(score_strings[0])
        self.iab_score.setText(score_strings[1])
        self.spi_score.setText(score_strings[2])
        self.sta_score.setText(score_strings[3])
        self.dsa_score.setText(score_strings[4])

        #set up total ratings
        self.need_score.setText(rating_strings[0])
        self.attitude_score.setText(rating_strings[1])
        self.awareness_score.setText(rating_strings[2])
        self.overall_score.setText(overall_score_string)
        

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