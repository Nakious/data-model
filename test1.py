import yaml
import csv
from graphviz import Digraph

# Static classes, import data and export to CSV...
# This is to test "idealexport type functionality"

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Person: {self.name}, Age: {self.age}"

class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)
        self.student_id = student_id

    def __str__(self):
        return f"Student: {self.name}, Age: {self.age}, Student ID: {self.student_id}"

class Teacher(Person):
    def __init__(self, name, age, employee_id):
        super().__init__(name, age)
        self.employee_id = employee_id

    def __str__(self):
        return f"Teacher: {self.name}, Age: {self.age}, Employee ID: {self.employee_id}"

class Course:
    def __init__(self, name, teacher=None, students=None, version=1):
        self.name = name
        self.teacher = teacher
        self.students = students if students else []
        self.version = version

    def set_version(self, version):
        self.version = version

    def assign_teacher(self, teacher):
        self.teacher = teacher

    def add_student(self, student):
        self.students.append(student)

    def __str__(self):
        if self.version == 2:
            teacher_name = self.teacher.name if self.teacher else "No teacher assigned"
            return f"Course: {self.name}, Version: {self.version}"
        else:
            teacher_name = self.teacher.name if self.teacher else "No teacher assigned"
            student_list = ", ".join([student.name for student in self.students])
            return f"Course: {self.name}, Teacher: {teacher_name}, Students: {student_list}"

    @property
    def __dict__(self):
        teacher_name = self.teacher.name if self.teacher else "No teacher assigned"
        student_list = ", ".join([student.name for student in self.students])
        return {'name': self.name, 'teacher': teacher_name, 'students': student_list, 'version': self.version}

def import_data(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
        teachers = {}
        students = {}
        courses = []

        # Create Teacher objects
        for teacher_data in data.get('teachers', []):
            teacher = Teacher(teacher_data['name'], teacher_data['age'], teacher_data['employee_id'])
            teachers[teacher_data['name']] = teacher

        # Create Student objects
        for student_data in data.get('students', []):
            student = Student(student_data['name'], student_data['age'], student_data['student_id'])
            students[student_data['name']] = student

        # Create Course objects
        for course_data in data.get('courses', []):
            course = Course(course_data['name'])
            version = course_data.get('version')
            if version:
                course.set_version(version)
            teacher_name = course_data.get('teacher')
            if teacher_name:
                teacher = teachers.get(teacher_name)
                if teacher:
                    course.assign_teacher(teacher)
                else:
                    print(f"Error: Teacher '{teacher_name}' not found for course '{course_data['name']}'")
            else:
                print(f"Error: No teacher assigned for course '{course_data['name']}'")

            for student_name in course_data.get('students', []):
                student = students.get(student_name)
                if student:
                    course.add_student(student)
                else:
                    print(f"Error: Student '{student_name}' not found for course '{course_data['name']}'")

            courses.append(course)

    return teachers, students, courses

# Print the imported data
def print_data(teachers, students, courses):
    for teacher in teachers.values():
        print(teacher)
    for student in students.values():
        print(student)
    for course in courses:
        print(course)
        print(course.__dict__)

# Function to export data to CSV
def export_to_csv(objects, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = objects[0].__dict__.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for obj in objects:
            writer.writerow(obj.__dict__)

# Export data for each class
def export_model_to_csv(teachers, students, courses):
    export_to_csv(list(teachers.values()), 'output/test1_teachers.csv')
    export_to_csv(list(students.values()), 'output/test1_students.csv')
    export_to_csv(courses, 'output/test1_courses.csv')

# Visualise
def visualise_data(teachers, students, courses):
    dot = Digraph()
    for course in courses:
        dot.node(course.name, 'Course: ' + course.name + '\n' + 'Version: ' + str(course.version))
        if course.teacher:
            dot.node(course.teacher.name, 'Teacher: ' + course.teacher.name + '\n' + 'ID: ' + course.teacher.employee_id)
            dot.edge(course.name, course.teacher.name)
        if course.students:
            for student in course.students:
                dot.node(student.name, 'Student: ' + student.name + '\n' + 'ID: ' + student.student_id)
                dot.edge(course.name, student.name)
    dot.render('output/test1', format='png', cleanup=True)

# Import data from YAML file
teachers, students, courses = import_data('data/test1.yaml')
print_data(teachers, students, courses)
export_model_to_csv(teachers, students, courses)
visualise_data(teachers, students, courses)