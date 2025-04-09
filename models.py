class Student:
    def __init__(self, name, email, grade, availability, courses, additional_info, not_tutors, email_status, final_tutor=None):
        self.name = name
        self.email = email
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.matched_tutors = []
        self.not_tutors = not_tutors
        self.tutor_index = 0
        self.time_index = 0
        self.final_tutor = final_tutor
        self.final_time = None
        self.info = additional_info
        self.email_status = False

class Tutor:
    def __init__(self, name, email, grade, availability, courses, not_students, email_status):
        self.name = name
        self.email = email
        self.grade = grade
        self.availability = availability
        self.courses = courses
        self.not_students = not_students
        self.matched_students = []
        self.final_students = {}
        self.final_times = []
        self.email_status = False