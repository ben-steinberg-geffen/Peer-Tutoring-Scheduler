import random

# random.seed(42)

def get_time_intersection(student, tutor):
    time_slots = []
    for slot in student.availability: 
        if slot in tutor.availability:
            time_slots.append(slot)
    return time_slots

def match_students_tutors(students, tutors):
    not_matched = {}
    for student in students:
        reason = ""
        for tutor in tutors:
            if set(student.courses).intersection(set(tutor.courses)) == set(student.courses):
                if set(student.availability).intersection(set(tutor.availability)):
                    if not student in tutor.not_students and not tutor in student.not_tutors:
                        student.matched_tutors.append(tutor)
                        tutor.matched_students.append(student)
        if not student.matched_tutors: #BUGGED
            if any(set(student.courses).intersection(set(tutor.courses)) for tutor in tutors) and not any(set(student.availability).intersection(set(tutor.availability)) for tutor in tutors):
                reason = "No matching availability with any tutor that teaches required courses."
            elif not any(set(student.courses).intersection(set(tutor.courses)) for tutor in tutors):
                reason = "No matching courses with any tutor."
            elif all(student in tutor.not_students or tutor in student.not_tutors for tutor in tutors):
                reason = "All potential tutors are in the not preferred list."
            elif not any(set(student.availability).intersection(set(tutor.availability)) for tutor in tutors):
                reason = "No matching availability with any tutor."
            elif not any(set(student.courses).intersection(set(tutor.courses)) and set(student.availability).intersection(set(tutor.availability)) for tutor in tutors):
                reason = "No matching availability with tutors that teach required courses."
            not_matched[student] = reason
    return students, tutors, not_matched

def select_unassigned_tutor(students):
    for student in students: 
        if student.final_tutor == None: 
            if not student.matched_tutors:
                continue

            random.shuffle(student.matched_tutors)

            return student.matched_tutors[0], student
        
    return False

def select_unassigned_time(tutor, student):
    times = get_time_intersection(student, tutor)

    random.shuffle(times)

    return times

def backtrack(student_assignment, time_assignment, students, tutors):
    if check_completion(student_assignment, time_assignment, students):
        return student_assignment, time_assignment
    
    result = select_unassigned_tutor(students)

    if not result:
        return False
    
    tutor, student = result
    times = get_time_intersection(student, tutor)

    for time in times:
        student_assignment[student] = tutor
        time_assignment[student] = time

        student.final_tutor = tutor
        student.final_time = time

        tutor.final_students[student] = time
        tutor.final_times.append(time)

        if check_constraints(student_assignment, time_assignment):
            result = backtrack(student_assignment, time_assignment, students, tutors)

            if result:
                return result
        
        del student_assignment[student]
        del time_assignment[student]
        
        student.final_tutor = None
        student.final_time = None
        
        del tutor.final_students[student]
        tutor.final_times.remove(time)

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
                # print("Constraint violated: Two students assigned to the same tutor at the same time.")
                return False
    for tutor in student_assignment.values():
        if len(tutor.final_students) > 2:
            # print("Constraint violated: Tutor assigned to more than two students.")
            return False
    # Ensure tutors without a student take priority over those with one already
    for student in student_assignment.keys():
        if student_assignment[student].final_students and len(student_assignment[student].final_students) == 1:
            for other_student in student_assignment.keys():
                if student_assignment[other_student] == student_assignment[student] and other_student != student:
                    # print("Constraint violated: Tutor with a student assigned another student while there are tutors without students.")
                    return False
    return True 

def check_completion(student_assignment, time_assignment, students):
    if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) is False:
        return True 
    return False