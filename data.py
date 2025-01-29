import os
import pandas as pd

def merge_courses(row):
    """
    Merge middle school and upper school course selections into a single set of columns.
    """
    courses = []
    for i in range(1, 8):
        ms_course = row.get(f'ms_course_{i}')
        us_course = row.get(f'us_course_{i}')
        if pd.notna(ms_course):
            courses.append(ms_course)
        elif pd.notna(us_course):
            courses.append(us_course)
        else:
            courses.append(None)
    return courses

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
        "Select Courses for Tutoring (Slot 1) (MS)": "ms_course_1",
        "Select Courses for Tutoring (Slot 2) (MS)": "ms_course_2",
        "Select Courses for Tutoring (Slot 3) (MS)": "ms_course_3",
        "Select Courses for Tutoring (Slot 4) (MS)": "ms_course_4",
        "Select Courses for Tutoring (Slot 5) (MS)": "ms_course_5",
        "Select Courses for Tutoring (Slot 6) (MS)": "ms_course_6",
        "Select Courses for Tutoring (Slot 7) (MS)": "ms_course_7",
        "Select Courses for Tutoring (Slot 1) (US)": "us_course_1",
        "Select Courses for Tutoring (Slot 2) (US)": "us_course_2",
        "Select Courses for Tutoring (Slot 3) (US)": "us_course_3",
        "Select Courses for Tutoring (Slot 4) (US)": "us_course_4",
        "Select Courses for Tutoring (Slot 5) (US)": "us_course_5",
        "Select Courses for Tutoring (Slot 6) (US)": "us_course_6",
        "Select Courses for Tutoring (Slot 7) (US)": "us_course_7",
        "If there is a specific area/topic that the sessions should focus on, please list it here. Examples: linear equations, graphing, grammar,  sentence syntax, etc.": "additional_info",
    })

    # Merge course selections for one set of columns
    merged_courses = df.apply(merge_courses, axis=1, result_type='expand')
    merged_courses.columns = [f'course_{i}' for i in range(1, 8)]
    df = pd.concat([df, merged_courses], axis=1)

    # Make a list of all the courses and availability status the student provided
    df['courses'] = df.apply(lambda row: [course for course in row[['course_1', 'course_2', 'course_3', 'course_4', 'course_5', 'course_6', 'course_7']] if pd.notna(course)], axis=1)
    df['availability'] = df.apply(lambda row: [day for day in row[['monday_availability', 'tuesday_availability', 'wednesday_availability', 'thursday_availability', 'friday_availability']] if pd.notna(day)], axis=1)

    # Drop the original MS and US course columns
    df = df.drop(columns=[f'ms_course_{i}' for i in range(1, 8)] + [f'us_course_{i}' for i in range(1, 8)])

    # Drop rows with missing names in case the data is incomplete
    df = df.dropna(subset=["name"])
    
    return df

def load_tutor_data():
    """
    Load tutor requests data from spring and fall CSV files, combine them, and rename columns for consistency.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the combined tutor requests data.
    
    OUTDATED (FOR OLD TUTOR RESPONSE CSV FILES)
    """
    base_path = os.path.dirname(__file__)
    spring_file_path = os.path.join(base_path, "data", "tutor_responses_spring.csv")
    fall_file_path = os.path.join(base_path, "data", "tutor_responses_fall.csv")
    
    # Load both CSV files
    spring_df = pd.read_csv(spring_file_path)
    fall_df = pd.read_csv(fall_file_path)
    
    # Combine the dataframes
    df = pd.concat([spring_df, fall_df])
    
    # Rename columns
    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Email Address": "email", 
        "Your name (first and last)": "name", 
        "Your Grade": "grade", 
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Monday]": "monday_availability", 
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Tuesday]": "tuesday_availability",
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Wednesday]": "wednesday_availability",
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Thursday]": "thursday_availability",
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Friday (before school or during lunch only)]": "friday_availability",
        "Subject(s) and level(s) you are comfortable or want to tutor in. This will be reviewed by educators. ": "subjects",
    })

    df = df.dropna(subset=["name"])
    
    return df
