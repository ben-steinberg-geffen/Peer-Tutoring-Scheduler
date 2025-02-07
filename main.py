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
            
            index = student.tutor_index

            if not student.matched_tutors: # same as == []
                continue

            student.tutor_index += 1
            if student.tutor_index > len(student.matched_tutors) - 1:
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
    # We also need to now account for assigning times too
    if check_completion(student_assignment, time_assignment, students, tutors):
        return student_assignment, time_assignment
        # After this, we need to assign the tutors to the students
    
    tutor_var, student_var = select_unassigned_tutor(students) ## iter1 is Raina Mahtabi, Ben Steinberg
    time_var = select_unassigned_time(tutor_var, student_var) ## iter1 Wednesday: H Block

    # Assign tutors in a list, if they don't work then backtrack
    for student in students:       
        if not student.matched_tutors: 
            continue
        
        student_assignment[student] = tutor_var
        student.final_tutor = tutor_var
        time_assignment[student] = time_var
        student.final_time = time_var

        if check_constraints(student_assignment, time_assignment):
            

            for student, tutor in student_assignment.items():
                print(f"Student: {student.name}, Tutor: {tutor.name}, Class: {student.courses}")

            for student, time in time_assignment.items():
                print(f"Student: {student.name} Time: {time}")    

            result = backtrack(student_assignment, time_assignment, students, tutors)
            
            if result:
                print('HERERERE')
                return result
            
            # Make sure to account for ALL of the times before removing
            student.final_tutor = None
            student.final_time = None
            del student_assignment[student]
            del time_assignment[student]

        else: 
            student.final_tutor = None
            student.final_time = None
            del student_assignment[student]
            del time_assignment[student]

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
                
    # Prioritize tutors with no students over students with tutors
    '''
    for tutor in tutors:
        if tutor not in student_assignment.values():
            for student in students:
                if student not in student_assignment:
                    return False
    '''
    return True 

def check_completion(student_assignment, time_assignment, students, tutors):
    if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) is False:
        return True 
    return False

students, tutors = match_students_tutors(students, tutors)
student_assignment, time_assignment = backtrack(student_assignment, time_assignment, students, tutors)

print(students[0].name, [tutor.name for tutor in students[0].matched_tutors], [tutor.availability for tutor in students[0].matched_tutors], students[0].availability)
print(students[1].name, [tutor.name for tutor in students[1].matched_tutors], [tutor.availability for tutor in students[1].matched_tutors], students[1].availability)
print(students[2].name, [tutor.name for tutor in students[2].matched_tutors], [tutor.availability for tutor in students[2].matched_tutors], students[2].availability)