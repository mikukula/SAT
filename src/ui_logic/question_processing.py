import os
#random unique identifier generator
import uuid
#object serialization for saving progress
import pickle
#gui imports
from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QButtonGroup, QMessageBox
from PyQt6.QtGui import QMouseEvent
from PyQt6.uic import loadUi

from database.main_database import DatabaseManager
from constants import ConstantsAndUtilities

class QuestionWidget(QWidget):
    def __init__(self, parent_widget):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui_design', 'question_widget.ui'), self)
        self.next_button.clicked.connect(self.onNextButtonClick)
        self.back_button.clicked.connect(self.onBackButtonClick)
        self.parent_widget = parent_widget
        manager = DatabaseManager()
        user = manager.getCurrentUser()
        self.questions_for_role = manager.getQuestionsForRole(user.roleID)
        self.current_survey_id = manager.getSurveyToCompleteForUser(user.userID)
        categories = []
        self.question_categories_frames = []
        #add all question categories that have corresponding questions
        for question in self.questions_for_role:
            if(question.category not in categories):
                categories.append(question.category)
        #add all categories as buttons
        #and assign the first category as the active category in reverse order
        #since we are starting from the top and the first element will end up last (think stack)
        for index, category in enumerate(reversed(categories)):
            questionCategory = QuestionCategoryFrame(category, self)
            #inserting at the front is not inefficient but in this case
            #there are few categories and this approach allows for less
            #frames to be added
            self.question_categories_frames.insert(0, questionCategory)
            self.questionCategoriesFrame.layout().insertWidget(0, questionCategory)
            #set the first category to be the active category (which in this case is the last element of the loop)
            if(index == len(categories) - 1):
                self.onCategoryChanged(questionCategory)

        

    def onCategoryChanged(self, questionCategory, startFromEnd = False):
        #set the new active category
        self.active_category_frame = questionCategory
        #set all question category frames to default
        for question in self.question_categories_frames:
            question.setDefaultStyleSheet()
        #highlight the new current active category
        questionCategory.highlightCategory()
        manager = DatabaseManager()
        if(startFromEnd == False):
            self.setupQuestion(manager.getQuestionsForRoleByCategory(manager.getCurrentUser().roleID, questionCategory.category.categoryID)[0])
        else:
            self.setupQuestion(manager.getQuestionsForRoleByCategory(manager.getCurrentUser().roleID, questionCategory.category.categoryID)[-1])

    def setupQuestion(self, question):
        
        manager = DatabaseManager()
        questions = manager.getQuestionsForRoleByCategory(manager.getCurrentUser().roleID, self.active_category_frame.category.categoryID)
        self.current_question = question
        question_number = self.findQuestionIndex(question, questions)
        self.question_number_label.setText(ConstantsAndUtilities().formatHTML(f"Question {question_number + 1} out of {len(questions)}", True))
        #Display answer instructions based on answer type
        if(question.answer.type == "single"):
            self.answer_type_label.setText(ConstantsAndUtilities().formatHTML("Please choose a single most adequate answer", True))
        else:
            self.answer_type_label.setText(ConstantsAndUtilities().formatHTML("Please choose all answers that apply", True))

        #setup the question
        self.question_label.setText(ConstantsAndUtilities().formatHTML(question.text, True))

        #setup the answers
        self.answers_frame = AnswersFrame(question.answer, self)
        self.scrollArea.setWidget(self.answers_frame)

        self.progress_label.setText(ConstantsAndUtilities().formatHTML(f"Progress: {round(Answers().getNumberOfAnsweredQuestions()/len(self.questions_for_role)*100)}%"))

        #load previous answers if they exist
        previous_answer_dictionary = Answers().answers
        #get all responses to the current question if they exist
        try:
            responses = previous_answer_dictionary[self.current_question.questionID]     
        except KeyError:
            return
        
        #loop through all answer frames and check if the answer is in the list
        for answer_frame in self.answers_frame.answer_frames:
            for response in responses:
                if(answer_frame.answer_text == response):
                    answer_frame.check_box.setChecked(True)



    def onNextButtonClick(self):
        #save the current question
        self.saveAnswer()
        #handle displaying the next question
        manager = DatabaseManager()
        next_question = self.getNextQuestion(manager.getQuestionsForRoleByCategory(manager.getCurrentUser().roleID, self.active_category_frame.category.categoryID))
        if(next_question is None):
            current_category_index = self.findCategoryIndex()
            #handle the user reaching the last question
            if(current_category_index == len(self.question_categories_frames) - 1):
                if(not self.checkResponsesCompleted()):
                    complete_all_box = QMessageBox()
                    complete_all_box.setWindowTitle("Responses not gathered")
                    complete_all_box.setText("Before you submit please answer all remaining questions.")
                    complete_all_box.addButton(QMessageBox.StandardButton.Ok)
                    complete_all_box.exec()
                    return
                submit_box = QMessageBox()
                submit_box.setWindowTitle("Submit Answers")
                submit_box.setText("The survey is now finished.\nPlease press Ok to submit answers\nor Cancel if you still want to change them.")
                submit_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                box_clicked = submit_box.exec()

                if(box_clicked == QMessageBox.StandardButton.Ok):
                    self.submitResponses()
                elif(box_clicked == QMessageBox.StandardButton.Cancel):
                    print("change answers")
            else:
                self.onCategoryChanged(self.question_categories_frames[current_category_index + 1])

        else:
            self.setupQuestion(next_question)

    def onBackButtonClick(self):
        #save the current question
        self.saveAnswer()

        manager = DatabaseManager()
        previous_question = self.getPreviousQuestion(manager.getQuestionsForRoleByCategory(manager.getCurrentUser().roleID, self.active_category_frame.category.categoryID))

        if(previous_question is None):
            current_category_index = self.findCategoryIndex()
            print("index is none")
            if(current_category_index == 0):
                print("This is the first question")
            else:
                self.onCategoryChanged(self.question_categories_frames[current_category_index - 1], True)
        else:
            self.setupQuestion(previous_question)

    def saveAnswer(self):
        answers = self.answers_frame.getCheckedAnswers()
        answer_texts = [text.answer_text for text in answers]
        Answers().saveAnswers(self.current_question.questionID, answer_texts)

    def checkResponsesCompleted(self):
        if(Answers().getNumberOfAnsweredQuestions() == len(self.questions_for_role)):
            return True
        return False
    
    def submitResponses(self):
        answers = Answers().answers
        manager = DatabaseManager()
        current_user = manager.getCurrentUser().userID
        #the first survey is always processed first
        try:
            current_survey = manager.getSurveyToCompleteForUser(current_user)
        #return if there are no surveys
        #would mean a bug or database tampering
        except IndexError:
            return

        for questionID, all_answers in answers.items():
            for single_answer in all_answers:
                manager.addResponse(questionID, current_user, single_answer, current_survey)

        Answers().deleteAnswers()
        manager.setUserFinishedSurvey(current_survey, current_user)
        self.parent_widget.onStartSurveyClick(None)
        
        
        



        
    #loop to find the number of the question within a subset of questions
    #this function is needed since the same question may appear twice in different parts of memory
    #hence index() function won't work
    def findQuestionIndex(self, question, questions):
        for index, array_question in enumerate(questions):
            if(array_question.questionID == question.questionID):
                return index
            
    def findCategoryIndex(self):
        for index, array_category in enumerate(self.question_categories_frames):
            if(array_category.category.categoryID == self.active_category_frame.category.categoryID):
                return index
    
    #get the next question from a question subset
    def getNextQuestion(self, questions):
        current_question_index = self.findQuestionIndex(self.current_question, questions)

        #try to get the next question from the subset or return None if it's the last question
        try:
            return questions[current_question_index + 1]
        except IndexError:
            return None
    
    #get the previous question from a subset of questions
    #very similar to the previous function but kept separate for readability purpose
    #and different out of bounds handling
    def getPreviousQuestion(self, questions):
        current_question_index = self.findQuestionIndex(self.current_question, questions)

        #try to get the previous question from the subset or return None if it's the last question
        if(current_question_index > 0):
            return questions[current_question_index - 1]
        else:
            return None
        


