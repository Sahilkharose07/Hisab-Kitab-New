import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
import subprocess
import sys

class WorkerWagesApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Worker Wages")
        self.root.geometry("1920x1080")

        # Database connection setup
        self.db_connection = mysql.connector.connect(
          host="localhost",          # Change if your MySQL server is on a different host
                user="root",
               password="root123",              # Your MySQL password
                database="dailywages"   # Your MySQL database name
        )
        self.db_cursor = self.db_connection.cursor()
        
        # Create the database table if it does not exist
        self.create_table_if_not_exists()
        
        self.setup_ui()

    def create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS wages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            date DATE,
            in_time TIME,
            out_time TIME,
            hours_worked FLOAT,
            wage_rate FLOAT,
            total_wage FLOAT
        )
        """
        self.db_cursor.execute(create_table_query)
        self.db_connection.commit()

    def setup_ui(self):
        # Create the header
        header_frame = tk.Frame(self.root, bg="lightblue", padx=10, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Button(header_frame, font=("helvetica",10), width=15, text="Home", bg="white", command=self.show_home).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, font=("helvetica",10), width=15, text="Invoice", bg="white", command=self.open_invoice).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, font=("helvetica",10), width=15, text="Pending Payment", bg="white", command=self.show_pending).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, font=("helvetica",10), width=15, text="Transection", bg="white", command=self.show_transection).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, font=("helvetica",10), width=15, text="Worker Wages", bg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, font=("helvetica",10), width=15, text="Bill Records", bg="white", command=self.show_bill).pack(side=tk.LEFT, padx=10)
        tk.Button(header_frame, font=("helvetica",10), width=15, text="Logout", bg="white", command=self.logout).pack(side=tk.LEFT, padx=10)

        # Create the main content area
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Fields
        input_frame = tk.Frame(main_frame)
        input_frame.pack()

        tk.Label(input_frame, text="Name", font=("helvetica", 10)).grid(row=0, column=0)
        tk.Label(input_frame, text="Date", font=("helvetica", 10)).grid(row=0, column=1)
        tk.Label(input_frame, text="In Time", font=("helvetica", 10)).grid(row=0, column=2)
        tk.Label(input_frame, text="Out Time", font=("helvetica", 10)).grid(row=0, column=3)
        tk.Label(input_frame, text="Hours Worked", font=("helvetica", 10)).grid(row=0, column=4)
        tk.Label(input_frame, text="Wage Rate (per hour)", font=("helvetica", 10)).grid(row=0, column=5)

        self.name_entry = tk.Entry(input_frame)
        self.date_entry = tk.Entry(input_frame)
        self.in_time_entry = tk.Entry(input_frame)
        self.out_time_entry = tk.Entry(input_frame)
        self.hours_work_entry = tk.Entry(input_frame)
        self.wage_rate_entry = tk.Entry(input_frame)

        self.name_entry.grid(row=1, column=0)
        self.date_entry.grid(row=1, column=1)
        self.in_time_entry.grid(row=1, column=2)
        self.out_time_entry.grid(row=1, column=3)
        self.hours_work_entry.grid(row=1, column=4)
        self.wage_rate_entry.grid(row=1, column=5)

        tk.Button(main_frame, font=("helvetica", 10), width=10, text="Add Entry", command=self.add_entry).pack(pady=20)

        # Table
        table_frame = tk.Frame(main_frame)
        table_frame.pack()

        columns = ("Name", "Date", "In Time", "Out Time", "Hours Worked", "Wage Rate", "Total Wage")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=210)
        self.table.pack()

        # Filters
        filter_frame = tk.Frame(main_frame)
        filter_frame.pack(pady=50)

        tk.Label(filter_frame, font=("helvetica", 10), text="Filter by Name").grid(row=0, column=0)
        tk.Label(filter_frame, font=("helvetica", 10), text="Filter by Date").grid(row=0, column=1)
        tk.Label(filter_frame, font=("helvetica", 10), text="Filter by Month").grid(row=0, column=2)
        tk.Label(filter_frame, font=("helvetica", 10), text="Filter by Year").grid(row=0, column=3)

        self.filter_name = tk.Entry(filter_frame)
        self.filter_date = tk.Entry(filter_frame)
        self.filter_month = tk.StringVar()
        self.filter_year = tk.Entry(filter_frame)

        months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_month, values=months)
        month_dropdown.grid(row=1, column=2)

        self.filter_name.grid(row=1, column=0)
        self.filter_date.grid(row=1, column=1)
        self.filter_year.grid(row=1, column=3)

        tk.Button(filter_frame, font=("helvetica", 10), width=10, text="Filter", command=self.filter_entries).grid(row=2, column=0, columnspan=4, pady=20)

        # Total Amount
        total_frame = tk.Frame(main_frame)
        total_frame.pack(pady=10)

        self.total_amount_label = tk.Label(total_frame, font=("helvetica", 10), text="Total Amount: 0.00")
        self.total_amount_label.pack(side="left", padx=10)
        self.filtered_total_amount_label = tk.Label(total_frame, font=("helvetica", 10), text="Filtered Total Amount: 0.00")
        self.filtered_total_amount_label.pack(side="left", padx=10)

        # Edit/Delete Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, font=("helvetica", 10), width=10, text="Edit", command=self.edit_entry).pack(side="left", padx=5)
        tk.Button(button_frame, font=("helvetica", 10), width=10, text="Delete", command=self.delete_entry).pack(side="left", padx=5)

        # Create the footer
        footer_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=10)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(footer_frame, font=("helvetica",10), text="2024 © All Rights Reserved By Hisab Kitab.", bg="lightgray").pack(side=tk.LEFT)
        tk.Label(footer_frame, font=("helvetica",10), text="Made By Sprier Technology Consultancy.", bg="lightgray").pack(side=tk.RIGHT)

        # Initialize the data
        self.update_table()

    def validate_date(self, date_str):
        """Validate the date format as DD/MM/YYYY."""
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def calculate_wage(self, hours, wage_rate):
        try:
            return float(hours) * float(wage_rate)
        except ValueError:
            return 0

    def add_entry(self):
        name = self.name_entry.get()
        date = self.date_entry.get()
        in_time = self.in_time_entry.get()
        out_time = self.out_time_entry.get()
        hours_work = self.hours_work_entry.get()
        wage_rate = self.wage_rate_entry.get()
        
        # Validate date format
        if not self.validate_date(date):
            messagebox.showwarning("Date Error", "Date must be in DD/MM/YYYY format.")
            return
        
        # Convert date to YYYY-MM-DD for SQL storage
        try:
            date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError as e:
            messagebox.showerror("Date Conversion Error", str(e))
            return
        
        wage = self.calculate_wage(hours_work, wage_rate)
        
        if not (name and date and in_time and out_time and hours_work and wage_rate):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            query = """
            INSERT INTO wages (name, date, in_time, out_time, hours_worked, wage_rate, total_wage)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.db_cursor.execute(query, (name, date, in_time, out_time, float(hours_work), float(wage_rate), wage))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            print(f"Error: {err}")
            return

        self.update_table()
        self.clear_entries()

    def update_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        total_amount = 0
        filtered_total_amount = 0

        query = "SELECT * FROM wages"
        filters = []
        conditions = []

        if self.filter_name.get():
            conditions.append("name LIKE %s")
            filters.append(f"%{self.filter_name.get()}%")
        if self.filter_date.get():
            conditions.append("date = %s")
            filters.append(self.filter_date.get())
        if self.filter_month.get():
            conditions.append("MONTH(date) = %s")
            filters.append(str(datetime.strptime(self.filter_month.get(), '%B').month))
        if self.filter_year.get():
            conditions.append("YEAR(date) = %s")
            filters.append(self.filter_year.get())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        try:
            self.db_cursor.execute(query, tuple(filters))
            records = self.db_cursor.fetchall()
            for record in records:
                filtered_total_amount += record[7]  # Total wage from filtered records
                self.table.insert("", "end", values=(record[1], record[2], record[3], record[4], record[5], record[6], record[7]))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            print(f"Error: {err}")
            return

        try:
            query = "SELECT SUM(total_wage) FROM wages"
            self.db_cursor.execute(query)
            total_amount = self.db_cursor.fetchone()[0] or 0  # Get total amount or default to 0
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            print(f"Error: {err}")
            return

        self.total_amount_label.config(text=f"Total Amount: {total_amount:.2f}")
        self.filtered_total_amount_label.config(text=f"Filtered Total Amount: {filtered_total_amount:.2f}")

    def filter_entries(self):
        self.update_table()

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.in_time_entry.delete(0, tk.END)
        self.out_time_entry.delete(0, tk.END)
        self.hours_work_entry.delete(0, tk.END)
        self.wage_rate_entry.delete(0, tk.END)

    def edit_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to edit.")
            return
        
        item = self.table.item(selected_item)
        values = item['values']
        
        self.name_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.in_time_entry.delete(0, tk.END)
        self.out_time_entry.delete(0, tk.END)
        self.hours_work_entry.delete(0, tk.END)
        self.wage_rate_entry.delete(0, tk.END)
        
        self.name_entry.insert(0, values[0])
        self.date_entry.insert(0, values[1])
        self.in_time_entry.insert(0, values[2])
        self.out_time_entry.insert(0, values[3])
        self.hours_work_entry.insert(0, values[4])
        self.wage_rate_entry.insert(0, values[5])
        
        self.delete_entry()
        
        updated_values = (
            self.name_entry.get(), self.date_entry.get(), self.in_time_entry.get(), self.out_time_entry.get(),
            float(self.hours_work_entry.get()), float(self.wage_rate_entry.get()), self.calculate_wage(self.hours_work_entry.get(), self.wage_rate_entry.get())
        )
        
        try:
            query = """
            UPDATE wages
            SET name = %s, date = %s, in_time = %s, out_time = %s, hours_worked = %s, wage_rate = %s, total_wage = %s
            WHERE name = %s AND date = %s
            """
            self.db_cursor.execute(query, (*updated_values, self.name_entry.get(), self.date_entry.get()))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            print(f"Error: {err}")
            return
        
        self.update_table()

    def delete_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return
        
        values = self.table.item(selected_item)['values']
        
        try:
            query = """
            DELETE FROM wages
            WHERE name = %s AND date = %s
            """
            self.db_cursor.execute(query, (values[0], values[1]))
            self.db_connection.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            print(f"Error: {err}")
            return
        
        self.update_table()

    def logout(self):
        self.root.destroy()
        subprocess.run([sys.executable, "login.py"])

    def show_home(self):
        self.root.destroy()
        subprocess.run([sys.executable, "home.py"])

    def open_invoice(self):
        self.root.destroy()
        subprocess.run([sys.executable, "invoice.py"])

    def show_pending(self):
        self.root.destroy()
        subprocess.run([sys.executable, "pending.py"])

    def show_transection(self):
        self.root.destroy()
        subprocess.run([sys.executable, "transection.py"])

    def show_bill(self):
        self.root.destroy()
        subprocess.run([sys.executable, "bill.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkerWagesApp(root)
    root.mainloop()
    # Close the database connection when the application exits
    app.db_connection.close()
