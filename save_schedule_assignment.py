import csv
import os
from models import Student, Tutor
from data_loader import load_student_data, load_tutor_data, load_existing_schedule, update_students_tutors, split_student_data
from scheduler import match_students_tutors, get_not_matched, backtrack

def save_schedule(student_assignment, not_matched):
    # Define the directory where you want to save the file
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the directory where the script is located
    file_path = os.path.join(script_dir, 'saved_schedule.csv')
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Status', 'Student Name', 'Student Email', 'Student Grade', 'Student Availability', 'Student Courses', 'Additional Info', 'Not Tutors', 'Tutor Name', 'Tutor Email', 'Tutor Grade', 'Tutor Availability', 'Tutor Courses', 'Time', 'Student Email Status', 'Tutor Email Status'])
        for student, tutor in student_assignment.items():
            writer.writerow([
                'Matched', student.name, student.email, student.grade, ', '.join(student.availability), ', '.join(student.courses), student.info,
                student.not_tutors, tutor.name, tutor.email, tutor.grade, ', '.join(tutor.availability), ', '.join(tutor.courses),
                student.final_time, student.email_status, student.tutor_email_status
            ])
        for student in not_matched.keys():
            writer.writerow([
                'Not Matched', student.name, student.email, student.grade, ', '.join(student.availability), ', '.join(student.courses), student.info,
                student.not_tutors, '', '', '', '', '', '', student.email_status
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
    
    # Update students and tutors with new data
    students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)
    students, tutors = match_students_tutors(students, tutors)
    not_matched = get_not_matched(students, tutors)

    # Perform backtracking to find a valid schedule
    result = None

    while not result:
        result = backtrack(student_assignment, time_assignment, students, tutors)

    # Save the result
    if result:
        student_assignment, time_assignment = result
        save_schedule(student_assignment, not_matched)
    else:
        print("No solution found.")

    return result