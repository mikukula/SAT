from sqlalchemy import create_engine, Column, Boolean, Integer, String, Sequence, ForeignKey, Enum, CheckConstraint, Date
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, joinedload
from base64 import b64encode
from datetime import datetime
import os
import bcrypt
import keyring

from database.default_database_details import *
from constants import ConstantsAndUtilities


DatabaseBase = declarative_base()

class DatabaseManager:

    def __init__(self):
        self.constants = ConstantsAndUtilities()
        db_url = "sqlite:///" + self.constants.getDatabasePath() + "/" + self.constants.database_name
        self.engine = create_engine(db_url, echo=False)
        self.Base = DatabaseBase
        self.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        

    def get_session(self):
        return self.Session()
    
    def initialise_database(self):

        session = self.get_session()
        
        initialise_roles(session)

        initialise_categories(session)

        initialise_answers(session)

        initialise_questions(session)

    
    def addRole(self, roleID, description):
        role = Role(roleID=roleID, description=description)
        session = self.get_session()
        try:
            session.add(role)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    def getRole(self, roleID=None):
        if(roleID == None):
            return self.get_session().query(Role).all()
        
        return self.get_session().query(Role).filter_by(roleID=roleID).first()


    def addUser(self, userID, roleID, password, is_technical=False):
        hashed_password = self.hashPassword(password)
        user = User(userID=userID, roleID=roleID, hash_salt=hashed_password, is_technical=is_technical)
        session = self.get_session()

        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    def createSurvey(self, date=None):
        if(date is None):
            survey = Survey(date=datetime.now())
        else:
            survey = Survey(date=date)

        with self.get_session() as session:
            try:
                session.add(survey)
                session.commit()
                return survey.surveyID
            except:
                session.rollback()

    def addResponse(self, questionID, userID, response, surveyID):
        with self.get_session() as session:
            new_response = Response(questionID=questionID, userID=userID, response=response, surveyID=surveyID)
            session.add(new_response)
            try:
                session.commit()
            except:
                session.rollback()

    def getSurvey(self, surveyID=None, date=None):
        if(surveyID is None and date is None):
            return self.get_session().query(Survey).all()
        if(date is not None):
            return self.get_session().query(Survey).filter_by(date=date).first()
        return self.get_session().query(Survey).filter_by(surveyID=surveyID).first()
    
    def getSurveyToCompleteForUser(self, username):
        with self.get_session() as session:
            survey = (session.query(UserProgress.surveyID)
                    .filter(UserProgress.userID == username, UserProgress.survey_finished == False)
                    .first())
            if(survey is not None):
                return survey.surveyID
            else:
                return None
            
    def getSurveysToCompleteForUser(self, username):
        with self.get_session() as session:
            survey = (session.query(UserProgress.surveyID)
                    .filter(UserProgress.userID == username, UserProgress.survey_finished == False)
                    .all())
            return survey

    def inviteUserToSurvey(self, username, surveyID):
        progress = UserProgress(surveyID=surveyID, userID=username)
        with self.get_session() as session:
            try:
                session.add(progress)
                session.commit()
            except:
                session.rollback()

    def setUserFinishedSurvey(self, surveyID, userID):
        with self.get_session() as session:
            try:
                session.query(UserProgress).filter_by(userID=userID, surveyID=surveyID).update({"survey_finished":True})
                session.commit()
            except:
                session.rollback()
            

    #encryption and verification functions
    def verifyUserByPassword(self, userID, password):
        user = self.getUser(userID)

        if(user is None):
            return False

        password_bytes = password.encode('utf-8')
        if(bcrypt.checkpw(password_bytes, user.hash_salt)):
            return True
        else:
            return False
        
    def verifyUserBySession(self, userID):
        if(keyring.get_password(self.constants.keyring_service_name, self.constants.keyring_user_name) == self.getUser(userID).token):
            return True
        else:
            return False

    def openSessionToken(self, userID):
        #encoding to ensure all the random bytes can later be retrieved as keyring.get_password uses utf-8 encoding
        keyring.set_password(self.constants.keyring_service_name, self.constants.keyring_user_name, b64encode(os.urandom(32)).decode(encoding='UTF-8'))
        token = keyring.get_password(self.constants.keyring_service_name, self.constants.keyring_user_name)
        with self.get_session() as session:
            try:
                session.query(User).filter_by(userID=userID).update({"token":token})
                session.commit()
            except:
                session.rollback()

    def closeSessionToken(self):

        user = self.getUser(token=keyring.get_password(self.constants.keyring_service_name, self.constants.keyring_user_name))
        keyring.delete_password(self.constants.keyring_service_name, self.constants.keyring_user_name)
        if(user is not None):
            with self.get_session() as session:
                try:
                    session.query(User).filter_by(userID=user.userID).update({"token":None})
                    session.commit()
                except:
                    session.rollback()

    def updatePassword(self, userID, new_password):
        user = self.getUser(userID=userID)
        hashed_password = self.hashPassword(new_password)
        if(user is not None):
            self.closeSessionToken()
            
            with self.get_session() as session:
                try:
                    session.query(User).filter_by(userID=user.userID).update({"hash_salt":hashed_password})
                    session.commit()
                    self.openSessionToken(userID)
                except:
                    session.rollback()


    def hashPassword(self, password):

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        return hashed_password
    
    def hashToken(self, token):
        hashed_token = bcrypt.hashpw(token, bcrypt.gensalt())
        return hashed_token
    #######################################################################
    
    def getUser(self, userID=None, token="no_token"):
        if(token is None):
            return None
        if(token != "no_token"):
            return self.get_session().query(User).filter_by(token=token).first()
        if(userID == None):
            return self.get_session().query(User).all()
        return self.get_session().query(User).filter_by(userID=userID).first()
    
    def getCurrentUser(self):
        token = keyring.get_password(self.constants.keyring_service_name, self.constants.keyring_user_name)
        return self.getUser(token=token)
    
    def getUsersByTechnicality(self, is_technical):
        return self.get_session().query(User).filter_by(is_technical=is_technical).all()
    
    def getCategories(self):
        return self.get_session().query(Category).all()
    
    def getCategory(self, categoryID):
        return self.get_session().query(Category).filter_by(categoryID=categoryID).first()
    
    def getQuestionsForRole(self, roleID):
        return self.get_session().query(Question).options(joinedload(Question.answer), joinedload(Question.category)).join(QuestionRoleAssociation).filter(QuestionRoleAssociation.roleID == roleID).order_by(Question.questionID).all()
    
    def getQuestionsByCategory(self, categoryID = None, category_name = None):
        if(categoryID is not None):
            return self.get_session().query(Question).options(joinedload(Question.answer)).filter_by(categoryID=categoryID).order_by(Question.questionID).all()
        elif(category_name is not None):
            return self.get_session().query(Question).options(joinedload(Question.answer)).join(Category, Question.categoryID == Category.categoryID).filter(Category.name == category_name).order_by(Question.questionID).all()
    
    def getQuestions(self):
        return self.get_session().query(Question).order_by(Question.questionID).all()
    
    def getQuestion(self, qID = None, qText = None):
        if(qID is not None):
            return self.get_session().query(Question).options(joinedload(Question.answer)).filter_by(questionID=qID).first()
        elif(qText is not None):
            return self.get_session().query(Question).options(joinedload(Question.answer)).filter_by(text=qText).first()
    
    
    def getQuestionsForRoleByCategory(self, roleID, categoryID):
        return (
                self.get_session().query(Question)
                .join(QuestionRoleAssociation)
                .filter(QuestionRoleAssociation.roleID == roleID)
                .filter(Question.categoryID == categoryID)
                .options(joinedload(Question.answer))
                .order_by(Question.questionID)
                .all()
            )
    
    def getResponse(self, roleID, surveyID, questionID):
        with self.get_session() as session:
            return (
                session.query(Response)
                .join(User)
                .filter(User.roleID == roleID)
                .filter(Response.surveyID == surveyID)
                .filter(Response.questionID == questionID)
                .order_by(Response.responseID)
                .all()
            )
        
        
    def getResponsesBySurvey(self, surveyID):
        with self.get_session() as session:
            return (
                session.query(Response)
                .filter(Response.surveyID == surveyID)
                .all()
            )
        
        
    def getAnswer(self, answerID):
        with self.get_session() as session:
            return (
                session.query(Answer)
                .filter(Answer.answerID == answerID)
                .first()
            )
        
    def getAnswers(self):
        with self.get_session() as session:
            return (
                session.query(Answer)
                .order_by(Answer.answerID)
                .all()
            )
        

    def checkUsernameUnique(self, username):
        users = DatabaseManager().getUser()
        usernames = []
        for user in users:
            usernames.append(user.userID)

        for u in usernames:
            if(u == username):
                return False
            
        return True
    

