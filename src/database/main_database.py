from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from default_database_details import *

DatabaseBase = declarative_base()

class DatabaseManager:

    def __init__(self, db_url='sqlite:///SATDatabase.db'):
        self.engine = create_engine(db_url, echo=True)
        self.Base = DatabaseBase
        self.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()

    def create_tables(self):
        self.Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

class Question(DatabaseBase):
    __tablename__ = 'questions'
    questionID = Column(Integer, Sequence("question_id_seq"), primary_key=True, autoincrement=True)
    roleID = Column(Integer, ForeignKey('roles.roleID'))
    categoryID = Column(String(3), ForeignKey('categories.categoryID'))
    text = Column(String())
    answerID = Column(Integer, ForeignKey('answers.answerID'))
    rationale = Column(String())
    comments = Column(String())
    weight = Column(Integer)

    #relationship setup
    role = relationship('Role', back_populates='questions')
    category = relationship('Category', back_populates='questions')
    answer = relationship('Answer', back_populates='questions')

    __table_args__ = (
        CheckConstraint('weight >= 0 AND weight <= 2', name='check_value_range'),
    )

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
    answerID = Column(Integer, Sequence("response_id_seq"), primary_key=True, autoincrement=True)
    answer = Column(String(), unique=True)
    type = Column(String(10))
    comments = Column(String())
    questions = relationship('Question', back_populates='answer')


class Role(DatabaseBase):
    __tablename__ = 'roles'
    roleID = Column(String(), primary_key=True)
    description = Column(String())
    questions = relationship('Question', back_populates='role')

def initialise_roles(session):
    defaultRoles = DefaultRoles()
    role_list = []
    for i in range(0, len(defaultRoles.roles)):
        role_list.append(Role(roleID=defaultRoles.roles[i], description=defaultRoles.descriptions[i]))
    session.add_all(role_list)
    session.commit()

def initialise_categories(session):
    defaultCategories = DefaultCategories()
    category_list = []

    for i in range(0, len(defaultCategories.categoryID)):
        category_list.append(Category(categoryID=defaultCategories.categoryID[i], name=defaultCategories.name[i], rationale=defaultCategories.rationale[i], rating=defaultCategories.rating[i]))

    session.add_all(category_list)
    session.commit()

def initialise_answers(session):
    answer_list = []
    defaultAnswers = DefaultAnswers()
    answer_texts = defaultAnswers.answer_text

    for i in range(0,len(answer_texts)):
        if i in {2, 6, 11, 12, 21, 22, 25}:
            answer_list.append(Answer(answer=answer_texts[i], type=Answer.TypeEnum.MULTIPLE))
        else:
            answer_list.append(Answer(answer=answer_texts[i], type=Answer.TypeEnum.SINGLE))

    session.add_all(answer_list)
    session.commit()












def initialise_database():

    manager = DatabaseManager()
    session = manager.get_session()
 
    initialise_roles(session)

    initialise_categories(session)

    initialise_answers(session)

    # Sample Questions
    #question1 = Question(text='Sample Question 1', role=admin_role, category=need_category, answer=multiple_answer, weight=1)
    #question2 = Question(text='Sample Question 2', role=user_role, category=attitude_category, answer=single_answer, weight=2)
    #session.add_all([question1, question2])
    #session.commit()

    #session.close()

initialise_database()
