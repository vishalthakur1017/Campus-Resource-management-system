import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import random
import json


class DatabaseManager:
    def __init__(self):
        self.db_name = "campus_management.db"
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Students table
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            semester INTEGER,
            email TEXT
        )''')

        # Faculty table
        cursor.execute('''CREATE TABLE IF NOT EXISTS faculty (
            faculty_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            email TEXT,
            phone TEXT
        )''')

        # Courses table
        cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY,
            course_code TEXT NOT NULL,
            course_name TEXT,
            credits INTEGER,
            department TEXT,
            faculty_id INTEGER,
            FOREIGN KEY (faculty_id) REFERENCES faculty (faculty_id)
        )''')

        # Rooms table
        cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY,
            room_name TEXT NOT NULL,
            capacity INTEGER,
            room_type TEXT,
            building TEXT
        )''')

        # Timetable table
        cursor.execute('''CREATE TABLE IF NOT EXISTS timetable (
            timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            faculty_id INTEGER,
            room_id INTEGER,
            day TEXT,
            time_slot TEXT,
            FOREIGN KEY (course_id) REFERENCES courses (course_id),
            FOREIGN KEY (faculty_id) REFERENCES faculty (faculty_id),
            FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        )''')

        # Insert sample data if tables are empty
        self.insert_sample_data(conn)
        conn.commit()
        conn.close()

    def insert_sample_data(self, conn):
        """Insert sample data into the database"""
        cursor = conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM students")
        if cursor.fetchone()[0] > 0:
            return

        # Sample students
        students_data = [
            (1, 'Alice Johnson', 'CSE', 3, 'alice@college.edu'),
            (2, 'Bob Smith', 'CSE', 3, 'bob@college.edu'),
            (3, 'Carol Davis', 'ECE', 2, 'carol@college.edu'),
            (4, 'David Wilson', 'ECE', 2, 'david@college.edu'),
            (5, 'Eva Brown', 'CSE', 4, 'eva@college.edu')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO students VALUES (?, ?, ?, ?, ?)', students_data)

        # Sample faculty
        faculty_data = [
            (1, 'Dr. Sharma', 'CSE', 'sharma@college.edu', '9876543210'),
            (2, 'Dr. Verma', 'CSE', 'verma@college.edu', '9876543211'),
            (3, 'Dr. Gupta', 'ECE', 'gupta@college.edu', '9876543212'),
            (4, 'Dr. Singh', 'ECE', 'singh@college.edu', '9876543213')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO faculty VALUES (?, ?, ?, ?, ?)', faculty_data)

        # Sample courses
        courses_data = [
            (1, 'CSE101', 'Introduction to Programming', 3, 'CSE', 1),
            (2, 'CSE102', 'Data Structures', 4, 'CSE', 1),
            (3, 'CSE201', 'Algorithms', 4, 'CSE', 2),
            (4, 'ECE101', 'Digital Electronics', 3, 'ECE', 3),
            (5, 'ECE102', 'Signals & Systems', 4, 'ECE', 4),
            (6, 'CSE301', 'Database Systems', 4, 'CSE', 2)
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO courses VALUES (?, ?, ?, ?, ?, ?)', courses_data)

        # Sample rooms
        rooms_data = [
            (1, 'C-101', 60, 'Classroom', 'Main Building'),
            (2, 'C-102', 45, 'Classroom', 'Main Building'),
            (3, 'Lab-201', 30, 'Lab', 'Tech Building'),
            (4, 'Lab-202', 25, 'Lab', 'Tech Building'),
            (5, 'C-103', 50, 'Classroom', 'Main Building')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO rooms VALUES (?, ?, ?, ?, ?)', rooms_data)

    def execute_query(self, query, params=()):
        """Execute query on database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

    def get_all_students(self):
        return self.execute_query("SELECT * FROM students")

    def get_all_faculty(self):
        return self.execute_query("SELECT * FROM faculty")

    def get_all_courses(self):
        return self.execute_query("SELECT * FROM courses")

    def get_all_rooms(self):
        return self.execute_query("SELECT * FROM rooms")

    def get_timetable(self):
        return self.execute_query('''SELECT t.timetable_id, c.course_code, c.course_name, 
                                   f.name, r.room_name, t.day, t.time_slot
                                   FROM timetable t
                                   JOIN courses c ON t.course_id = c.course_id
                                   JOIN faculty f ON t.faculty_id = f.faculty_id
                                   JOIN rooms r ON t.room_id = r.room_id
                                   ORDER BY t.day, t.time_slot''')

    def add_student(self, name, department, semester, email):
        student_id = self.get_next_id("students", "student_id")
        self.execute_query('INSERT INTO students VALUES (?, ?, ?, ?, ?)',
                           (student_id, name, department, semester, email))
        return student_id

    def add_faculty(self, name, department, email, phone):
        faculty_id = self.get_next_id("faculty", "faculty_id")
        self.execute_query('INSERT INTO faculty VALUES (?, ?, ?, ?, ?)',
                           (faculty_id, name, department, email, phone))
        return faculty_id

    def add_course(self, course_code, course_name, credits, department, faculty_id):
        course_id = self.get_next_id("courses", "course_id")
        self.execute_query('INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)',
                           (course_id, course_code, course_name, credits, department, faculty_id))
        return course_id

    def add_room(self, room_name, capacity, room_type, building):
        room_id = self.get_next_id("rooms", "room_id")
        self.execute_query('INSERT INTO rooms VALUES (?, ?, ?, ?, ?)',
                           (room_id, room_name, capacity, room_type, building))
        return room_id

    def get_next_id(self, table_name, id_column):
        """Get next available ID for a table"""
        result = self.execute_query(
            f"SELECT MAX({id_column}) FROM {table_name}")
        max_id = result[0][0] if result[0][0] is not None else 0
        return max_id + 1

    def delete_student(self, student_id):
        self.execute_query(
            "DELETE FROM students WHERE student_id = ?", (student_id,))

    def delete_faculty(self, faculty_id):
        self.execute_query(
            "DELETE FROM faculty WHERE faculty_id = ?", (faculty_id,))

    def delete_course(self, course_id):
        self.execute_query(
            "DELETE FROM courses WHERE course_id = ?", (course_id,))

    def delete_room(self, room_id):
        self.execute_query("DELETE FROM rooms WHERE room_id = ?", (room_id,))

    def generate_timetable(self):
        """Generate a simple random timetable"""
        # Clear existing timetable
        self.execute_query("DELETE FROM timetable")

        courses = self.get_all_courses()
        faculty = self.get_all_faculty()
        rooms = self.get_all_rooms()

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = ['9:00-10:00', '10:00-11:00',
                      '11:00-12:00', '2:00-3:00', '3:00-4:00']

        timetable_data = []

        for course in courses:
            course_id, course_code, course_name, credits, department, faculty_id = course

            # Assign random day and time slot
            day = random.choice(days)
            time_slot = random.choice(time_slots)

            # Assign random room
            room = random.choice(rooms)
            room_id = room[0]

            timetable_data.append(
                (course_id, faculty_id, room_id, day, time_slot))

        # Insert into timetable
        for entry in timetable_data:
            self.execute_query('''INSERT INTO timetable 
                               (course_id, faculty_id, room_id, day, time_slot) 
                               VALUES (?, ?, ?, ?, ?)''', entry)

        return len(timetable_data)


class CampusManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Management System")
        self.root.geometry("1200x700")

        self.db_manager = DatabaseManager()

        self.setup_gui()
        self.load_initial_data()

    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Dashboard Tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")

        # Student Management Tab
        self.students_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.students_frame, text="Students")

        # Faculty Management Tab
        self.faculty_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.faculty_frame, text="Faculty")

        # Course Management Tab
        self.courses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.courses_frame, text="Courses")

        # Room Management Tab
        self.rooms_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rooms_frame, text="Rooms")

        # Timetable Tab
        self.timetable_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.timetable_frame, text="Timetable")

        self.setup_dashboard()
        self.setup_students_tab()
        self.setup_faculty_tab()
        self.setup_courses_tab()
        self.setup_rooms_tab()
        self.setup_timetable_tab()

    def setup_dashboard(self):
        """Setup dashboard tab"""
        welcome_label = ttk.Label(self.dashboard_frame,
                                  text="Campus Management System",
                                  font=('Arial', 16, 'bold'))
        welcome_label.pack(pady=20)

        desc_label = ttk.Label(self.dashboard_frame,
                               text="Simple system for managing students, faculty, courses, rooms and timetable",
                               font=('Arial', 10))
        desc_label.pack(pady=5)

        # Quick stats frame
        stats_frame = ttk.LabelFrame(
            self.dashboard_frame, text="Quick Statistics", padding=15)
        stats_frame.pack(fill='x', padx=50, pady=20)

        # Stats labels
        self.students_count_label = ttk.Label(
            stats_frame, text="Students: Loading...", font=('Arial', 12))
        self.students_count_label.grid(
            row=0, column=0, padx=20, pady=10, sticky='w')

        self.faculty_count_label = ttk.Label(
            stats_frame, text="Faculty: Loading...", font=('Arial', 12))
        self.faculty_count_label.grid(
            row=0, column=1, padx=20, pady=10, sticky='w')

        self.courses_count_label = ttk.Label(
            stats_frame, text="Courses: Loading...", font=('Arial', 12))
        self.courses_count_label.grid(
            row=1, column=0, padx=20, pady=10, sticky='w')

        self.rooms_count_label = ttk.Label(
            stats_frame, text="Rooms: Loading...", font=('Arial', 12))
        self.rooms_count_label.grid(
            row=1, column=1, padx=20, pady=10, sticky='w')

        # Control buttons
        button_frame = ttk.Frame(self.dashboard_frame)
        button_frame.pack(pady=30)

        generate_btn = ttk.Button(button_frame, text="Generate Timetable",
                                  command=self.generate_timetable, width=20)
        generate_btn.grid(row=0, column=0, padx=10)

        refresh_btn = ttk.Button(button_frame, text="Refresh All Data",
                                 command=self.load_initial_data, width=20)
        refresh_btn.grid(row=0, column=1, padx=10)

    def setup_students_tab(self):
        """Setup students management tab"""
        main_frame = ttk.Frame(self.students_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Student buttons
        student_btn_frame = ttk.Frame(main_frame)
        student_btn_frame.pack(fill='x', pady=10)

        ttk.Button(student_btn_frame, text="Add Student",
                   command=self.add_student).pack(side='left', padx=5)
        ttk.Button(student_btn_frame, text="Delete Student",
                   command=self.delete_student).pack(side='left', padx=5)
        ttk.Button(student_btn_frame, text="Refresh",
                   command=self.load_students_data).pack(side='left', padx=5)

        # Students treeview
        columns = ('ID', 'Name', 'Department', 'Semester', 'Email')
        self.students_tree = ttk.Treeview(
            main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(
            main_frame, orient='vertical', command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)

        self.students_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_faculty_tab(self):
        """Setup faculty management tab"""
        main_frame = ttk.Frame(self.faculty_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Faculty buttons
        faculty_btn_frame = ttk.Frame(main_frame)
        faculty_btn_frame.pack(fill='x', pady=10)

        ttk.Button(faculty_btn_frame, text="Add Faculty",
                   command=self.add_faculty).pack(side='left', padx=5)
        ttk.Button(faculty_btn_frame, text="Delete Faculty",
                   command=self.delete_faculty).pack(side='left', padx=5)
        ttk.Button(faculty_btn_frame, text="Refresh",
                   command=self.load_faculty_data).pack(side='left', padx=5)

        # Faculty treeview
        columns = ('ID', 'Name', 'Department', 'Email', 'Phone')
        self.faculty_tree = ttk.Treeview(
            main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.faculty_tree.heading(col, text=col)
            self.faculty_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(
            main_frame, orient='vertical', command=self.faculty_tree.yview)
        self.faculty_tree.configure(yscrollcommand=scrollbar.set)

        self.faculty_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_courses_tab(self):
        """Setup courses management tab"""
        main_frame = ttk.Frame(self.courses_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Course buttons
        course_btn_frame = ttk.Frame(main_frame)
        course_btn_frame.pack(fill='x', pady=10)

        ttk.Button(course_btn_frame, text="Add Course",
                   command=self.add_course).pack(side='left', padx=5)
        ttk.Button(course_btn_frame, text="Delete Course",
                   command=self.delete_course).pack(side='left', padx=5)
        ttk.Button(course_btn_frame, text="Refresh",
                   command=self.load_courses_data).pack(side='left', padx=5)

        # Courses treeview
        columns = ('ID', 'Code', 'Name', 'Credits', 'Department', 'Faculty ID')
        self.courses_tree = ttk.Treeview(
            main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.courses_tree.heading(col, text=col)
            self.courses_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            main_frame, orient='vertical', command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=scrollbar.set)

        self.courses_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_rooms_tab(self):
        """Setup rooms management tab"""
        main_frame = ttk.Frame(self.rooms_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Room buttons
        room_btn_frame = ttk.Frame(main_frame)
        room_btn_frame.pack(fill='x', pady=10)

        ttk.Button(room_btn_frame, text="Add Room",
                   command=self.add_room).pack(side='left', padx=5)
        ttk.Button(room_btn_frame, text="Delete Room",
                   command=self.delete_room).pack(side='left', padx=5)
        ttk.Button(room_btn_frame, text="Refresh",
                   command=self.load_rooms_data).pack(side='left', padx=5)

        # Rooms treeview
        columns = ('ID', 'Name', 'Capacity', 'Type', 'Building')
        self.rooms_tree = ttk.Treeview(
            main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(
            main_frame, orient='vertical', command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scrollbar.set)

        self.rooms_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_timetable_tab(self):
        """Setup timetable display tab"""
        main_frame = ttk.Frame(self.timetable_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=10)

        ttk.Button(control_frame, text="Refresh Timetable",
                   command=self.load_timetable).pack(side='left', padx=5)

        # Timetable treeview
        columns = ('Course Code', 'Course Name',
                   'Faculty', 'Room', 'Day', 'Time Slot')
        self.timetable_tree = ttk.Treeview(
            main_frame, columns=columns, show='headings', height=20)
        for col in columns:
            self.timetable_tree.heading(col, text=col)
            self.timetable_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(
            main_frame, orient='vertical', command=self.timetable_tree.yview)
        self.timetable_tree.configure(yscrollcommand=scrollbar.set)

        self.timetable_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def load_initial_data(self):
        """Load initial data into GUI"""
        self.update_stats()
        self.load_students_data()
        self.load_faculty_data()
        self.load_courses_data()
        self.load_rooms_data()
        self.load_timetable()

    def update_stats(self):
        """Update dashboard statistics"""
        students_count = len(self.db_manager.get_all_students())
        faculty_count = len(self.db_manager.get_all_faculty())
        courses_count = len(self.db_manager.get_all_courses())
        rooms_count = len(self.db_manager.get_all_rooms())

        self.students_count_label.config(text=f"Students: {students_count}")
        self.faculty_count_label.config(text=f"Faculty: {faculty_count}")
        self.courses_count_label.config(text=f"Courses: {courses_count}")
        self.rooms_count_label.config(text=f"Rooms: {rooms_count}")

    def load_students_data(self):
        """Load students data into treeview"""
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        students = self.db_manager.get_all_students()
        for s in students:
            self.students_tree.insert('', 'end', values=s)

    def load_faculty_data(self):
        """Load faculty data into treeview"""
        for item in self.faculty_tree.get_children():
            self.faculty_tree.delete(item)

        faculty = self.db_manager.get_all_faculty()
        for f in faculty:
            self.faculty_tree.insert('', 'end', values=f)

    def load_courses_data(self):
        """Load courses data into treeview"""
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)

        courses = self.db_manager.get_all_courses()
        for c in courses:
            self.courses_tree.insert('', 'end', values=c)

    def load_rooms_data(self):
        """Load rooms data into treeview"""
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)

        rooms = self.db_manager.get_all_rooms()
        for r in rooms:
            self.rooms_tree.insert('', 'end', values=r)

    def load_timetable(self):
        """Load timetable data into treeview"""
        for item in self.timetable_tree.get_children():
            self.timetable_tree.delete(item)

        timetable = self.db_manager.get_timetable()
        for t in timetable:
            self.timetable_tree.insert(
                '', 'end', values=t[1:])  # Skip timetable_id

    def add_student(self):
        """Add new student"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Student")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('name', 'Name:', ''),
            ('department', 'Department:', 'CSE'),
            ('semester', 'Semester:', '3'),
            ('email', 'Email:', '')
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(
                row=i, column=0, sticky='w', padx=10, pady=5)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
            entry.insert(0, default)
            entries[field] = entry

        def save_student():
            try:
                self.db_manager.add_student(
                    entries['name'].get(),
                    entries['department'].get(),
                    int(entries['semester'].get()),
                    entries['email'].get()
                )
                self.load_students_data()
                self.update_stats()
                dialog.destroy()
                messagebox.showinfo("Success", "Student added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid data: {str(e)}")

        ttk.Button(dialog, text="Save", command=save_student).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)

    def delete_student(self):
        """Delete selected student"""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Warning", "Please select a student to delete")
            return

        student_id = self.students_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            self.db_manager.delete_student(student_id)
            self.load_students_data()
            self.update_stats()
            messagebox.showinfo("Success", "Student deleted successfully!")

    def add_faculty(self):
        """Add new faculty"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Faculty")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('name', 'Name:', ''),
            ('department', 'Department:', 'CSE'),
            ('email', 'Email:', ''),
            ('phone', 'Phone:', '')
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(
                row=i, column=0, sticky='w', padx=10, pady=5)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
            entry.insert(0, default)
            entries[field] = entry

        def save_faculty():
            try:
                self.db_manager.add_faculty(
                    entries['name'].get(),
                    entries['department'].get(),
                    entries['email'].get(),
                    entries['phone'].get()
                )
                self.load_faculty_data()
                self.update_stats()
                dialog.destroy()
                messagebox.showinfo("Success", "Faculty added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid data: {str(e)}")

        ttk.Button(dialog, text="Save", command=save_faculty).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)

    def delete_faculty(self):
        """Delete selected faculty"""
        selection = self.faculty_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Warning", "Please select a faculty member to delete")
            return

        faculty_id = self.faculty_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this faculty member?"):
            self.db_manager.delete_faculty(faculty_id)
            self.load_faculty_data()
            self.update_stats()
            messagebox.showinfo("Success", "Faculty deleted successfully!")

    def add_course(self):
        """Add new course"""
        # Get available faculty for dropdown
        faculty = self.db_manager.get_all_faculty()
        faculty_dict = {f[0]: f[1] for f in faculty}

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Course")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('course_code', 'Course Code:', 'CSE'),
            ('course_name', 'Course Name:', ''),
            ('credits', 'Credits:', '3'),
            ('department', 'Department:', 'CSE'),
            ('faculty_id', 'Faculty:', '')
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(
                row=i, column=0, sticky='w', padx=10, pady=5)

            if field == 'faculty_id':
                # Create combobox for faculty selection
                faculty_names = [f"{fid} - {name}" for fid,
                                 name in faculty_dict.items()]
                combo = ttk.Combobox(
                    dialog, values=faculty_names, state='readonly')
                combo.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
                if faculty_names:
                    combo.set(faculty_names[0])
                entries[field] = combo
            else:
                entry = ttk.Entry(dialog)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
                entry.insert(0, default)
                entries[field] = entry

        def save_course():
            try:
                # Get faculty ID from combobox
                faculty_str = entries['faculty_id'].get()
                faculty_id = int(faculty_str.split(' - ')[0])

                self.db_manager.add_course(
                    entries['course_code'].get(),
                    entries['course_name'].get(),
                    int(entries['credits'].get()),
                    entries['department'].get(),
                    faculty_id
                )
                self.load_courses_data()
                self.update_stats()
                dialog.destroy()
                messagebox.showinfo("Success", "Course added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid data: {str(e)}")

        ttk.Button(dialog, text="Save", command=save_course).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)

    def delete_course(self):
        """Delete selected course"""
        selection = self.courses_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Warning", "Please select a course to delete")
            return

        course_id = self.courses_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this course?"):
            self.db_manager.delete_course(course_id)
            self.load_courses_data()
            self.update_stats()
            messagebox.showinfo("Success", "Course deleted successfully!")

    def add_room(self):
        """Add new room"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Room")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ('room_name', 'Room Name:', 'C-'),
            ('capacity', 'Capacity:', '50'),
            ('room_type', 'Room Type:', 'Classroom'),
            ('building', 'Building:', 'Main Building')
        ]

        entries = {}
        for i, (field, label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(
                row=i, column=0, sticky='w', padx=10, pady=5)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky='ew')
            entry.insert(0, default)
            entries[field] = entry

        def save_room():
            try:
                self.db_manager.add_room(
                    entries['room_name'].get(),
                    int(entries['capacity'].get()),
                    entries['room_type'].get(),
                    entries['building'].get()
                )
                self.load_rooms_data()
                self.update_stats()
                dialog.destroy()
                messagebox.showinfo("Success", "Room added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid data: {str(e)}")

        ttk.Button(dialog, text="Save", command=save_room).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
        dialog.columnconfigure(1, weight=1)

    def delete_room(self):
        """Delete selected room"""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a room to delete")
            return

        room_id = self.rooms_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this room?"):
            self.db_manager.delete_room(room_id)
            self.load_rooms_data()
            self.update_stats()
            messagebox.showinfo("Success", "Room deleted successfully!")

    def generate_timetable(self):
        """Generate random timetable"""
        try:
            count = self.db_manager.generate_timetable()
            self.load_timetable()
            messagebox.showinfo(
                "Success", f"Timetable generated successfully with {count} entries!")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to generate timetable: {str(e)}")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CampusManagementApp(root)
    root.mainloop()


if _name_ == "_main_":
    main()