class Question(DatabaseBase):
    __tablename__ = 'questions'
    questionID = Column(Integer, Sequence("question_id_seq"), primary_key=True, autoincrement=True)
    categoryID = Column(String(3), ForeignKey('categories.categoryID'))
    text = Column(String(), unique=True)
    answerID = Column(Integer, ForeignKey('answers.answerID'))
    rationale = Column(String())
    comments = Column(String())
    producer = Column(Boolean, default=False)
    answer_weights = Column(String())
    weight = Column(Integer, default=1)


    #relationship setup
    role = relationship('Role', secondary='question_role_association', back_populates='questions')
    category = relationship('Category', back_populates='questions')
    answer = relationship('Answer', back_populates='questions')
    role_specific_wording = relationship('RoleSpecificQuestionWording', back_populates='questions')
    response = relationship('Response', back_populates='questions')

    __table_args__ = (
        CheckConstraint('weight >= 0 AND weight <= 2', name='check_value_range'),
    )

class RoleSpecificQuestionWording(DatabaseBase):
    __tablename__ = 'role-specific-question-wordings'
    questionID = Column(Integer, ForeignKey('questions.questionID'), primary_key=True)
    roleID = Column(String, ForeignKey('roles.roleID'), primary_key=True)
    wording = Column(String)

    questions = relationship('Question', back_populates='role_specific_wording')
    role = relationship('Role', back_populates='role_specific_wording')

