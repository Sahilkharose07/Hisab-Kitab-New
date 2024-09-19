import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
import subprocess
import sys

class PaymentsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("transection")
        self.root.geometry("1920x1080")

        # Database connection
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="dailywages"
        )
        self.db_cursor = self.db_connection.cursor()

        # Create table if it does not exist
        self.create_table_if_not_exists()

        # Track the ID of the record being edited
        self.editing_record_id = None

        # Header
        self.header_frame = tk.Frame(self.root, bg="lightblue", padx=5, pady=5)
        self.header_frame.pack(fill=tk.X)

        # Navigation Buttons
        self.buttons = {
            "Home": tk.Button(self.header_frame, text="Home", command=lambda: self.navigate("home")),
            "Invoice": tk.Button(self.header_frame, text="Invoice", command=lambda: self.navigate("invoice")),
            "Pending Payment": tk.Button(self.header_frame, text="Pending Payment", command=lambda: self.navigate("pendingpayment")),
            "Transection": tk.Button(self.header_frame, text="Transection", command=lambda: self.navigate("transection")),
            "Worker Wages": tk.Button(self.header_frame, text="Worker Wages", command=lambda: self.navigate("workerwages")),
            "Bill Records": tk.Button(self.header_frame, text="Bill Records", command=lambda: self.navigate("billrecords")),
            "Logout": tk.Button(self.header_frame, text="Logout", command=lambda: self.navigate("login"))
        }

        for btn in self.buttons.values():
            btn.pack(side=tk.LEFT, padx=10, pady=5)

        # Main Section
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.main_frame, text="Name", font=("helvetica", 10)).grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.main_frame, width=50)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Description", font=("helvetica", 10)).grid(row=1, column=0, padx=5, pady=5)
        self.description_entry = tk.Entry(self.main_frame, width=50)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Amount Due", font=("helvetica", 10)).grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.main_frame, width=50)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Due Date (DD/MM/YYYY)", font=("helvetica", 10)).grid(row=3, column=0, padx=5, pady=5)
        self.due_date_entry = tk.Entry(self.main_frame, width=50)
        self.due_date_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Status", font=("helvetica", 10)).grid(row=4, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar(value="Unpaid")
        self.status_dropdown = ttk.Combobox(self.main_frame, textvariable=self.status_var, values=["Paid", "Unpaid"])
        self.status_dropdown.grid(row=4, column=1, padx=5, pady=5)

        self.submit_button = tk.Button(self.main_frame, font=("helvetica", 10), text="Submit", command=self.submit)
        self.submit_button.grid(row=5, column=1, columnspan=3, pady=10)

        # Table Section
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.table = ttk.Treeview(self.table_frame, columns=("Name", "Description", "Amount Due", "Due Date", "Status"), show='headings')
        self.table.heading("Name", text="Name")
        self.table.heading("Description", text="Description")
        self.table.heading("Amount Due", text="Amount Due")
        self.table.heading("Due Date", text="Due Date")
        self.table.heading("Status", text="Status")
        self.table.pack(fill=tk.BOTH, expand=True)

        # Edit and Delete Buttons
        self.edit_button = tk.Button(self.table_frame, font=("helvetica", 10), text="Edit", command=self.edit, width=10)
        self.edit_button.pack(side=tk.LEFT, padx=10, pady=20)
        self.delete_button = tk.Button(self.table_frame, font=("helvetica", 10), text="Delete", command=self.delete, width=10)
        self.delete_button.pack(side=tk.LEFT, padx=10, pady=20)

        # Load records
        self.load_records()

    def create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            amount_due DECIMAL(10, 2),
            due_date DATE,
            paid_unpaid ENUM('Paid', 'Unpaid')
        )
        """
        self.db_cursor.execute(create_table_query)
        self.db_connection.commit()

    def submit(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        amount_due = self.amount_entry.get()
        due_date = self.due_date_entry.get()
        status = self.status_var.get()

        if not all([name, amount_due, due_date]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return

        try:
            amount_due = float(amount_due)
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a valid number")
            return

        try:
            due_date = datetime.strptime(due_date, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showwarning("Input Error", "Due Date must be in DD/MM/YYYY format")
            return

        if self.editing_record_id is not None:
            # Update existing record
            query = """
            UPDATE payments 
            SET name=%s, description=%s, amount_due=%s, due_date=%s, paid_unpaid=%s 
            WHERE id=%s
            """
            values = (name, description, amount_due, due_date, status, self.editing_record_id)
            self.db_cursor.execute(query, values)
            self.db_connection.commit()

            self.editing_record_id = None  # Reset the id
        else:
            # Insert new record
            query = "INSERT INTO payments (name, description, amount_due, due_date, paid_unpaid) VALUES (%s, %s, %s, %s, %s)"
            values = (name, description, amount_due, due_date, status)
            self.db_cursor.execute(query, values)
            self.db_connection.commit()

        self.clear_entries()
        self.load_records()

    def load_records(self):
        for row in self.table.get_children():
            self.table.delete(row)

        query = "SELECT * FROM payments"
        self.db_cursor.execute(query)
        records = self.db_cursor.fetchall()

        for record in records:
            self.table.insert("", "end", values=record[1:])  # Skip the ID

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.status_var.set("Unpaid")

    def edit(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to edit")
            return

        selected_item = selected_item[0]
        values = self.table.item(selected_item, 'values')

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[0])

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, values[1])

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, values[2])

        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, values[3])

        self.status_var.set(values[4])

        # Store the ID of the selected record for updates
        self.editing_record_id = self.get_record_id(values)

    def delete(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete")
            return

        selected_item = selected_item[0]
        values = self.table.item(selected_item, 'values')
        record_id = self.get_record_id(values)

        confirm = messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this record?")
        if confirm:
            query = "DELETE FROM payments WHERE id=%s"
            self.db_cursor.execute(query, (record_id,))
            self.db_connection.commit()
            self.load_records()

    def get_record_id(self, values):
        query = "SELECT id FROM payments WHERE name=%s AND amount_due=%s"
        self.db_cursor.execute(query, (values[0], values[2]))
        record = self.db_cursor.fetchone()
        return record[0] if record else None

    def navigate(self, page_name):
        if page_name == 'home':
            self.root.destroy()
            subprocess.Popen([sys.executable, "home.py"])
        elif page_name == 'invoice':
            self.root.destroy()
            subprocess.Popen([sys.executable, "invoice.py"])
        elif page_name == 'pendingpayment':
            self.root.destroy()
            subprocess.Popen([sys.executable, "pending.py"])
        elif page_name == 'workerwages':
            self.root.destroy()
            subprocess.Popen([sys.executable, "workerwages.py"])
        elif page_name == 'transection':
            self.root.destroy()
            subprocess.Popen([sys.executable, "transection.py"])
        elif page_name == 'billrecords':
            self.root.destroy()
            subprocess.Popen([sys.executable, "bill.py"])
        elif page_name == 'login':
            self.root.destroy()
            subprocess.Popen([sys.executable, "login.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentsApp(root)
    root.mainloop()