#a frame with all the answers
class AnswersFrame(QFrame):
    def __init__(self, answer, question_widget: QuestionWidget):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.answer = answer
        self.possible_answers = answer.answer.split(';')
        self.parent_widget = question_widget
        self.answer_frames = []
        self.button_group = QButtonGroup()

        for possible_answer in self.possible_answers:
            single_frame = SingleAnswerFrame(possible_answer)
            self.answer_frames.append(single_frame)
            #make the checkbox mutually exclusive is it's a single answer
            if(question_widget.current_question.answer.type == "single"):
                self.button_group.addButton(single_frame.check_box)
            self.layout.addWidget(single_frame)

    def getCheckedAnswers(self):
        checked_answers = []
        for answer_frame in self.answer_frames:
            if(answer_frame.check_box.isChecked()):
                checked_answers.append(answer_frame)
        return checked_answers



#a frame for a single answer
class SingleAnswerFrame(QFrame):
    def __init__(self, answer_text):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.answer_text = answer_text
        self.check_box = QCheckBox()
        self.check_box.setStyleSheet("""QCheckBox::indicator {
                                        width: 20px;
                                        height: 20px;
                                    }""")
        self.layout.addWidget(self.check_box)
        
        self.answer_label = QLabel()
        self.answer_label.setMinimumWidth(310)
        self.answer_label.setWordWrap(True)
        self.answer_label.setText(ConstantsAndUtilities().formatHTML(answer_text))
        self.layout.addWidget(self.answer_label)
        