class Category(DatabaseBase):

    class RatingEnum(Enum):
        NEED = 'need'
        ATTITUDE = 'attitude'
        AWARENESS = 'awareness'

    __tablename__ = 'categories'
    categoryID = Column(String(3), primary_key=True)
    name = Column(String(), unique=True)
    rationale = Column(String())
    rating = Column(String(10))
    questions = relationship('Question', back_populates='category')

class Answer(DatabaseBase):

    class TypeEnum(Enum):
        MULTIPLE = 'multiple'
        SINGLE = 'single'
            
    __tablename__ = 'answers'
    answerID = Column(Integer, Sequence("answer_id_seq"), primary_key=True, autoincrement=True)
    answer = Column(String(), unique=True)
    type = Column(String(10))
    comments = Column(String())
    questions = relationship('Question', back_populates='answer')


class Role(DatabaseBase):
    __tablename__ = 'roles'
    roleID = Column(String(), primary_key=True)
    description = Column(String())
    questions = relationship('Question', secondary='question_role_association', back_populates='role')
    role_specific_wording = relationship('RoleSpecificQuestionWording', back_populates='role')
    user = relationship('User', back_populates='role')

class QuestionRoleAssociation(DatabaseBase):
    __tablename__ = 'question_role_association'
    questionID = Column(Integer, ForeignKey('questions.questionID'), primary_key=True)
    roleID = Column(String(), ForeignKey('roles.roleID'), primary_key=True)

