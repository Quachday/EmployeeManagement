'''
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from sqlite3 import Error

class EmployeeManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System")

        # Database connection
        self.connection = self.create_connection("data/employee_management.db")
        self.create_tables()
        self.create_dummy_data()  # Create dummy data for testing
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Position", "Department ID", "Salary"), show='headings')
        self.set_employee_view()  # Set up the tree view
        self.create_widgets()

    def create_connection(self, db_file):
        """Create a database connection to the SQLite database."""
        try:
            connection = sqlite3.connect(db_file)
            print("Connection to SQLite DB successful")
            return connection
        except Error as e:
            messagebox.showerror("Error", f"The error '{e}' occurred")
            return None

    def create_tables(self):
        """Create tables if they don't exist."""
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS employee;")
        cursor.execute("DROP TABLE IF EXISTS departments;")

        # Create departments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """)
        # Create employee table with department_id
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            salary REAL NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        );
        """)
        self.connection.commit()
        cursor.close()

    def create_dummy_data(self):
        """Insert dummy data into the database."""
        cursor = self.connection.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM employee;")
        cursor.execute("DELETE FROM departments;")

        # Create departments
        departments = [
            ("Human Resources",),
            ("Development",),
            ("Marketing",),
            ("Sales",),
            ("Finance",)
        ]
        cursor.executemany("INSERT INTO departments (name) VALUES (?)", departments)

        # Get the department IDs
        cursor.execute("SELECT id FROM departments;")
        department_ids = cursor.fetchall()

        # Create employees using department IDs
        employees = [
            ("Alice", "Manager", department_ids[0][0], 60000),  # HR
            ("Bob", "Developer", department_ids[1][0], 80000),  # Development
            ("Charlie", "Sales Rep", department_ids[3][0], 50000),  # Sales
            ("Diana", "Marketing Specialist", department_ids[2][0], 55000),  # Marketing
            ("Evan", "Accountant", department_ids[4][0], 70000)  # Finance
        ]

        cursor.executemany("INSERT INTO employee (name, position, department_id, salary) VALUES (?, ?, ?, ?)", employees)

        self.connection.commit()
        cursor.close()
        print("Dummy data created.")

    def create_widgets(self):
        # Employee Form
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Name").grid(row=0, column=0)
        tk.Label(form_frame, text="Position").grid(row=0, column=1)
        tk.Label(form_frame, text="Department").grid(row=0, column=2)
        tk.Label(form_frame, text="Salary").grid(row=0, column=3)

        self.name_entry = tk.Entry(form_frame)
        self.position_entry = tk.Entry(form_frame)
        self.department_entry = tk.Entry(form_frame)
        self.salary_entry = tk.Entry(form_frame)

        self.name_entry.grid(row=1, column=0)
        self.position_entry.grid(row=1, column=1)
        self.department_entry.grid(row=1, column=2)
        self.salary_entry.grid(row=1, column=3)

        tk.Button(form_frame, text="Add Employee", command=self.add_employee).grid(row=1, column=4, padx=5)
        tk.Button(form_frame, text="Update Employee", command=self.update_employee).grid(row=1, column=5, padx=5)
        tk.Button(form_frame, text="Delete Employee", command=self.delete_employee).grid(row=1, column=6, padx=5)
        tk.Button(form_frame, text="Show by department", command=self.load_employees_with_departments).grid(row=1, column=7, padx=5)
        tk.Button(form_frame, text="Show total salary by department", command=self.load_total_salaries_by_department).grid(row=1, column=8, padx=5)
        # Employee List


        self.load_employee()
    def set_employee_view(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Position", "Department", "Salary"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Position", text="Position")
        self.tree.heading("Department", text="Department")
        self.tree.heading("Salary", text="Salary")
        self.tree.pack(pady=20)

    def load_employee(self):
        self.tree.destroy()
        self.set_employee_view()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT * FROM employee"
        cursor = self.connection.cursor()
        cursor.execute(query)
        employee = cursor.fetchall()
        for employee in employee:
            self.tree.insert("", "end", values=employee)
        cursor.close()

    def add_employee(self):
        name = self.name_entry.get()
        position = self.position_entry.get()
        department = self.department_entry.get()
        salary = self.salary_entry.get()

        if name and position and department and salary:
            query = "INSERT INTO employee (name, position, department, salary) VALUES (%s, %s, %s, %s)"
            cursor = self.connection.cursor()
            cursor.execute(query, (name, position, department, salary))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Employee added successfully.")
            self.load_employee()
            self.clear_entries()
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    def update_employee(self):


        name = self.name_entry.get().strip()  # Remove leading/trailing spaces
        position = self.position_entry.get().strip()
        department = self.department_entry.get().strip()
        salary = self.salary_entry.get().strip()


        # Check if all fields are empty
        if not name and not position and not department and not salary:
            messagebox.showwarning("Input Error", "No changes made. Please enter at least one field to update.")
            self.load_employee()  # Reload the employee data
            return  # Exit the method early
        else: 
            selected_item = self.tree.selection()
            employee_id = self.tree.item(selected_item[0])['values'][0]
            # Check if an employee is selected
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select an employee to update.")
                return
            # Prepare the SQL query and parameters
            query = "UPDATE employee SET name = %s, position = %s, department = %s, salary = %s WHERE id = %s"
            
            cursor = self.connection.cursor()
            
            # Fetch the current values from the database for the selected employee
            cursor.execute("SELECT name, position, department, salary FROM employee WHERE id = %s", (employee_id,))
            current_values = cursor.fetchone()

            # Use existing values if no new value is provided
            new_name = name if name else current_values[0]
            new_position = position if position else current_values[1]
            new_department = department if department else current_values[2]
            new_salary = salary if salary else current_values[3]

            # Execute the update only if any fields have changed
            cursor.execute(query, (new_name, new_position, new_department, new_salary, employee_id))
            self.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "Employee updated successfully.")
            self.load_employee()  # Reload employee data to reflect changes
            self.clear_entries()  # Clear input fields
    def delete_employee(self):
        selected_item = self.tree.selection()[0]
        employee_id = self.tree.item(selected_item)['values'][0]

        query = "DELETE FROM employee WHERE id = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (employee_id,))
        self.connection.commit()
        cursor.close()
        messagebox.showinfo("Success", "Employee deleted successfully.")
        self.load_employee()

    def select_employee(self, event):
        selected_item = self.tree.selection()[0]
        employee_data = self.tree.item(selected_item)['values']
        self.clear_entries()
        self.name_entry.insert(0, employee_data[1])
        self.position_entry.insert(0, employee_data[2])
        self.department_entry.insert(0, employee_data[3])
        self.salary_entry.insert(0, employee_data[4])

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.department_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")
    def load_employees_with_departments(self):
        # Clear the existing tree view
        self.tree.destroy()
        self.set_employee_view() 
        # Fetch employees including their department names
        cursor = self.connection.cursor()
        query = """
                SELECT e.id AS employee_id, e.name AS employee_name, 
                    e.position, d.name AS department, e.salary
                FROM employee e
                LEFT JOIN departments d ON e.department_id = d.id
                ORDER BY e.id;
        """
        cursor.execute(query)
        employees = cursor.fetchall()

        # Insert fetched employees into the tree view
        for employee in employees:
            self.tree.insert('', 'end', values=employee)
        
        cursor.close()


    def load_total_salaries_by_department(self):
        # Clear the existing tree view
        self.tree.destroy()
        self.tree = ttk.Treeview(self.root, columns=("department_name", "total_salary"), show='headings')
        self.tree.heading("department_name", text="Department")
        self.tree.heading("total_salary", text="Total salary")

        # Pack the new Treeview into the GUI
        self.tree.pack(pady=20, fill=tk.BOTH, expand=True)
        # Fetch total salary by department
        cursor = self.connection.cursor()
        query = """
        SELECT d.name AS department_name, SUM(e.salary) AS total_salary
        FROM employee e
        JOIN departments d ON e.department_id = d.id
        GROUP BY d.name;
        """
        cursor.execute(query)
        department_totals = cursor.fetchall()

        # Insert fetched department totals into the tree view
        for total in department_totals:
            self.tree.insert('', 'end', values=total)

        cursor.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeManagementApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_connection)
    root.mainloop()
'''
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

