import csv

def load_constraints(constraints_file):
    constraints = []
    with open(constraints_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            constraints.append(row)
    return constraints

def apply_constraints(students, tutors, constraints):
    for constraint in constraints:
        if constraint['type'] == 'not_tutor':
            student_name = constraint['student']
            tutor_name = constraint['tutor']
            student = next((s for s in students if s.name == student_name), None)
            tutor = next((t for t in tutors if t.name == tutor_name), None)
            if student and tutor:
                student.not_tutors.append(tutor)
                tutor.not_students.append(student)
        elif constraint['type'] == 'higher_grade':
            student_name = constraint['student']
            tutor_name = constraint['tutor']
            student = next((s for s in students if s.name == student_name), None)
            tutor = next((t for t in tutors if t.name == tutor_name), None)
            if student and tutor and tutor.grade <= student.grade:
                student.not_tutors.append(tutor)
                tutor.not_students.append(student)