class Response(DatabaseBase):
    __tablename__ = 'responses'
    responseID = Column(Integer, Sequence("response_id_seq"), primary_key=True, autoincrement=True)
    questionID = Column(Integer, ForeignKey('questions.questionID'))
    userID = Column(Integer, ForeignKey('users.userID'))
    response = Column(String())
    surveyID = Column(Integer, ForeignKey('surveys.surveyID'))
    questions = relationship('Question', back_populates='response')
    user = relationship('User', back_populates='response')
    survey = relationship('Survey', back_populates='response')

class User(DatabaseBase):
    __tablename__ = 'users'
    userID = Column(String(), primary_key=True)
    roleID = Column(String(), ForeignKey('roles.roleID'))
    hash_salt = Column(String())
    token = Column(String())
    is_technical = Column(Boolean, default=False)
    role = relationship('Role', back_populates='user')
    response = relationship('Response', back_populates='user')
    progress = relationship('UserProgress', back_populates='user')

class Survey(DatabaseBase):
    __tablename__ = 'surveys'
    surveyID = Column(Integer, Sequence('survey_id_seq'), primary_key=True, autoincrement=True)
    date = Column(Date)
    response = relationship('Response', back_populates='survey')
    progress = relationship('UserProgress', back_populates='survey')

class UserProgress(DatabaseBase):
    __tablename__ = 'user_progress'
    surveyID = Column(Integer, ForeignKey('surveys.surveyID'), primary_key=True)
    userID = Column(String, ForeignKey('users.userID'), primary_key=True)
    survey_finished = Column(Boolean, default=False)
    survey = relationship('Survey', back_populates='progress')
    user = relationship('User', back_populates='progress')

def initialise_roles(session):
    defaultRoles = DefaultRoles()
    role_list = []
    for i in range(0, len(defaultRoles.roles)):
        role_list.append(Role(roleID=defaultRoles.roles[i], description=defaultRoles.descriptions[i]))
    
    try:
        session.add_all(role_list)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()

def initialise_categories(session):
    defaultCategories = DefaultCategories()
    category_list = []

    for i in range(0, len(defaultCategories.categoryID)):
        category_list.append(Category(categoryID=defaultCategories.categoryID[i], name=defaultCategories.name[i],
                                       rationale=defaultCategories.rationale[i], rating=defaultCategories.rating[i]))

    try:
        session.add_all(category_list)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()

def initialise_answers(session):
    answer_list = []
    defaultAnswers = DefaultAnswers()
    answer_texts = defaultAnswers.answer_text

    for i in range(0,len(answer_texts)):
        if i in {2, 4, 6, 11, 12, 21, 24}:
            answer_list.append(Answer(answer=answer_texts[i], type=Answer.TypeEnum.MULTIPLE))
        else:
            answer_list.append(Answer(answer=answer_texts[i], type=Answer.TypeEnum.SINGLE))
    try:
        session.add_all(answer_list)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()