class QuestionCategoryFrame(QFrame):
    def __init__(self, category, question_widget: QuestionWidget):
        super().__init__()
        self.category = category
        self.parent_widget = question_widget
        self.questionCategoryLabel = QLabel()
        self.setMinimumSize(182, 65)
        self.questionCategoryLabel.setWordWrap(True)
        self.questionCategoryLabel.setText(ConstantsAndUtilities().formatHTML(category.name, True))
        frame_name = str(uuid.uuid4())
        self.setObjectName(frame_name)
        self.setDefaultStyleSheet()
        questionLayout = QHBoxLayout(self)
        questionLayout.addWidget(self.questionCategoryLabel)
        self.mousePressEvent = self.onCategoryClick

    def onCategoryClick(self, event: QMouseEvent):
        manager = DatabaseManager()
        available_questions = manager.getQuestionsByCategory(self.category.categoryID)
        self.parent_widget.question_number_label.setText(self.category.categoryID)
        self.parent_widget.onCategoryChanged(self)

    def highlightCategory(self):
        
        background_style_sheet = f"QFrame#{self.objectName()}"
        background_style_sheet += """{
                            background-color: lightGray;
                        }\n"""
        self.setStyleSheet(self.styleSheet() + background_style_sheet)

    def setDefaultStyleSheet(self):
        style_sheet = f"QFrame#{self.objectName()}"
        style_sheet += """{
                            border: 2px solid black;
                            border-radius: 30px;
                        }\n"""
        style_sheet += """QFrame:hover {
	                    background-color: lightGray;
	                    border-radius: 30px;
                        }"""
        self.setStyleSheet(style_sheet)


#a class to store all answers
class Answers:
    def __init__(self):
        manager = DatabaseManager()
        self.surveyID = manager.getSurveyToCompleteForUser(manager.getCurrentUser().userID)
        self.path_to_file = os.path.join(ConstantsAndUtilities().getUserFolder(DatabaseManager().getCurrentUser().userID), f'answers{self.surveyID}.pkl')
        self.loadAnswers()

    def loadAnswers(self):
        
        try:
            with open(self.path_to_file, 'rb') as file:
                self.answers = pickle.load(file)
        except FileNotFoundError:
            with open(self.path_to_file, 'w') as file:
                self.answers = {}
        except EOFError:
            self.answers = {}

    def saveAnswers(self, question_id, answer_text):
        #skip if there is no answer
        self.answers[question_id] = answer_text
        with open(self.path_to_file, 'wb') as file:
            pickle.dump(self.answers, file)

    def deleteAnswers(self):
        print(self.path_to_file)
        if(os.path.exists(self.path_to_file)):
            os.remove(self.path_to_file)

    def getNumberOfAnsweredQuestions(self):
        count = 0
        for key, value in self.answers.items():
            if(value != []):
                count += 1
        return count
    
class NoQuestionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.noQuestionsLabel = QLabel()
        self.noQuestionsLabel.setWordWrap(True)
        self.noQuestionsLabel.setText(ConstantsAndUtilities().formatHTML("There are currently no surveys for you to do.", True, 16, 600))