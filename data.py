import os
import pandas as pd

def load_student_data():
    """
    Load student requests data from a CSV file and rename columns for consistency.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the tutor requests data.
    """
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "data", "student_requests.csv")
    df = pd.read_csv(file_path)

    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Status": "status", 
        "Student's name: ": "name", 
        "Who are you in relation to the student?": "relation", 
        "Student email address: ": "email", 
        "Subject (and level if applicable) that the student needs tutoring in: ": "subjects",
        "Students Grade level: ": "grade",
        "If there is a specific area/topic that the sessions should focus on, please list it here.  Examples: linear equations, graphing, grammar,  sentence syntax, etc. ": "topic",
        "For EDUCATORS: If you would like a specific tutor to help your student, please list them here.": "recommended_tutor",
        "Contact log": "contact_log",
        "Days/Times requested": "requested_times",
        # "Tutor matched": "tutor_assigned", # Tutor already matched in data but not our intention
        "Additional comments": "additional_comments",
    })

    df = df.dropna(subset=["name"])
    
    return df

def load_tutor_data():
    """
    Load tutor requests data from a CSV file and rename columns for consistency.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the tutor requests data.
    """

    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "data", "tutor_requests.csv")
    df = pd.read_csv(file_path)

    df = df.rename(columns={
        "Timestamp": "timestamp",
        "Email Address": "email", 
        "Your name (first and last)": "name", 
        "Your Grade": "grade", 
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Monday]": "monday_availability", 
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Tuesday]": "tuesday_availability",
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Wednesday]": "wednesday_availability",
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Thursday]": "thursday_availability",
        "Select the days (must be available for BOTH blue and gold week) and times you are available for tutoring [Friday (before school or during lunch only)]": "friday_avaibility",
        "Subject(s) and level(s) you are comfortable or want to tutor in. This will be reviewed by educators. ": "subjects",
    })

    df = df.dropna(subset=["name"])
    
    return df

if __name__ == "__main__":
    student_df = load_student_data()
    tutor_df = load_tutor_data()