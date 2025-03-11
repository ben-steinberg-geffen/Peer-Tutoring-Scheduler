import os
import csv
import pandas as pd
import requests
from io import StringIO
from models import Student, Tutor

def load_student_data():
    """
    Load student requests data from a CSV file, rename columns for consistency, and merge course selections.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the student requests data.
    """
    response = requests.get('https://docs.google.com/spreadsheets/d/1t3wSutzLqKCV6-ZZVaEEU3NZaRT_ZNhVyxHPAqK_oE8/export?format=csv')
    assert response.status_code == 200, 'Wrong status code'
    file_path = StringIO(response.content.decode('utf-8'))
    df = pd.read_csv(file_path)

    # Rename columns
    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Student's Name (first and last)": "name", 
        "Who are you in relation to the student?": "relation", 
        "Student's School Email": "email", 
        "Grade Level": "grade",
        "Availability [Monday]": "monday_availability",
        "Availability [Tuesday]": "tuesday_availability",
        "Availability [Wednesday]": "wednesday_availability",
        "Availability [Thursday]": "thursday_availability",
        "Availability [Friday]": "friday_availability",
        "Select Courses for Tutoring (MS)": "ms_courses",
        "Select Courses for Tutoring (US)": "us_courses",
        "If there is a specific area/topic that the sessions should focus on, please list it here. Examples: linear equations, graphing, grammar, sentence syntax, etc." : "additional_info"  })

    # Merge course and availability selections and separate them into a list
    df['courses'] = df.apply(lambda row: list(sorted(set(course.strip() for course_list in row[['ms_courses', 'us_courses']] if pd.notna(course_list) for course in course_list.split(', ')))), axis=1)
    df['availability'] = df.apply(lambda row: [f"{day_name}: {slot.strip()}" for day_name, day in zip(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], row[['monday_availability', 'tuesday_availability', 'wednesday_availability', 'thursday_availability', 'friday_availability']]) if pd.notna(day) and day != 'Not Available' for slot in day.split(',')], axis=1)
    df['additional_info'] = df['additional_info'].apply(lambda x: x.replace('\n', ' ') if pd.notna(x) else x)

    # Drop rows with missing names in case the data is incomplete
    df = df.dropna(subset=["name"])

    df = df[['name', 'email', 'grade', 'courses', 'availability', 'additional_info']]

    return df

def split_student_data(df):
    new_rows = []
    for _, row in df.iterrows():
        courses = row['courses']
        if len(courses) > 1:
            for course in courses:
                new_row = row.copy()
                new_row['courses'] = [course]
                new_rows.append(new_row)
        else:
            new_rows.append(row)
    return pd.DataFrame(new_rows)

def load_tutor_data(path="tutor_responses.csv"):
    """
    Load tutor requests data from spring and fall CSV files, combine them, and rename columns for consistency.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the combined tutor requests data.
    """
    response = requests.get('https://docs.google.com/spreadsheets/d/1UCMF2kBOBzqD_s-PTI-z4tFNxH5FLjEYzVAkymsGH7M/export?format=csv')
    assert response.status_code == 200, 'Wrong status code'
    file_path = StringIO(response.content.decode('utf-8'))
    df = pd.read_csv(file_path)

    # Rename columns
    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Student's Name (first and last)": "name", 
        "Student's School Email": "email", 
        "Grade Level": "grade",
        "Availability [Monday]": "monday_availability",
        "Availability [Tuesday]": "tuesday_availability",
        "Availability [Wednesday]": "wednesday_availability",
        "Availability [Thursday]": "thursday_availability",
        "Availability [Friday]": "friday_availability",
        "Select Courses for Tutoring (MS)": "ms_courses",
        "Select Courses for Tutoring (US)": "us_courses",
    })

    # Merge course and availability selections and separate them into a list removes duplicate courses as well
    df['courses'] = df.apply(lambda row: list(sorted(set(course.strip() for course_list in row[['ms_courses', 'us_courses']] if pd.notna(course_list) for course in course_list.split(', ')))), axis=1)
    df['availability'] = df.apply(lambda row: [f"{day_name}: {slot.strip()}" for day_name, day in zip(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], row[['monday_availability', 'tuesday_availability', 'wednesday_availability', 'thursday_availability', 'friday_availability']]) if pd.notna(day) and day != 'Not Available' for slot in day.split(',')], axis=1)
    
    # Drop rows with missing names in case the data is incomplete
    df = df.dropna(subset=["name"])

    df = df[['name', 'email', 'grade', 'courses', 'availability']]
    
    return df

def load_assignment():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "tutoring_schedule.csv")
    student_assignment = {}
    time_assignment = {}

    df = 0

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        student_assignment = {df['Student Object'] : df['Tutor Object']}
        time_assignment = {df['Student Object'] : df['Time']}

    return student_assignment, time_assignment

def load_existing_schedule(schedule_file, students, tutors):
    student_assignment = {}
    time_assignment = {}
    with open(schedule_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            student = next((s for s in students if s.name == row['Student Name']), None)
            tutor = next((t for t in tutors if t.name == row['Tutor Name']), None)
            if student and tutor:
                student_assignment[student] = tutor
                time_assignment[student] = row['Time']
                student.final_tutor = tutor
                student.final_time = row['Time']
                tutor.final_students[student] = row['Time']
                tutor.final_times.append(row['Time'])

    return student_assignment, time_assignment

def update_students_tutors(student_df, tutor_df, student_assignment):
    existing_students = {student.name for student in student_assignment.keys()}
    existing_tutors = {tutor.name for tutor in student_assignment.values()}
    
    students = []
    tutors = []
    
    for _, row in student_df.iterrows():
        if row['name'] not in existing_students:
            students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses'], row['additional_info'], []))
    
    for _, row in tutor_df.iterrows():
        if row['name'] not in existing_tutors:
            tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))
    return students, tutors