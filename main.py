from data import load_student_data, load_tutor_data
import pandas as pd
import sys

sys.setrecursionlimit(1000)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


student_df = load_student_data()
tutor_df = load_tutor_data()

student_assignment = {}
time_assignment = {} # Lines up student with their time

class Student:
    def __init__(self, name, email, grade, availability, courses):
        self.name = name
        self.email = email
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matched_tutors = []
        self.tutor_index = 0 
        self.time_index = 0
        self.final_tutor = None
        self.final_time = None

class Tutor:
    def __init__(self, name, email, grade, availability, courses):
        self.name = name
        self.email = email
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matched_students = []
        self.final_students = {} # This aligns the students with the time slot
        
students = []
tutors = []

for index, row in student_df.iterrows():
    students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses']))

for index, row in tutor_df.iterrows():
    tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses']))

def get_time_intersection(student, tutor):
    times = []
    for time in student.availability: 
        if time in tutor.availability: 
            times.append(time) 

    return times

def match_students_tutors(students, tutors):
    for student in students:
        for tutor in tutors:
            if set(student.courses).intersection(set(tutor.courses)) == set(student.courses):
                if set(student.availability).intersection(set(tutor.availability)):
                    student.matched_tutors.append(tutor)
                    tutor.matched_students.append(student)
    return students, tutors

def select_unassigned_tutor(students):
    for student in students: 
        if student.final_tutor == None: 
            if not student.matched_tutors:
                continue

            index = student.tutor_index

            temp_index = student.tutor_index + 1 # This is affecting index somehow and returning the wrong tutor
            
            if temp_index > len(student.matched_tutors) - 1:
                student.tutor_index = 0

            return student.matched_tutors[index], student
        
    return False

def select_unassigned_time(tutor_var, student_var):
    index = student_var.time_index

    times = get_time_intersection(student_var, tutor_var)

    selected_time = times[index]

    student_var.time_index += 1
    if student_var.time_index > len(times) - 1:
        student_var.time_index = 0

    return selected_time
        
def backtrack(student_assignment, time_assignment, students, tutors):
    if check_completion(student_assignment, time_assignment, students, tutors):
        return student_assignment, time_assignment
    
    tutor_var, student_var = select_unassigned_tutor(students) ## iter1 is Raina Mahtabi, Ben Steinberg
    time_var = select_unassigned_time(tutor_var, student_var) ## iter1 Wednesday: H Block

    student_assignment[student_var] = tutor_var
    student_var.final_tutor = tutor_var
    time_assignment[student_var] = time_var
    student_var.final_time = time_var
    tutor_var.final_students[student_var] = time_var

    if check_constraints(student_assignment, time_assignment):
        result = backtrack(student_assignment, time_assignment, students, tutors)

        if result:
            return result
        
    student_var.final_tutor = None
    student_var.final_time = None
    del student_assignment[student_var]
    del time_assignment[student_var]
    return False

def check_constraints(student_assignment, time_assignment):
    '''
    Tutors can't teach two tutors at the same time slot*
    # Tutors and students must have the same classes
    # It must be at the same time as well
    Tutors and students will have the ability to request a change in tutors 
    # Tutors with no students take priority over students with tutors * 
    * are the ones that we need to handle here
    '''
    
    for tutor in student_assignment.values():
        student_array = []
        possible_students = len(tutor.availability)

        for student in student_assignment.keys():
            if student_assignment[student] == tutor: 
                # This would mean they have the same tutor 
                if possible_students < len(student_array):
                    student_array.append(student)

        # if any of the student times intesect that would be bad
        for student in student_array:
            for other in student_array:
                if student != other and time_assignment[student] == time_assignment[other]:
                    return False
                
    return True 

def check_completion(student_assignment, time_assignment, students, tutors):
    if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) is False:
        return True 
    return False

students, tutors = match_students_tutors(students, tutors)
student_assignment, time_assignment = backtrack(student_assignment, time_assignment, students, tutors)

for student, tutor in student_assignment.items():
    print(f"Student: {student.name}, Tutor: {tutor.name}, Class: {student.courses}", student.final_time)