def initialise_questions(session):

    #find audiences
    ceo = session.query(Role).filter_by(roleID='CEO').first()
    cfo = session.query(Role).filter_by(roleID='CFO').first()
    cpo = session.query(Role).filter_by(roleID='CPO').first()
    ciso = session.query(Role).filter_by(roleID='CISO').first()
    cio = session.query(Role).filter_by(roleID='CIO').first()
    cto = session.query(Role).filter_by(roleID='CTO').first()
    default = [ceo, cfo, cpo, ciso, cio, cto]

    #find categories
    tdu = session.query(Category).filter_by(categoryID='TDU').first()
    iab = session.query(Category).filter_by(categoryID='IAB').first()
    spi = session.query(Category).filter_by(categoryID='SPI').first()
    sta = session.query(Category).filter_by(categoryID='STA').first()
    dsa = session.query(Category).filter_by(categoryID='DSA').first()

    #find answers
    answers = []
    for i in range(0, len(DefaultAnswers().answer_text)+1):
        answers.append(session.query(Answer).filter_by(answerID=i).first())

    defaultQuestions = DefaultQuestions()
    defaultQuestionsText = defaultQuestions.question_text
    defaultQuestionsRationale = defaultQuestions.rationale
    defaultQuestionsComments = defaultQuestions.comments

    #tdu questions
    #1
    questionsToAdd = []
    questionsToAdd.append(Question(
        text=defaultQuestionsText[0],
        role=default,
        category=tdu,
        answer=answers[3],
        rationale=defaultQuestionsRationale[0],
        comments=None,
        answer_weights="+1"
    ))
    #2
    questionsToAdd.append(Question(
        text=defaultQuestionsText[1],
        role=default,
        category=tdu,
        answer=answers[4],
        rationale=defaultQuestionsRationale[1],
        comments=defaultQuestionsComments[0],
        answer_weights="5,4,3,1,0"
    ))
    #3
    questionsToAdd.append(Question(
        text=defaultQuestionsText[2],
        role=default,
        category=tdu,
        answer=answers[3],
        rationale=defaultQuestionsRationale[2],
        comments=None,
        answer_weights="+1"
    ))
    #4
    questionsToAdd.append(Question(
        text=defaultQuestionsText[3],
        role=default,
        category=tdu,
        answer=answers[5],
        rationale=defaultQuestionsRationale[3],
        comments=defaultQuestionsComments[1],
        answer_weights="+1"
    ))
    #5
    questionsToAdd.append(Question(
        text=defaultQuestionsText[4],
        role=default,
        category=tdu,
        answer=answers[6],
        rationale=defaultQuestionsRationale[4],
        comments=None,
        answer_weights="1,2,3,5,0"
    ))
    #6
    questionsToAdd.append(Question(
        text=defaultQuestionsText[5],
        role=[ciso, cio, cto],
        category=tdu,
        answer=answers[1],
        rationale=defaultQuestionsRationale[5],
        comments=defaultQuestionsComments[2],
        answer_weights="1,2,3,4,5"
    ))

    #iab questions
    #7
    questionsToAdd.append(Question(
        text=defaultQuestionsText[6],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[2],
        rationale=defaultQuestionsRationale[6],
        comments=defaultQuestionsComments[3],
        answer_weights="5,4,3,2,1,0"
    ))
    #8
    questionsToAdd.append(Question(
        text=defaultQuestionsText[7],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[1],
        rationale=defaultQuestionsRationale[7],
        comments=defaultQuestionsComments[3],
        answer_weights="5,4,3,2,1"
    ))
    #9
    questionsToAdd.append(Question(
        text=defaultQuestionsText[8],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[7],
        rationale=defaultQuestionsRationale[8],
        comments=defaultQuestionsComments[3],
        answer_weights="+1"
    ))
    #10
    questionsToAdd.append(Question(
        text=defaultQuestionsText[9],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[7],
        rationale=defaultQuestionsRationale[9],
        comments=None,
        answer_weights="+1"
    ))
    #11
    questionsToAdd.append(Question(
        text=defaultQuestionsText[10],
        role=[ciso, cio, cto],
        category=iab,
        answer=answers[8],
        rationale=defaultQuestionsRationale[10],
        comments=defaultQuestionsComments[4],
        answer_weights="1,2,3,5,0"
    ))
    #12
    questionsToAdd.append(Question(
        text=defaultQuestionsText[11],
        role=[ciso, cio, cto],
        category=iab,
        answer=answers[8],
        rationale=defaultQuestionsRationale[11],
        comments=defaultQuestionsComments[5],
        answer_weights="1,2,3,5,0"
    ))
    #13
    questionsToAdd.append(Question(
        text=defaultQuestionsText[12],
        role=[ciso, cio, cto],
        category=iab,
        answer=answers[1],
        rationale=None,
        comments=defaultQuestionsComments[6],
        answer_weights="5,4,3,2,1"
    ))
    #14
    questionsToAdd.append(Question(
        text=defaultQuestionsText[13],
        role=[ceo, ciso, cio, cto],
        category=iab,
        answer=answers[9],
        rationale=defaultQuestionsRationale[12],
        comments=defaultQuestionsComments[7],
        producer=True,
        answer_weights="1,2,3,4,5"
    ))
    #15
    questionsToAdd.append(Question(
        text=defaultQuestionsText[14],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[10],
        rationale=defaultQuestionsRationale[13],
        comments=defaultQuestionsComments[8],
        answer_weights="1,2,3,4,5"
    ))
    #16
    questionsToAdd.append(Question(
        text=defaultQuestionsText[15],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[2],
        rationale=defaultQuestionsRationale[14],
        comments=defaultQuestionsComments[8],
        answer_weights="5,4,3,2,1,0"
    ))

    #spi questions
    #17
    questionsToAdd.append(Question(
        text=defaultQuestionsText[16],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[15],
        comments=defaultQuestionsComments[9],
        answer_weights="5,4,3,2,1"
    ))
    #18
    questionsToAdd.append(Question(
        text=defaultQuestionsText[17],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[16],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #19
    questionsToAdd.append(Question(
        text=defaultQuestionsText[18],
        role=default,
        category=spi,
        answer=answers[11],
        rationale=defaultQuestionsRationale[17],
        comments=None,
        answer_weights="1,2,3,4,5"
    ))
    #20
    questionsToAdd.append(Question(
        text=defaultQuestionsText[19],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[18],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #21
    questionsToAdd.append(Question(
        text=defaultQuestionsText[20],
        role=default,
        category=spi,
        answer=answers[12],
        rationale=defaultQuestionsRationale[19],
        comments=None,
        answer_weights="+1"
    ))
    #22
    questionsToAdd.append(Question(
        text=defaultQuestionsText[21],
        role=default,
        category=spi,
        answer=answers[13],
        rationale=defaultQuestionsRationale[20],
        comments=defaultQuestionsComments[10],
        answer_weights="-1"
    ))
    #23
    questionsToAdd.append(Question(
        text=defaultQuestionsText[22],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[21],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #24
    questionsToAdd.append(Question(
        text=defaultQuestionsText[23],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[22],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #25
    questionsToAdd.append(Question(
        text=defaultQuestionsText[24],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[23],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #26
    questionsToAdd.append(Question(
        text=defaultQuestionsText[25],
        role=default,
        category=spi,
        answer=answers[14],
        rationale=defaultQuestionsRationale[24],
        comments=defaultQuestionsComments[11],
        answer_weights="1,2,3,5"
    ))

    #sta questions
    #27
    questionsToAdd.append(Question(
        text=defaultQuestionsText[26],
        role=default,
        category=sta,
        answer=answers[12],
        rationale=defaultQuestionsRationale[25],
        comments=defaultQuestionsComments[12],
        answer_weights="+1"
    ))
    #28
    questionsToAdd.append(Question(
        text=defaultQuestionsText[27],
        role=default,
        category=sta,
        answer=answers[15],
        rationale=defaultQuestionsRationale[26],
        comments=None,
        answer_weights="1,2,3,5"
    ))
    #29
    questionsToAdd.append(Question(
        text=defaultQuestionsText[28],
        role=default,
        category=sta,
        answer=answers[15],
        rationale=defaultQuestionsRationale[27],
        comments=None,
        answer_weights="1,2,3,5"
    ))
    #30
    questionsToAdd.append(Question(
        text=defaultQuestionsText[29],
        role=default,
        category=sta,
        answer=answers[16],
        rationale=defaultQuestionsRationale[28],
        comments=None,
        answer_weights="5,3,1"
    ))
    #31
    questionsToAdd.append(Question(
        text=defaultQuestionsText[30],
        role=default,
        category=sta,
        answer=answers[17],
        rationale=defaultQuestionsRationale[29],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #32
    questionsToAdd.append(Question(
        text=defaultQuestionsText[31],
        role=default,
        category=sta,
        answer=answers[18],
        rationale=defaultQuestionsRationale[30],
        comments=defaultQuestionsComments[13],
        answer_weights="1,3,5"
    ))
    #33
    questionsToAdd.append(Question(
        text=defaultQuestionsText[32],
        role=default,
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[31],
        comments=None,
        answer_weights="5,4,3,2,1"
    ))
    #34
    questionsToAdd.append(Question(
        text=defaultQuestionsText[33],
        role=[ciso, cio, cto],
        category=sta,
        answer=answers[19],
        rationale=defaultQuestionsRationale[32],
        comments=None,
        answer_weights="1,3,5,0"
    ))
    #35
    questionsToAdd.append(Question(
        text=defaultQuestionsText[34],
        role=[ceo, cfo, ciso, cio, cto],
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[33],
        comments=defaultQuestionsComments[14],
        producer=True,
        answer_weights="5,4,3,2,1"
    ))
    #36
    questionsToAdd.append(Question(
        text=defaultQuestionsText[35],
        role=[ceo, cfo, ciso, cio, cto],
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[34],
        comments=defaultQuestionsComments[14],
        producer=True,
        answer_weights="5,4,3,2,1"
    ))
    #37
    questionsToAdd.append(Question(
        text=defaultQuestionsText[36],
        role=[ceo, cfo, ciso, cio, cto],
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[35],
        comments=defaultQuestionsComments[14],
        producer=True,
        answer_weights="5,4,3,2,1"
    ))
    #dsa questions
    #38
    questionsToAdd.append(Question(
        text=defaultQuestionsText[37],
        role=default,
        category=dsa,
        answer=answers[20],
        rationale=defaultQuestionsRationale[36],
        comments=defaultQuestionsComments[15],
        answer_weights="5,3,2,1"
    ))
    #39
    questionsToAdd.append(Question(
        text=defaultQuestionsText[38],
        role=default,
        category=dsa,
        answer=answers[1],
        rationale=defaultQuestionsRationale[37],
        comments=defaultQuestionsComments[16],
        answer_weights="5,4,3,2,1"
    ))
    #40
    questionsToAdd.append(Question(
        text=defaultQuestionsText[39],
        role=default,
        category=dsa,
        answer=answers[1],
        rationale=defaultQuestionsRationale[38],
        comments=defaultQuestionsComments[16],
        answer_weights="5,4,3,2,1"
    ))
    #41
    questionsToAdd.append(Question(
        text=defaultQuestionsText[40],
        role=default,
        category=dsa,
        answer=answers[21],
        rationale=defaultQuestionsRationale[39],
        comments=defaultQuestionsComments[17],
        answer_weights="5,3,2,1"
    ))
    #42
    questionsToAdd.append(Question(
        text=defaultQuestionsText[41],
        role=default,
        category=dsa,
        answer=answers[22],
        rationale=defaultQuestionsRationale[40],
        comments=defaultQuestionsComments[18],
        answer_weights="-1"
    ))
    #43
    questionsToAdd.append(Question(
        text=defaultQuestionsText[42],
        role=default,
        category=dsa,
        answer=answers[13],
        rationale=defaultQuestionsRationale[41],
        comments=defaultQuestionsComments[19],
        answer_weights="-1"
    ))
    #44
    questionsToAdd.append(Question(
        text=defaultQuestionsText[43],
        role=[ceo, ciso, cio, cto],
        category=dsa,
        answer=answers[23],
        rationale=defaultQuestionsRationale[42],
        comments=defaultQuestionsComments[20],
        producer=True,
        answer_weights="5,1,0,0"
    ))
    #45
    questionsToAdd.append(Question(
        text=defaultQuestionsText[44],
        role=[ceo, ciso, cio, cto],
        category=dsa,
        answer=answers[24],
        rationale=defaultQuestionsRationale[43],
        comments=defaultQuestionsComments[21],
        producer=True,
        answer_weights="5,1,3,0"
    ))
    #46
    questionsToAdd.append(Question(
        text=defaultQuestionsText[45],
        role=[ceo, ciso, cio, cto],
        category=dsa,
        answer=answers[25],
        rationale=defaultQuestionsRationale[44],
        comments=defaultQuestionsComments[21],
        producer=True,
        answer_weights="-1"
    ))

    try:
        session.add_all(questionsToAdd)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()