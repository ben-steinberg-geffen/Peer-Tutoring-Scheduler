import os
import pandas as pd

def load_student_data():
    """
    Load student requests data from a CSV file, rename columns for consistency, and merge course selections.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the student requests data.
    """
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "data", "student_responses.csv")
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
        "If there is a specific area/topic that the sessions should focus on, please list it here. Examples: linear equations, graphing, grammar,  sentence syntax, etc.": "additional_info",
    })

    # Merge course and availability selections and separate them into a list
    df['courses'] = df.apply(lambda row: list(sorted(set(course.strip() for course_list in row[['ms_courses', 'us_courses']] if pd.notna(course_list) for course in course_list.split(', ')))), axis=1)
    df['availability'] = df.apply(lambda row: [day for day in row[['monday_availability', 'tuesday_availability', 'wednesday_availability', 'thursday_availability', 'friday_availability']] if pd.notna(day)], axis=1)
    df['status'] = "Pending"

    # Drop rows with missing names in case the data is incomplete
    df = df.dropna(subset=["name"])
    
    return df

def load_tutor_data():
    """
    Load tutor requests data from spring and fall CSV files, combine them, and rename columns for consistency.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the combined tutor requests data.
    """
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "data", "tutor_responses.csv")

    # Load both CSV files
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
    df['availability'] = df.apply(lambda row: [day for day in row[['monday_availability', 'tuesday_availability', 'wednesday_availability', 'thursday_availability', 'friday_availability']] if pd.notna(day)], axis=1)
    df['status'] = "Pending"

    # Drop rows with missing names in case the data is incomplete
    df = df.dropna(subset=["name"])
    
    return df
