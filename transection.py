import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
import subprocess
import sys

class TransectionApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Transection")
        self.root.geometry("1920x1080")

        # Database connection
        self.db_connection = mysql.connector.connect(
         host="localhost",          # Change if your MySQL server is on a different host
         user="root",
         password="root123",            # Your MySQL password
         database="dailywages"  # Your MySQL database name
        )
        self.db_cursor = self.db_connection.cursor()

        # Create table if it does not exist
        self.create_table_if_not_exists()

        # Track the ID of the record being edited
        self.editing_record_id = None

        # Header
        self.header_frame = tk.Frame(self.root, bg="lightblue", padx=5, pady=5)
        self.header_frame.pack(fill=tk.X)

        self.buttons = {
            "Home": tk.Button(self.header_frame, font=("helvetica",10), width=15, text="Home", bg="white", command=lambda: self.navigate("home")),
            "Invoice": tk.Button(self.header_frame, font=("helvetica",10), width=15, text="Invoice", bg="white", command=lambda: self.navigate("invoice")),
            "Pending Payment": tk.Button(self.header_frame, font=("helvetica",10), width=15, text="Pending Payment", bg="white", command=lambda: self.navigate("pendingpayment")),
            "Transection": tk.Button(self.header_frame, font=("helvetica",10), width=15, text="Transection", bg="white"),
            "Worker Wages": tk.Button(self.header_frame, font=("helvetica",10), width=15, text="Worker Wages", bg="white", command=lambda: self.navigate("workerwages")),
            "Bill Records": tk.Button(self.header_frame, font=("helvetica",10), width=15, text="Bill Records", bg="white", command=lambda: self.navigate("billrecords")),
            "Logout": tk.Button(self.header_frame, text="Logout", bg="white", font=("helvetica",10), width=15, command=lambda: self.navigate("login"))
        }

        for i, (text, btn) in enumerate(self.buttons.items()):
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

        tk.Label(self.main_frame, text="Purpose", font=("helvetica", 10)).grid(row=2, column=0, padx=5, pady=5)
        self.purpose_entry = tk.Entry(self.main_frame, width=50)
        self.purpose_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Amount", font=("helvetica", 10)).grid(row=3, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.main_frame, width=50)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.main_frame, text="Date", font=("helvetica", 10)).grid(row=4, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.main_frame, width=50)
        self.date_entry.grid(row=4, column=1, padx=5, pady=5)

        self.submit_button = tk.Button(self.main_frame, font=("helvetica", 10), width=15, text="Submit", command=self.submit)
        self.submit_button.grid(row=5, column=1, columnspan=3, pady=10)

        # Filter Section
        self.filter_frame = tk.Frame(self.root, padx=10, pady=10)
        self.filter_frame.pack(fill=tk.X)

        tk.Label(self.filter_frame, text="Filter by Month", font=("helvetica", 10)).pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar()
        self.month_dropdown = ttk.Combobox(self.filter_frame, width=20, textvariable=self.month_var, values=[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Label(self.filter_frame, text="Year", font=("helvetica", 10)).pack(side=tk.LEFT, padx=5)
        self.year_entry = tk.Entry(self.filter_frame, width=20)
        self.year_entry.pack(side=tk.LEFT, padx=5)
        self.show_button = tk.Button(self.filter_frame, font=("helvetica", 10), width=15, text="Show", command=self.filter_by_date)
        self.show_button.pack(side=tk.LEFT, padx=5)

        # Table Section
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.table = ttk.Treeview(self.table_frame, columns=("Name", "Description", "Purpose", "Amount", "Date"), show='headings')
        self.table.heading("Name", text="Name")
        self.table.heading("Description", text="Description")
        self.table.heading("Purpose", text="Purpose")
        self.table.heading("Amount", text="Amount")
        self.table.heading("Date", text="Date (DD/MM/YYYY)")
        self.table.pack(fill=tk.BOTH, expand=True)

        # Edit and Delete Buttons
        self.edit_button = tk.Button(self.table_frame, font=("helvetica", 10), text="Edit", command=self.edit, width=10)
        self.edit_button.pack(side=tk.LEFT, padx=10, pady=20)
        self.delete_button = tk.Button(self.table_frame, font=("helvetica", 10), text="Delete", command=self.delete, width=10)
        self.delete_button.pack(side=tk.LEFT, padx=10, pady=20)

        # Filtered Total Amount Display
        self.filtered_total_label = tk.Label(self.table_frame, font=("helvetica", 10), text="Filtered Total Amount: 0.00")
        self.filtered_total_label.pack(side=tk.LEFT, padx=5)

        # Footer
        self.footer_frame = tk.Frame(self.root, bg="lightgray")
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.left_footer = tk.Label(self.footer_frame, font=("helvetica",10), text="2024 © All Rights Reserved By Hisab Kitab.", bg="lightgray")
        self.left_footer.pack(side=tk.LEFT, padx=10, pady=10)

        self.right_footer = tk.Label(self.footer_frame, font=("helvetica",10), text="Made By Sprier Technology Consultancy.", bg="lightgray")
        self.right_footer.pack(side=tk.RIGHT, padx=10, pady=10)

        self.load_records()

    def create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            purpose VARCHAR(255),
            amount DECIMAL(10, 2) NOT NULL,
            transection_date DATE NOT NULL
        )
        """
        self.db_cursor.execute(create_table_query)
        self.db_connection.commit()

    def submit(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        purpose = self.purpose_entry.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()

        if not all([name, description, purpose, amount, date]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return

        try:
            amount = float(amount.replace('', '').replace(',', ''))
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a valid number")
            return

        try:
            date = datetime.strptime(date, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showwarning("Input Error", "Date must be in DD/MM/YYYY format")
            return

        if self.editing_record_id is not None:
            # Update existing record
            query = """
            UPDATE transections 
            SET name=%s, description=%s, purpose=%s, amount=%s, transection_date=%s
            WHERE id=%s
            """
            values = (name, description, purpose, amount, date, self.editing_record_id)
            self.db_cursor.execute(query, values)
            self.db_connection.commit()

            self.editing_record_id = None  # Reset the id
        else:
            # Insert new record
            query = "INSERT INTO transections (name, description, purpose, amount, transection_date) VALUES (%s, %s, %s, %s, %s)"
            values = (name, description, purpose, amount, date)
            self.db_cursor.execute(query, values)
            self.db_connection.commit()

        self.load_records()

        # Clear the entries
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.purpose_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)

    def load_records(self):
        query = "SELECT id, name, description, purpose, amount, transection_date FROM transections"
        self.db_cursor.execute(query)
        rows = self.db_cursor.fetchall()

        self.records = []
        for row in rows:
            self.records.append((
                row[0],  # ID
                row[1],  # Name
                row[2],  # Description
                row[3],  # Purpose
                row[4],  # Amount
                row[5]   # Date (datetime.date object)
            ))

        self.update_table()

    def update_table(self):
        self.table.delete(*self.table.get_children())
        for record in self.records:
            self.table.insert("", tk.END, values=(
                record[1],
                record[2],
                record[3],
                f"{record[4]:,.2f}",
                record[5].strftime("%d/%m/%Y")
            ))
        self.update_filtered_total()

    def update_filtered_total(self):
        filtered_total = sum(record[4] for record in self.records)
        self.filtered_total_label.config(text=f"Filtered Total Amount: {filtered_total:,.2f}")

    def filter_by_date(self):
        month = self.month_var.get()
        year = self.year_entry.get()

        if not month or not year:
            messagebox.showwarning("Input Error", "Please select a month and enter a year")
            return

        try:
            year = int(year)
        except ValueError:
            messagebox.showwarning("Input Error", "Year must be a valid number")
            return

        month_number = datetime.strptime(month, "%B").month

        query = """
        SELECT id, name, description, purpose, amount, transection_date 
        FROM transections 
        WHERE MONTH(transection_date)=%s AND YEAR(transection_date)=%s
        """
        self.db_cursor.execute(query, (month_number, year))
        rows = self.db_cursor.fetchall()

        self.records = []
        for row in rows:
            self.records.append((
                row[0],  # ID
                row[1],  # Name
                row[2],  # Description
                row[3],  # Purpose
                row[4],  # Amount
                row[5]   # Date (datetime.date object)
            ))

        self.update_table()

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
        
        self.purpose_entry.delete(0, tk.END)
        self.purpose_entry.insert(0, values[2])
        
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, values[3].replace('', '').replace(',', ''))
        
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[4])

        # Set the id of the record to be updated
        self.editing_record_id = self.get_record_id(values)

    def get_record_id(self, values):
        query = """
        SELECT id FROM transections 
        WHERE name=%s AND description=%s AND purpose=%s AND amount=%s AND transection_date=%s
        """
        self.db_cursor.execute(query, (
            values[0], 
            values[1], 
            values[2], 
            float(values[3].replace('', '').replace(',', '')), 
            datetime.strptime(values[4], "%d/%m/%Y").date()
        ))
        return self.db_cursor.fetchone()[0]

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
            query = "DELETE FROM transections WHERE id=%s"
            self.db_cursor.execute(query, (record_id,))
            self.db_connection.commit()
            self.load_records()

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
        elif page_name == 'billrecords':
            self.root.destroy()
            subprocess.Popen([sys.executable, "bill.py"])
        elif page_name == 'login':
            self.root.destroy()
            subprocess.Popen([sys.executable, "login.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = TransectionApp(root)
    root.mainloop()
