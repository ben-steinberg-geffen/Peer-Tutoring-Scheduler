import random

def get_time_intersection(student, tutor):
    time_slots = []
    for slot in student.availability: 
        if slot in tutor.availability:
            time_slots.append(slot)
    return time_slots

def match_students_tutors(students, tutors):
    for student in students:
        reason = ""
        for tutor in tutors:
            if set(student.courses).intersection(set(tutor.courses)) == set(student.courses):
                if set(student.availability).intersection(set(tutor.availability)):
                    if not student in tutor.not_students and not tutor in student.not_tutors:
                        student.matched_tutors.append(tutor)
                        tutor.matched_students.append(student)
    return students, tutors

def get_not_matched(students, tutors):
    not_matched = {}
    for student in students:
        reason = "tutors that teach your course are not available at the same time"
        if not student.matched_tutors:
            potential_times = []
            if (set(student.courses).intersection(set(tutor.courses)) == set(student.courses) and not any(set(student.availability).intersection(set(tutor.availability))) for tutor in tutors):
                for tutor in tutors: 
                    if set(student.courses).intersection(set(tutor.courses)) == set(student.courses):
                        for time in tutor.availability:
                            potential_times.append(time) 
                        potential_times = list(set(potential_times))
            elif not any(set(student.courses).intersection(set(tutor.courses)) for tutor in tutors):
                reason = "no tutors are availabile to teach your selected courses"
            else:
                reason = "NONE"
            not_matched[student] = [reason, potential_times]
        if len(student.availability) < len(student.courses):
            reason = "student needs to enter more times of availability"
            not_matched[student] = [reason, []]

        # this is the only precaution we took for this case, we need to make it so that if the availability doesn't 
        # line up for other courses then we need to add that to the not_matched dictionary
            
        # the amount of courses needs to have the same amount or more UNIQUE time values that line up

    return not_matched

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


        for student in time_assignment.keys():
            for student_2 in time_assignment.keys():
                if student != student_2:        
                    if student.name == student_2.name and time_assignment[student] == time_assignment[student_2]:
                        print(f"Student {student.name} with course {student.courses} and {student_2.courses} are assigned to the same time {time_assignment[student]}")

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
    # Check if any tutor is assigned to more than one student at the same time
    for student in time_assignment.keys():
        for other in time_assignment.keys():
            if student != other and student.final_time == other.final_time and student_assignment[student] == student_assignment[other]:
                return False
            
    for student in time_assignment.keys():
       for student_2 in time_assignment.keys():
           if student != student_2:        
               if student.name == student_2.name and time_assignment[student] == time_assignment[student_2]:
                   return False
            
    for tutor in student_assignment.values():
        if len(tutor.final_students) > 2:
            return False
    # Ensure tutors without a student take priority over those with one already
    for student in student_assignment.keys():
        if student_assignment[student].final_students and len(student_assignment[student].final_students) == 1:
            for other_student in student_assignment.keys():
                if student_assignment[other_student] == student_assignment[student] and other_student != student:
                    return False
    return True 

def check_completion(student_assignment, time_assignment, students):
    if check_constraints(student_assignment, time_assignment) and select_unassigned_tutor(students) is False:
        return True 
    return False