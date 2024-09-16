#a script to add some random data to the database for testing

from database.main_database import DatabaseManager
import time
import random
from datetime import datetime

#add users for all roles
def createUsers():
    manager = DatabaseManager()
    users = ["admin", "test.ceo", "test.cfo", "test.cpo",
             "test.ciso", "test.cio", "test.cto"]
    roles = ["UNIVERSAL", 'CEO', 'CFO', 'CPO', 'CISO', 'CIO',
             'CTO']
    default_password = "Password123!#" #not meant to be secure ;)
    
    for i, username in enumerate(users):
        if(i >= 3):
            technicality = True
        else:
            technicality = False
        manager.addUser(username, roles[i], default_password, technicality)

#number is the number of surveys to be created
def createSurveys(number: int):
    manager = DatabaseManager()
    begin_date = "1/1/2008"
    #create the appropriate number of surveys
    for i in range (0, number):
        date = random_date(begin_date, "1/1/2024", random.random())
        manager.createSurvey(date)
        begin_date = date.strftime("%d/%m/%Y")
    inviteUsers()

def inviteUsers():
    manager = DatabaseManager()
    users = manager.getUser()
    surveys = manager.getSurvey()

    for user in users:
        for survey in surveys:
            if(user.roleID == "UNIVERSAL"):
                continue
            manager.inviteUserToSurvey(user.userID, survey.surveyID)

def addResponses():
    manager = DatabaseManager()
    users = manager.getUser()

    #add responses for each survey for each user
    for user in users:
        for survey in manager.getSurveysToCompleteForUser(user.userID):
            available_questions = manager.getQuestionsForRole(user.roleID)
            #go through all available questions
            for question in available_questions:
                chosen_responses = generateResponses(question)
                #add all responses
                for response in chosen_responses:
                    manager.addResponse(question.questionID, user.userID, response, survey.surveyID)
            manager.setUserFinishedSurvey(survey.surveyID, user.userID)

#generate a list of responses
def generateResponses(question):

    chosen_responses = []
    available_responses = question.answer.answer.split(';')

    #add only one response if response type is single
    if(question.answer.type == "single"):
        repetitions = 1
    #multiple otherwise
    else:
        repetitions = random.randint(1, len(available_responses) - 1)

    used_answers = []

    #add the chosen responses and return them
    for i in range (0, repetitions):
        
        answer_id = random.randint(0, len(available_responses) - 1)
        if(answer_id in used_answers):
            continue
        else:
            chosen_responses.append(available_responses[answer_id])
            used_answers.append(answer_id)

    return chosen_responses

#from stack overflow - random date generation
def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))

#stack overflow - random date generation
def random_date(start, end, prop):
    return datetime.strptime(str_time_prop(start, end, '%d/%m/%Y', prop), '%d/%m/%Y')


#unneccessary additions are commented out as needed

createUsers()
createSurveys(3)
inviteUsers()
addResponses()