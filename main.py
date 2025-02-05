from data import load_student_data, load_tutor_data
import pandas as pd

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

def get_time_x_intersection(student_a, student_b):
    times = []
    for time in student_a.availability:
        if time not in student_b.availability: 
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

            if not student.matched_tutors:
                # return False
                continue

            print("availability: ", student.availability)
            print("tutor index: ", student.tutor_index )
            print(len(student.matched_tutors) - 1)
            student.tutor_index += 1
            if student.tutor_index > len(student.matched_tutors) - 1:
                student.tutor_index = 0
            return student.matched_tutors[index]
        
            # This should change the index of the student every time and rotate between them.

    return False

def select_unassigned_time(students):
    for student in students: 
        if student.final_time == None: 
            
            index = student.time_index

            student.time_index += 1
            if student.time_index > len(student.availability) - 1:
                student.time_index = 0
            return student.availability[index]
        
    return False

def backtrack(student_assignment, time_assignment, students, tutors):
    # We also need to now account for assigning times too
    if check_completion(student_assignment, time_assignment, students, tutors):
        return student_assignment, time_assignment
        # After this, we need to assign the tutors to the students
    
    tutor_var = select_unassigned_tutor(students)
    time_var = select_unassigned_time(students)

    # Assign tutors in a list, if they don't work then backtrack
    for student in students:       
        
        if check_constraints(student_assignment, time_assignment):
            print("AT RECURSIVE")
            student_assignment[tutor_var] = student
            time_assignment[student] = time_var


            result = backtrack(student_assignment, time_assignment, students, tutors)
            
            if result != False:
                return result
            
            # Make sure to account for ALL of the times before removing
            del student_assignment[tutor_var]
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
                if time_assignment[student] == time_assignment[other]:
                    print("here2")
                    return False
                
    # Prioritize tutors with no students over students with tutors
    '''
    for tutor in tutors:
        if tutor not in student_assignment.values():
            for student in students:
                if student not in student_assignment:
                    print("here3")
                    return False
    '''
    print("passes constraints")
    return True 

def check_completion(student_assignment, time_assignment, students, tutors):
    print(select_unassigned_tutor(students))
    if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) == False:
        return True 
    return False

students, tutors = match_students_tutors(students, tutors)
student_assignment, time_assignment = backtrack(student_assignment, time_assignment, students, tutors)

print("student_assignment: ", student_assignment)
print("time_assignment: ", time_assignment)