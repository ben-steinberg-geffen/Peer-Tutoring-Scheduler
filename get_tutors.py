import csv
import os
from models import Student, Tutor
from data_loader import load_student_data, load_tutor_data, load_existing_schedule, update_students_tutors
from constraint_loader import load_constraints, apply_constraints
from scheduler import match_students_tutors, backtrack

def save_schedule(student_assignment, path):
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Student Name', 'Student Email', 'Student Grade', 'Student Availability', 'Student Courses', 'Additional Info', 'Not Tutors', 'Tutor Name', 'Tutor Email', 'Tutor Grade', 'Tutor Availability', 'Tutor Courses', 'Time'])
        for student, tutor in student_assignment.items():
            writer.writerow([
                student.name, student.email, student.grade, ', '.join(student.availability), ', '.join(student.courses), student.info,
                student.not_tutors, tutor.name, tutor.email, tutor.grade, ', '.join(tutor.availability), ', '.join(tutor.courses),
                student.final_time
            ])
    print("Results saved to tutoring_schedule.csv")

def get_schedule(student_path, tutor_path, save_path):
    # Load data
    student_df = load_student_data(student_path)
    tutor_df = load_tutor_data(tutor_path)

    # Initialize students and tutors
    students = []
    tutors = []

    for _, row in student_df.iterrows():
        students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses'], row['additional_info'], []))

    for _, row in tutor_df.iterrows():
        tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))

    # Load existing schedule if any
    if os.path.exists('tutoring_schedule.csv'):
        student_assignment, time_assignment = load_existing_schedule('tutoring_schedule.csv', students, tutors)
    else:
        student_assignment, time_assignment = {}, {}

    # Update students and tutors with new data
    students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)
    students, tutors, not_matched = match_students_tutors(students, tutors)

    # Load and apply constraints
    constraints = load_constraints('constraints.csv')
    apply_constraints(students, tutors, constraints)

    # Perform backtracking to find a valid schedule
    result = None

    while not result:
        result = backtrack(student_assignment, time_assignment, students, tutors)

    # Save the result
    if result:
        student_assignment, time_assignment = result

        for student, reason in not_matched.items():
            print(f"{student.name} was not matched because {reason}")
        for student, tutor in student_assignment.items():
            if not set(student.courses).intersection(set(tutor.courses)):
                print(f"{student.name} with {tutor.name} BUT SOMEHOW NO INTERSECTION.")
        save_schedule(student_assignment, save_path)
    else:
        print("No solution found.")

    return result