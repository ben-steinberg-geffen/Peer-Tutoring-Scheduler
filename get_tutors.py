from data_loader import load_student_data, load_tutor_data
import random
import csv

class Student:
    def __init__(self, name, email, grade, availability, courses, not_tutors):
        self.name = name
        self.email = email
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matched_tutors = []
        self.not_tutors = not_tutors
        self.tutor_index = 0 
        self.time_index = 0
        self.final_tutor = None
        self.final_time = None

class Tutor:
    def __init__(self, name, email, grade, availability, courses, not_students):
        self.name = name
        self.email = email
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.not_students = not_students
        self.matched_students = []
        self.final_students = {} # This aligns the students with the time slot
        self.final_times = []

def get_tutors(student_path, tutor_path):
    student_df = load_student_data(student_path)
    tutor_df = load_tutor_data(tutor_path)

    student_assignment = {}
    time_assignment = {}
            
    students = []
    tutors = []

    for index, row in student_df.iterrows():
        students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))

    for index, row in tutor_df.iterrows():
        tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))

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
                        if not student in tutor.not_students and not tutor in student.not_tutors:
                            student.matched_tutors.append(tutor)
                            tutor.matched_students.append(student)
        return students, tutors

    def select_unassigned_tutor(students):
        for student in students: 
            if student.final_tutor == None: 
                if not student.matched_tutors:
                    continue

                index = student.tutor_index - 1 # because we increment it before returning

                student.tutor_index += 1
                
                if student.tutor_index > len(student.matched_tutors) - 1:
                    student.tutor_index = 0

                random.shuffle(student.matched_tutors)

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
        if check_completion(student_assignment, time_assignment, students):
            return student_assignment, time_assignment
        
        result = select_unassigned_tutor(students)

        if not result:
            return False
        
        tutor_var, student_var = result
        times = get_time_intersection(student_var, tutor_var)
        random.shuffle(times)

        for time_var in times:
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
        for tutor in student_assignment.values():
            if len(tutor.final_students) > 2:
                print("Constraint violated: Tutor assigned to more than two students.")
                return False
        # Ensure tutors without a student take priority over those with one already
        for student in student_assignment.keys():
            if student_assignment[student].final_students and len(student_assignment[student].final_students) == 1:
                for other_student in student_assignment.keys():
                    if student_assignment[other_student] == student_assignment[student] and other_student != student:
                        print("Constraint violated: Tutor with a student assigned another student while there are tutors without students.")
                        return False
        return True 

    def check_completion(student_assignment, time_assignment, students):
        if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) is False:
            return True 
        return False

    students, tutors = match_students_tutors(students, tutors)

    result = None

    while not result:
        result = backtrack(student_assignment, time_assignment, students, tutors)

    if result:
        return result
    else:
       return None