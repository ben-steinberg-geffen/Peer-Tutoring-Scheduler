from data import load_student_data, load_tutor_data
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


student_df = load_student_data()
tutor_df = load_tutor_data()

class Student:
    def __init__(self, name, grade, availability, courses):
        self.name = name
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matches = []
        self.matched_tutor = None

class Tutor:
    def __init__(self, name, grade, availability, courses):
        self.name = name
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matches = []
        self.matched_student = []

students = []
tutors = []

for index, row in student_df.iterrows():
    students.append(Student(row['name'], row['grade'], row['availability'], row['courses']))

for index, row in tutor_df.iterrows():
    tutors.append(Tutor(row['name'], row['grade'], row['availability'], row['courses']))

def match_students_tutors(students, tutors):
    for student in students:
        for tutor in tutors:
            if set(student.courses).intersection(set(tutor.courses)) == set(student.courses):
                if set(student.availability).intersection(set(tutor.availability)):
                    student.matches.append(tutor)
                    tutor.matches.append(student)
    return students, tutors
                    
students, tutors = match_students_tutors(students, tutors)