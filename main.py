import csv
import os
from models import Student, Tutor
from data_loader import load_student_data, load_tutor_data, load_existing_schedule, update_students_tutors, split_student_data
from scheduler import match_students_tutors, get_not_matched, backtrack

def main():
    def save_schedule(student_assignment, not_matched):
        with open('tutoring_schedule.csv', mode='w', newline='') as file:
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
        print("Results saved to tutoring_schedule.csv")
        
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
    # else:
    #     student_assignment, time_assignment = {}, {}

    print(student_assignment)
    
    # Update students and tutors with new data
    students, tutors = update_students_tutors(student_df, tutor_df, student_assignment)
    students, tutors = match_students_tutors(students, tutors)
    not_matched = get_not_matched(students, tutors)

    # for student in not_matched.keys():
    #     print(f"Student {student.name} with courses {student.courses} could not be matched because {not_matched[student][0]}")
    
    # Perform backtracking to find a valid schedule
    result = None

    while not result:
        result = backtrack(student_assignment, time_assignment, students, tutors)
    
    # Save the result
    if result:
        student_assignment, time_assignment = result
        # for student in student_assignment.keys():
            # if not set(student.courses).intersection(student_assignment[student].courses):
            #     print(f"Student {student.name} with course {student.courses} is not matched with tutor {student_assignment[student].name} with course {student_assignment[student].courses}")
        save_schedule(student_assignment, not_matched)
    else:
        print("No solution found.")

    return result

if __name__ == "__main__":
    student_assignment, time_assignment = main()
    # for student in student_assignment:
    #     print(f"{student.name} is matched with {student_assignment[student].name} at {time_assignment[student]} for this course: {student.courses}")


