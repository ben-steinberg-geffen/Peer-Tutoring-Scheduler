import os
import csv
import pandas as pd
import requests
from io import StringIO
from models import Student, Tutor 
from persistent_data import load_data

def load_student_data():
    """
    Load student requests data from a CSV file, rename columns for consistency, and merge course selections.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the student requests data.
    """
    message = load_data("links")
    if  message is not None:
        student_link = message["student_link"].replace("/edit?usp=sharing", "/export?format=csv")
        response = requests.get(student_link)
    else:
        response = requests.get('https://docs.google.com/spreadsheets/d/1t3wSutzLqKCV6-ZZVaEEU3NZaRT_ZNhVyxHPAqK_oE8/export?format=csv')
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
        "If there is a specific area/topic that the sessions should focus on, please list it here. Examples: linear equations, graphing, grammar, sentence syntax, etc. If you have a tutor in mind, you may also request them here. " : "additional_info"})

    # Merge course and availability selections and separate them into a list
    df['courses'] = df.apply(lambda row: list(sorted(set(course.strip() for course_list in row[['ms_courses', 'us_courses']] if pd.notna(course_list) for course in course_list.split(', ')))), axis=1)
    df['availability'] = df.apply(lambda row: [f"{day_name}: {slot.strip()}" for day_name, day in zip(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], row[['monday_availability', 'tuesday_availability', 'wednesday_availability', 'thursday_availability', 'friday_availability']]) if pd.notna(day) and day != 'Not Available' for slot in day.split(',')], axis=1)
    df['additional_info'] = df['additional_info'].apply(lambda x: x.replace('\n', ' ') if pd.notna(x) else x)
    # df['additional_info'] = df['additional_info'].apply(lambda x: x.replace(',', '') if pd.notna(x) else x)
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

def load_tutor_data():
    """
    Load tutor requests data from spring and fall CSV files, combine them, and rename columns for consistency.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the combined tutor requests data.
    """
    message = load_data("links")
    if message is not None:
        tutor_link = message["tutor_link"].replace("/edit?usp=sharing", "/export?format=csv")
        response = requests.get(tutor_link)
    else:
        response = requests.get('https://docs.google.com/spreadsheets/d/1UCMF2kBOBzqD_s-PTI-z4tFNxH5FLjEYzVAkymsGH7M/export?format=csv')
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

def load_existing_schedule(schedule_file, students, tutors):
    student_assignment = {}
    time_assignment = {}
    processed_students = set()  # Track ALL students we've already processed (both Matched and Not Matched)
    
    with open(schedule_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            student_name = row['Student Name']
            processed_students.add(student_name)  # Track all students, regardless of status
            
            if row['Status'] == 'Matched':
                student = next((s for s in students if s.name == row['Student Name'] and s.courses[0] == row['Student Courses']), None)
                tutor = next((t for t in tutors if t.name == row['Tutor Name']), None)
                
                if student and tutor:
                    student_assignment[student] = tutor
                    time_assignment[student] = row['Time']
                    student.final_tutor = tutor
                    student.final_time = row['Time']
                    tutor.final_students[student] = row['Time']
                    tutor.final_times.append(row['Time'])
                    student.email_status = row['Student Email Status']
                    tutor.email_status = row['Tutor Email Status']

    return student_assignment, time_assignment, processed_students

def update_students_tutors(student_df, tutor_df, student_assignment, processed_students=None):
    existing_students = [student.name for student in student_assignment.keys()]
    existing_tutors = [tutor.name for tutor in student_assignment.values()]
    
    # Combine existing students with previously processed students to avoid re-processing
    if processed_students is None:
        processed_students = set()
    all_processed = set(existing_students) | processed_students
    
    students = []
    tutors = []
    
    for _, row in student_df.iterrows():
        if row['name'] not in all_processed:
            students.append(Student(row['name'], row['email'], row['grade'], row['availability'], row['courses'], row['additional_info'], []))
    
    for _, row in tutor_df.iterrows():
        if row['name'] not in existing_tutors:
            tutors.append(Tutor(row['name'], row['email'], row['grade'], row['availability'], row['courses'], []))
    return students, tutors