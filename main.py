from data_loader import load_student_data, load_tutor_data, load_existing_schedule, update_students_tutors
from models import Student, Tutor
from constraint_loader import load_constraints, apply_constraints
from scheduler import match_students_tutors, backtrack
import csv

# Load data
student_df = load_student_data()
tutor_df = load_tutor_data()

# Initialize students and tutors
students = []
tutors = []

for index, row in student_df.iterrows():
    students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))

for index, row in tutor_df.iterrows():
    tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))

# Load existing schedule if any
student_assignment, time_assignment = load_existing_schedule('tutoring_schedule.csv', students, tutors)

# Update students and tutors with new data
students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)

# Load and apply constraints
# constraints = load_constraints('constraints.csv')
# apply_constraints(students, tutors, constraints)

# Match students and tutors
students, tutors, not_matched = match_students_tutors(students, tutors)

# Perform backtracking to find a valid schedule
result = None

while not result:
    result = backtrack(student_assignment, time_assignment, students, tutors)

# Save the result
if result:
    student_assignment, time_assignment = result
    
    for student, reason in not_matched.items():
        print(f"{student.name} was not matched because {reason}")

    with open('tutoring_schedule.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Student Object', 'Student Name', 'Student Email', 'Student Grade', 'Student Availability', 'Student Courses', 'Not Tutors', 'Tutor Object', 'Tutor Name', 'Tutor Email', 'Tutor Grade', 'Tutor Availability', 'Tutor Courses', 'Time'])
        for student, tutor in student_assignment.items():
            writer.writerow([
                student, student.name, student.email, student.grade, ', '.join(student.availability), ', '.join(student.courses),
                student.not_tutors, tutor, tutor.name, tutor.email, tutor.grade, ', '.join(tutor.availability), ', '.join(tutor.courses),
                student.final_time
            ])
    print("Results saved to tutoring_schedule.csv")
else:
    print("No solution found.")