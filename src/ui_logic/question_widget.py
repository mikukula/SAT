import os
from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi

class QuestionWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui_design', 'question_widget.ui'), self)