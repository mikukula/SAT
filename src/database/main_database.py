from sqlalchemy import create_engine, Column, Boolean, Integer, String, Sequence, ForeignKey, Enum, CheckConstraint, Date
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from database.default_database_details import *
from constants import Constants
import bcrypt

DatabaseBase = declarative_base()
mainDatabaseConstants = Constants()

class DatabaseManager:

    def __init__(self, db_url="sqlite:///" + mainDatabaseConstants.getDatabasePath() + "/" + mainDatabaseConstants.database_name):
        self.engine = create_engine(db_url, echo=True)
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


    def addUser(self, userID, roleID, password, admin_rights=False):
        hashed_password, salt = self.hashPassword(password)
        user = User(userID=userID, roleID=roleID, hash=hashed_password, salt=salt, admin_rights=admin_rights)
        session = self.get_session()

        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    def hashPassword(self, password):
        salt = bcrypt.gensalt()

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed_password, salt
    
    
    def getUser(self, userID=None):
        if(userID == None):
            return self.get_session().query(User).all()
        return self.get_session().query(User).filter_by(userID=userID).first()

class Question(DatabaseBase):
    __tablename__ = 'questions'
    questionID = Column(Integer, Sequence("question_id_seq"), primary_key=True, autoincrement=True)
    categoryID = Column(String(3), ForeignKey('categories.categoryID'))
    text = Column(String(), unique=True)
    answerID = Column(Integer, ForeignKey('answers.answerID'))
    rationale = Column(String())
    comments = Column(String())
    producer = Column(Boolean, default=False)
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
    questions = relationship('Question', back_populates='response')
    user = relationship('User', back_populates='response')
    survey = relationship('Survey', back_populates='response')

class User(DatabaseBase):
    __tablename__ = 'users'
    userID = Column(String(), primary_key=True)
    roleID = Column(String(), ForeignKey('roles.roleID'))
    salt = Column(String())
    hash = Column(String())
    admin_rights = Column(Boolean, default=False)
    role = relationship('Role', back_populates='user')
    response = relationship('Response', back_populates='user')

