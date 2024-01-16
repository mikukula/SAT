from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

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
    answer = Column(String())
    type = Column(String(10))
    comments = Column(String())
    questions = relationship('Question', back_populates='answer')


class Role(DatabaseBase):
    __tablename__ = 'roles'
    roleID = Column(Integer, Sequence("role_id_seq"), primary_key=True, autoincrement=True)
    name = Column(String())
    description = Column(String())
    questions = relationship('Question', back_populates='role')

def initialise_database():

    manager = DatabaseManager()
    session = manager.get_session()

    admin_role = Role(name='Admin', description='Administrator role')
    user_role = Role(name='User', description='Regular user role')
    session.add_all([admin_role, user_role])
    session.commit()

    # Sample Categories
    need_category = Category(categoryID='NEE', name='Need', rationale='Sample rationale for need', rating=Category.RatingEnum.NEED)
    attitude_category = Category(categoryID='ATT', name='Attitude', rationale='Sample rationale for attitude', rating=Category.RatingEnum.ATTITUDE)
    awareness_category = Category(categoryID='AWA', name='Awareness', rationale='Sample rationale for awareness', rating=Category.RatingEnum.AWARENESS)
    session.add_all([need_category, attitude_category, awareness_category])
    session.commit()

    # Sample Answers
    multiple_answer = Answer(answer='Multiple Choice', type=Answer.TypeEnum.MULTIPLE)
    single_answer = Answer(answer='Single Choice', type=Answer.TypeEnum.SINGLE)
    session.add_all([multiple_answer, single_answer])
    session.commit()

    # Sample Questions
    question1 = Question(text='Sample Question 1', role=admin_role, category=need_category, answer=multiple_answer, weight=1)
    question2 = Question(text='Sample Question 2', role=user_role, category=attitude_category, answer=single_answer, weight=2)
    session.add_all([question1, question2])
    session.commit()

    session.close()

initialise_database()
