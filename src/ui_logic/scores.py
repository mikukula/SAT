import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

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
        surveys = self.manager.getSurvey()
        self.surveyBox.addItems(str(survey.date) for survey in surveys)
        self.surveyBox.currentTextChanged.connect(lambda: self.calculateScores())

    def calculateScores(self):
        
        current_surveyid = self.surveyBox.currentIndex() + 1
        responses = self.manager.getResponsesBySurvey(current_surveyid)
        categories = self.manager.getCategories()
        scores = [ThreadedScoreCalculator().calculateScorePerCategory(responses, category.categoryID) for category in categories]
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



class ThreadedScoreCalculator:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.score_lock = Lock()
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
        
        # Using ThreadPoolExecutor to parallelize score calculation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map the score calculation to all responses
            future_scores = list(executor.map(self.calculateResponseScore, responses))
            
            # Aggregate results
            for score, count in future_scores:
                total_score += score
                total_count += count
                
        return round(total_score/total_count, 2) if total_count > 0 else 0.0