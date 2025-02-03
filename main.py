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
        self.matched_tutors = []
        self.final_tutor = None
        self.matched = False

class Tutor:
    def __init__(self, name, grade, availability, courses):
        self.name = name
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matched_students = []
        self.final_students = []

students = []
tutors = []

for index, row in student_df.iterrows():
    students.append(Student(row['name'], row['grade'], row['availability'], row['courses']))

for index, row in tutor_df.iterrows():
        tutors.append(Tutor(row['name'], row['grade'], row['availability'], row['courses']))

def get_time_intersection(student, tutor):
    times = []
    for time in student.availability: 
        if time in tutor.availability: 
            times.append(time) 

def match_students_tutors(students, tutors):
    for student in students:
        for tutor in tutors:
            if set(student.courses).intersection(set(tutor.courses)) == set(student.courses):
                if set(student.availability).intersection(set(tutor.availability)):
                    student.matched_tutors.append(tutor)
                    tutor.matched_students.append(student)
    return students, tutors



def select_unassigned_var(students):
    for student in students: 
        if student.matched_tutor == None: 

            return student.matched_tutors[0]
        
    return False

def backtrack(students, tutors):
    if check_completion(students, tutors):
        return students, tutors
    
    var = select_unassigned_var(students)
    # Assign tutors in a list, if they don't work then backtrack
    for student in students: 
        pass
    pass

def check_constraints(students, tutors):
    # Tutors can't teach two tutors at the same time
    # Tutors and students must have the same classes
    # It must be at the same time as well
    # Tutors with no students take priority over students with tutors

    for tutor in tutors: 
        for student in students: 
            times = get_time_intersection(student, tutor)
            # We want to see even if a tutor teaches multiple people, that they 
            # can still work with everyone at different times.
            
    pass

def check_completion(students, tutors):
    for student in students: 
        if student.matched_tutor == None:
            return False
        
    # If all of them are matched up, it then checks the constraint to see if it works
    return check_constraints(students, tutors)

students, tutors = match_students_tutors(students, tutors)