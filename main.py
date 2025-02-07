from data import load_student_data, load_tutor_data
# import sys

# sys.setrecursionlimit(10**4)

student_df = load_student_data()
tutor_df = load_tutor_data()

student_assignment = {}
time_assignment = {}

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
        self.final_times = []
        
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

            index = student.tutor_index - 1 # - 1 because we increment it before returning

            student.tutor_index += 1
            
            if student.tutor_index > len(student.matched_tutors) - 1:
                student.tutor_index = 0

            return student.matched_tutors[index], student
        
    return False

def select_unassigned_time(tutor_var, student_var):
    index = student_var.time_index - 1

    times = get_time_intersection(student_var, tutor_var)

    selected_time = times[index]

    student_var.time_index += 1
    if student_var.time_index > len(times) - 1:
        student_var.time_index = 0

    return selected_time

def backtrack(student_assignment, time_assignment, students, tutors):
    if check_completion(student_assignment, time_assignment, students, tutors):
        return student_assignment, time_assignment
    
    result = select_unassigned_tutor(students)

    if not result:
        return False
    
    tutor_var, student_var = result
    time_var = select_unassigned_time(tutor_var, student_var)

    student_assignment[student_var] = tutor_var
    student_var.final_tutor = tutor_var
    time_assignment[student_var] = time_var
    student_var.final_time = time_var
    tutor_var.final_students[student_var] = time_var
    tutor_var.final_times.append(time_var)

    if check_constraints(student_assignment, time_assignment):
        result = backtrack(student_assignment, time_assignment, students, tutors)

        if result:
            return result
        
    student_var.final_tutor = None
    student_var.final_time = None
    del student_assignment[student_var]
    del time_assignment[student_var]
    del tutor_var.final_students[student_var]
    tutor_var.final_times.remove(time_var)

    return False

def check_constraints(student_assignment, time_assignment):
    '''
    Tutors can't teach two students at the same time slot*
    # Tutors and students must have the same classes
    # It must be at the same time as well
    # Tutors with no students take priority over students with tutors * 
    * are the ones that we need to handle here
    '''
    # Check if any tutor is assigned to more than one student at the same time
    for student in time_assignment.keys():
        for other in time_assignment.keys():
            if student != other and student.final_time == other.final_time and student_assignment[student] == student_assignment[other]:
                print("Constraint violated: Two students assigned to the same tutor at the same time.")
                return False
    # for tutor in student_assignment.values():
    #     if len(tutor.final_students) > 2:
    #         return False
    return True 

def check_completion(student_assignment, time_assignment, students, tutors):
    if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) is False:
        return True 
    return False

students, tutors = match_students_tutors(students, tutors)
result = backtrack(student_assignment, time_assignment, students, tutors)

if result:
    student_assignment, time_assignment = result
    for student, tutor in student_assignment.items():
        print(f"Student: {student.name}, Tutor: {tutor.name}, Class: {student.courses}", student.final_time)
else:
    print("No solution found.")