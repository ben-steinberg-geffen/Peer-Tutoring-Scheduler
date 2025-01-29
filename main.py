from data import load_student_data, load_tutor_data
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

student_df = load_student_data()
tutor_df = load_tutor_data()

class student:
    def __init__(self, name, grade, availability, courses):
        self.name = name
        self.grade = grade
        self.availability = availability
        self.courses = courses

class tutor:
    def __init__(self, name, grade, availability, courses):
        self.name = name
        self.grade = grade
        self.availability = availability
        self.courses = courses