def create_connection(db_file):
    """Create a database connection to the SQLite database."""
    try:
        connection = sqlite3.connect(db_file)
        print("Connection to SQLite DB successful")
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

def create_tables():
    """Create tables if they don't exist."""
    connection = create_connection("data/employee_management.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS employee;")
    cursor.execute("DROP TABLE IF EXISTS departments;")

    # Create departments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    """)
    # Create employee table with department_id
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        position TEXT NOT NULL,
        department_id INTEGER NOT NULL,
        salary REAL NOT NULL,
        FOREIGN KEY (department_id) REFERENCES departments (id)
    );
    """)
    connection.commit()
    cursor.close()

def create_dummy_data():
    """Insert dummy data into the database."""
    connection = create_connection("data/employee_management.db")
    cursor = connection.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM employee;")
    cursor.execute("DELETE FROM departments;")

    # Create departments
    departments = [
        ("Human Resources",),
        ("Development",),
        ("Marketing",),
        ("Sales",),
        ("Finance",)
    ]
    cursor.executemany("INSERT INTO departments (name) VALUES (?)", departments)

    # Get the department IDs
    cursor.execute("SELECT id FROM departments;")
    department_ids = cursor.fetchall()

    # Create employees using department IDs
    employees = [
        ("Alice", "Manager", department_ids[0][0], 60000),  # HR
        ("Bob", "Developer", department_ids[1][0], 80000),  # Development
        ("Charlie", "Sales Rep", department_ids[3][0], 50000),  # Sales
        ("Diana", "Marketing Specialist", department_ids[2][0], 55000),  # Marketing
        ("Evan", "Accountant", department_ids[4][0], 70000)  # Finance
    ]

    cursor.executemany("INSERT INTO employee (name, position, department_id, salary) VALUES (?, ?, ?, ?)", employees)
    connection.commit()
    cursor.close()
    print("Dummy data created.")

@app.route('/')
def index():
    connection = create_connection("data/employee_management.db")
    cursor = connection.cursor()
    cursor.execute("SELECT e.id, e.name, e.position, d.name, e.salary FROM employee e JOIN departments d ON e.department_id = d.id")
    employees = cursor.fetchall()
    cursor.close()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    name = request.form['name']
    position = request.form['position']
    department_id = request.form['department_id']
    salary = request.form['salary']

    if name and position and department_id and salary:
        connection = create_connection("data/employee_management.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO employee (name, position, department_id, salary) VALUES (?, ?, ?, ?)",
                       (name, position, department_id, salary))
        connection.commit()
        cursor.close()
        flash('Employee added successfully!', 'success')
    else:
        flash('All fields are required!', 'danger')
    return redirect(url_for('index'))

@app.route('/update/<int:employee_id>', methods=['POST'])
def update_employee(employee_id):
    name = request.form['name']
    position = request.form['position']
    department_id = request.form['department_id']
    salary = request.form['salary']

    connection = create_connection("data/employee_management.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE employee SET name = ?, position = ?, department_id = ?, salary = ? WHERE id = ?",
                   (name, position, department_id, salary, employee_id))
    connection.commit()
    cursor.close()
    flash('Employee updated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    connection = create_connection("data/employee_management.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM employee WHERE id = ?", (employee_id,))
    connection.commit()
    cursor.close()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_tables()  # Create tables at the start
    create_dummy_data()  # Create dummy data for testing
    app.run(host='0.0.0.0', port=5000, debug=True)