class Survey(DatabaseBase):
    __tablename__ = 'surveys'
    surveyID = Column(Integer, Sequence('survey_id_seq'), primary_key=True, autoincrement=True)
    date = Column(Date)
    responseID = Column(Integer, ForeignKey('responses.responseID'))
    response = relationship('Response', back_populates='survey')

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
        category_list.append(Category(categoryID=defaultCategories.categoryID[i], name=defaultCategories.name[i], rationale=defaultCategories.rationale[i], rating=defaultCategories.rating[i]))

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
        if i in {2, 6, 11, 12, 21, 22, 25}:
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
        comments=None
    ))
    #2
    questionsToAdd.append(Question(
        text=defaultQuestionsText[1],
        role=default,
        category=tdu,
        answer=answers[4],
        rationale=defaultQuestionsRationale[1],
        comments=defaultQuestionsComments[0]
    ))
    #3
    questionsToAdd.append(Question(
        text=defaultQuestionsText[2],
        role=default,
        category=tdu,
        answer=answers[3],
        rationale=defaultQuestionsRationale[2],
        comments=None
    ))
    #4
    questionsToAdd.append(Question(
        text=defaultQuestionsText[3],
        role=default,
        category=tdu,
        answer=answers[5],
        rationale=defaultQuestionsRationale[3],
        comments=defaultQuestionsComments[1]
    ))
    #5
    questionsToAdd.append(Question(
        text=defaultQuestionsText[4],
        role=default,
        category=tdu,
        answer=answers[6],
        rationale=defaultQuestionsRationale[4],
        comments=None
    ))
    #6
    questionsToAdd.append(Question(
        text=defaultQuestionsText[5],
        role=[ciso, cio, cto],
        category=tdu,
        answer=answers[1],
        rationale=defaultQuestionsRationale[5],
        comments=defaultQuestionsComments[2]
    ))

    #iab questions
    #1
    questionsToAdd.append(Question(
        text=defaultQuestionsText[6],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[2],
        rationale=defaultQuestionsRationale[6],
        comments=defaultQuestionsComments[3]
    ))
    #2
    questionsToAdd.append(Question(
        text=defaultQuestionsText[7],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[1],
        rationale=defaultQuestionsRationale[7],
        comments=defaultQuestionsComments[3]
    ))
    #3
    questionsToAdd.append(Question(
        text=defaultQuestionsText[8],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[7],
        rationale=defaultQuestionsRationale[8],
        comments=defaultQuestionsComments[3]
    ))
    #4
    questionsToAdd.append(Question(
        text=defaultQuestionsText[9],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[7],
        rationale=defaultQuestionsRationale[9],
        comments=None
    ))
    #5
    questionsToAdd.append(Question(
        text=defaultQuestionsText[10],
        role=[ciso, cio, cto],
        category=iab,
        answer=answers[8],
        rationale=defaultQuestionsRationale[10],
        comments=defaultQuestionsComments[4]
    ))
    #6
    questionsToAdd.append(Question(
        text=defaultQuestionsText[11],
        role=[ciso, cio, cto],
        category=iab,
        answer=answers[8],
        rationale=defaultQuestionsRationale[11],
        comments=defaultQuestionsComments[5]
    ))
    #7
    questionsToAdd.append(Question(
        text=defaultQuestionsText[12],
        role=[ciso, cio, cto],
        category=iab,
        answer=answers[1],
        rationale=None,
        comments=defaultQuestionsComments[6]
    ))
    #8
    questionsToAdd.append(Question(
        text=defaultQuestionsText[13],
        role=[ceo, ciso, cio, cto],
        category=iab,
        answer=answers[9],
        rationale=defaultQuestionsRationale[12],
        comments=defaultQuestionsComments[7],
        producer=True
    ))
    #9
    questionsToAdd.append(Question(
        text=defaultQuestionsText[14],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[10],
        rationale=defaultQuestionsRationale[13],
        comments=defaultQuestionsComments[8]
    ))
    #10
    questionsToAdd.append(Question(
        text=defaultQuestionsText[15],
        role=[ceo, cfo, ciso, cio, cto],
        category=iab,
        answer=answers[2],
        rationale=defaultQuestionsRationale[14],
        comments=defaultQuestionsComments[8]
    ))

    #spi questions
    #1
    questionsToAdd.append(Question(
        text=defaultQuestionsText[16],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[15],
        comments=defaultQuestionsComments[9]
    ))
    #2
    questionsToAdd.append(Question(
        text=defaultQuestionsText[17],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[16],
        comments=None
    ))
    #3
    questionsToAdd.append(Question(
        text=defaultQuestionsText[18],
        role=default,
        category=spi,
        answer=answers[11],
        rationale=defaultQuestionsRationale[17],
        comments=None
    ))
    #4
    questionsToAdd.append(Question(
        text=defaultQuestionsText[19],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[18],
        comments=None
    ))
    #5
    questionsToAdd.append(Question(
        text=defaultQuestionsText[20],
        role=default,
        category=spi,
        answer=answers[12],
        rationale=defaultQuestionsRationale[19],
        comments=None
    ))
    #6
    questionsToAdd.append(Question(
        text=defaultQuestionsText[21],
        role=default,
        category=spi,
        answer=answers[13],
        rationale=defaultQuestionsRationale[20],
        comments=defaultQuestionsComments[10]
    ))
    #7
    questionsToAdd.append(Question(
        text=defaultQuestionsText[22],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[21],
        comments=None
    ))
    #8
    questionsToAdd.append(Question(
        text=defaultQuestionsText[23],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[22],
        comments=None
    ))
    #9
    questionsToAdd.append(Question(
        text=defaultQuestionsText[24],
        role=default,
        category=spi,
        answer=answers[1],
        rationale=defaultQuestionsRationale[23],
        comments=None
    ))
    #10
    questionsToAdd.append(Question(
        text=defaultQuestionsText[25],
        role=default,
        category=spi,
        answer=answers[14],
        rationale=defaultQuestionsRationale[24],
        comments=defaultQuestionsComments[11]
    ))

    #sta questions
    #1
    questionsToAdd.append(Question(
        text=defaultQuestionsText[26],
        role=default,
        category=sta,
        answer=answers[12],
        rationale=defaultQuestionsRationale[25],
        comments=defaultQuestionsComments[12]
    ))
    #2
    questionsToAdd.append(Question(
        text=defaultQuestionsText[27],
        role=default,
        category=sta,
        answer=answers[15],
        rationale=defaultQuestionsRationale[26],
        comments=None
    ))
    #3
    questionsToAdd.append(Question(
        text=defaultQuestionsText[28],
        role=default,
        category=sta,
        answer=answers[15],
        rationale=defaultQuestionsRationale[27],
        comments=None
    ))
    #4
    questionsToAdd.append(Question(
        text=defaultQuestionsText[29],
        role=default,
        category=sta,
        answer=answers[16],
        rationale=defaultQuestionsRationale[28],
        comments=None
    ))
    #5
    questionsToAdd.append(Question(
        text=defaultQuestionsText[30],
        role=default,
        category=sta,
        answer=answers[17],
        rationale=defaultQuestionsRationale[29],
        comments=None
    ))
    #6
    questionsToAdd.append(Question(
        text=defaultQuestionsText[31],
        role=default,
        category=sta,
        answer=answers[18],
        rationale=defaultQuestionsRationale[30],
        comments=defaultQuestionsComments[13]
    ))
    #7
    questionsToAdd.append(Question(
        text=defaultQuestionsText[32],
        role=default,
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[31],
        comments=None
    ))
    #8
    questionsToAdd.append(Question(
        text=defaultQuestionsText[33],
        role=[ciso, cio, cto],
        category=sta,
        answer=answers[19],
        rationale=defaultQuestionsRationale[32],
        comments=None
    ))
    #9
    questionsToAdd.append(Question(
        text=defaultQuestionsText[34],
        role=[ceo, cfo, ciso, cio, cto],
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[33],
        comments=defaultQuestionsComments[14],
        producer=True
    ))
    #10
    questionsToAdd.append(Question(
        text=defaultQuestionsText[35],
        role=[ceo, cfo, ciso, cio, cto],
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[34],
        comments=defaultQuestionsComments[14],
        producer=True
    ))
    #11
    questionsToAdd.append(Question(
        text=defaultQuestionsText[36],
        role=[ceo, cfo, ciso, cio, cto],
        category=sta,
        answer=answers[1],
        rationale=defaultQuestionsRationale[35],
        comments=defaultQuestionsComments[14],
        producer=True
    ))
    #dsa questions
    #1
    questionsToAdd.append(Question(
        text=defaultQuestionsText[37],
        role=default,
        category=dsa,
        answer=answers[20],
        rationale=defaultQuestionsRationale[36],
        comments=defaultQuestionsComments[15]
    ))
    #2
    questionsToAdd.append(Question(
        text=defaultQuestionsText[38],
        role=default,
        category=dsa,
        answer=answers[1],
        rationale=defaultQuestionsRationale[37],
        comments=defaultQuestionsComments[16]
    ))
    #3
    questionsToAdd.append(Question(
        text=defaultQuestionsText[39],
        role=default,
        category=dsa,
        answer=answers[1],
        rationale=defaultQuestionsRationale[38],
        comments=defaultQuestionsComments[16]
    ))
    #4
    questionsToAdd.append(Question(
        text=defaultQuestionsText[40],
        role=default,
        category=dsa,
        answer=answers[21],
        rationale=defaultQuestionsRationale[39],
        comments=defaultQuestionsComments[17]
    ))
    #5
    questionsToAdd.append(Question(
        text=defaultQuestionsText[41],
        role=default,
        category=dsa,
        answer=answers[22],
        rationale=defaultQuestionsRationale[40],
        comments=defaultQuestionsComments[18]
    ))
    #6
    questionsToAdd.append(Question(
        text=defaultQuestionsText[42],
        role=default,
        category=dsa,
        answer=answers[13],
        rationale=defaultQuestionsRationale[41],
        comments=defaultQuestionsComments[19]
    ))
    #7
    questionsToAdd.append(Question(
        text=defaultQuestionsText[43],
        role=[ceo, ciso, cio, cto],
        category=dsa,
        answer=answers[23],
        rationale=defaultQuestionsRationale[42],
        comments=defaultQuestionsComments[20],
        producer=True
    ))
    #8
    questionsToAdd.append(Question(
        text=defaultQuestionsText[44],
        role=[ceo, ciso, cio, cto],
        category=dsa,
        answer=answers[24],
        rationale=defaultQuestionsRationale[43],
        comments=defaultQuestionsComments[21],
        producer=True
    ))
    #9
    questionsToAdd.append(Question(
        text=defaultQuestionsText[45],
        role=[ceo, ciso, cio, cto],
        category=dsa,
        answer=answers[25],
        rationale=defaultQuestionsRationale[44],
        comments=defaultQuestionsComments[21],
        producer=True
    ))

    try:
        session.add_all(questionsToAdd)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()