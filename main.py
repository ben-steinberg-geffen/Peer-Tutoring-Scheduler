from data import load_student_data, load_tutor_data
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

student_df = load_student_data()
tutor_df = load_tutor_data()

assignment = {}

class Student:
    def __init__(self, name, grade, availability, courses):
        self.name = name
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matched_tutors = []
        self.index = 0 
        self.final_tutor = None

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

def get_time_x_intersection(student_a, student_b):
    times = []
    for time in student_a.availability:
        if time not in student_b.availability: 
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
        if student.final_tutor == None: 
            
            index = student.index

            student.index += 1
            student.index = student.index % (len(student.matched_tutors) - 1)
            return student.matched_tutors[index]
        
            # This should change the index of the student every time and rotate between them.

    return False

def backtrack(assignment, students, tutors):
    if check_completion(students, tutors):
        return assignment
        # After this, we need to assign the tutors to the students
    
    var = select_unassigned_var(students)
    # Assign tutors in a list, if they don't work then backtrack
    for student in students: 
        if check_constraints(assignment, students, tutors):
            assignment[var] = student
            result = backtrack(students, tutors)
            if result != False:
                return result
            
            del assignment[var]
    
    return False

def check_constraints(assignment, students, tutors):
    '''
    Tutors can't teach two tutors at the same time *
    Tutors and students must have the same classes
    It must be at the same time as well
    Tutors and students will have the ability to request a change in tutors 
    Tutors with no students take priority over students with tutors * 
    * are the ones that we need to handle here
    '''
    
    for tutor in assignment.values():
        student_array = []
        possible_students = len(tutor.availability)

        for student in assignment.keys():
            if assignment[student] == tutor: 
                # This would mean they have the same tutor 
                if possible_students < len(student_array):
                    student_array.append(student)

        # From here check the times
        for student in student_array: 
            pass
        


    return True # CHANGE LATER 

def check_completion(assignment, students, tutors):
    if check_constraints(assignment, students, tutors) and select_unassigned_var(students) == False:
        return True 
    return False

students, tutors = match_students_tutors(students, tutors)