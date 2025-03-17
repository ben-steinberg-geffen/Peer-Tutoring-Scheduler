import csv
import os
from models import Student, Tutor
from data_loader import load_student_data, load_tutor_data, load_existing_schedule, update_students_tutors, split_student_data
from scheduler import match_students_tutors, get_not_matched, backtrack

def save_schedule(student_assignment):
    # Define the directory where you want to save the file
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory where the script is located
    file_path = os.path.join(script_dir, 'saved_schedule.csv')
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Student Name', 'Student Email', 'Student Grade', 'Student Availability', 'Student Courses', 'Additional Info', 'Not Tutors', 'Tutor Name', 'Tutor Email', 'Tutor Grade', 'Tutor Availability', 'Tutor Courses', 'Time'])
        for student, tutor in student_assignment.items():
            writer.writerow([
                student.name, student.email, student.grade, ', '.join(student.availability), ', '.join(student.courses), student.info,
                student.not_tutors, tutor.name, tutor.email, tutor.grade, ', '.join(tutor.availability), ', '.join(tutor.courses),
                student.final_time
            ])
    print(f"Results saved to {file_path}")

def save_schedule_assignment():
    # Load data
    student_df = load_student_data()
    student_df = split_student_data(student_df)
    tutor_df = load_tutor_data()

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
    
    # student_assignment, time_assignment = {}, {}
    
    # Update students and tutors with new data
    students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)
    students, tutors = match_students_tutors(students, tutors)
    not_matched = get_not_matched(students, tutors)
    for student in not_matched.keys():
        print(f"Student {student.name} with courses {student.courses} could not be matched because {not_matched[student][0]}")
    # Perform backtracking to find a valid schedule
    result = None
    n = 0

    while not result:
        n += 1
        if n > 5000:
            print("No solution found.")
            break
        result = backtrack(student_assignment, time_assignment, students, tutors)

    # Save the result
    if result:
        student_assignment, time_assignment = result
        for student in student_assignment.keys():
            if not set(student.courses).intersection(student_assignment[student].courses):
                print(f"Student {student.name} with course {student.courses} is not matched with tutor {student_assignment[student].name} with course {student_assignment[student].courses}")
        save_schedule(student_assignment)
    else:
        print("No solution found.")

    return result