import tkinter as tk
import mysql.connector
import subprocess
import sys
from datetime import datetime, timedelta

# Import the app modules
from invoice import InvoiceApp
# from pending import PaymentApp
from transection import TransectionApp
from workerwages import WorkerWagesApp
from bill import BillManagerApp

class HomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Home App")
        self.root.geometry("1920x1080")

        # Create the header
        self.create_header()

        # Create the section area
        self.create_section_area()

        # Add a month selection dropdown
        self.create_month_menu()

        # Button to refresh data based on selected month
        self.refresh_button = tk.Button(self.root, text="Refresh Data", command=self.update_data)
        self.refresh_button.pack(pady=(10, 10))

        # Create the footer
        self.create_footer()

        # Initialize the data
        self.update_data()

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="lightblue", padx=10, pady=10)
        header_frame.pack(fill=tk.X)

        tk.Button(header_frame, text="Home").pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Invoice", command=self.open_invoice).pack(side=tk.LEFT, padx=5)
        # tk.Button(header_frame, text="Pending Payment", command=self.show_pending).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Transection", command=self.show_transection).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Worker Wages", command=self.show_worker_wages).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Bill Records", command=self.show_bill_records).pack(side=tk.LEFT, padx=5)
        tk.Button(header_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)

    def create_section_area(self):
        self.section_frame = tk.Frame(self.root, padx=10, pady=10)
        self.section_frame.pack(pady=(0, 10), fill=tk.BOTH, expand=True)

        self.total_expense_var = tk.StringVar()
        self.pending_payment_var = tk.StringVar()
        self.worker_wages_var = tk.StringVar()
        self.worker_count_var = tk.StringVar()

        box_labels = ["Total Expense", "Pending Payment", "Worker Wages", "Worker Count"]
        vars = [self.total_expense_var, self.pending_payment_var, self.worker_wages_var, self.worker_count_var]

        for idx, (label_text, var) in enumerate(zip(box_labels, vars)):
            frame = tk.Frame(self.section_frame, padx=20, pady=20, relief=tk.RAISED, borderwidth=2, width=200, height=100)
            frame.grid(row=0, column=idx, padx=10, pady=10, sticky="nsew")

            label = tk.Label(frame, text=label_text)
            label.pack(pady=(10, 0))

            value = tk.Label(frame, textvariable=var, font=("Arial", 14))
            value.pack(pady=(5, 10))

        # Adjust column weights to ensure centering
        for col in range(4):
            self.section_frame.grid_columnconfigure(col, weight=1)

    def create_month_menu(self):
        self.month_var = tk.StringVar()
        months = [datetime.now().strftime("%Y-%m")]  # Start with the current month

        # Populate the month list with the last 12 months
        for i in range(1, 12):
            month = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%Y-%m")
            months.append(month)

        self.month_menu = tk.OptionMenu(self.root, self.month_var, *months)
        self.month_menu.pack(pady=(10, 0))

        # Bind the month change event
        self.month_var.trace_add("write", self.on_month_change)

    def create_footer(self):
        footer_frame = tk.Frame(self.root, bg="lightgray", padx=10, pady=5)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(footer_frame, text="2024 © All Rights Reserved By Hisab Kitab.", bg="lightgray").pack(side=tk.LEFT)
        tk.Label(footer_frame, text="Design By Sprier Technology Consultancy.", bg="lightgray").pack(side=tk.RIGHT)

    def get_worker_count(self, month):
        config = {
            'user': 'root',
            'password': 'root123',
            'host': 'localhost',
            'database': 'dailywages'
        }

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(DISTINCT name) FROM wages WHERE DATE_FORMAT(date, '%Y-%m') = %s", (month,))
        count = cursor.fetchone()[0]

        conn.close()

        return count

    def get_total_wages(self, month):
        config = {
             'user': 'root',
            'password': 'root123',
            'host': 'localhost',
            'database': 'dailywages'
        }

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(total_wage) FROM wages WHERE DATE_FORMAT(date, '%Y-%m') = %s", (month,))
        total = cursor.fetchone()[0]

        conn.close()

        if total is None:
            total = 0

        return total

    def get_unpaid_amount(self, month):
        config = {
             'user': 'root',
            'password': 'root123',
            'host': 'localhost',
            'database': 'dailywages'
        }

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount_due) FROM payments WHERE paid_unpaid = 'unpaid' AND DATE_FORMAT(due_date, '%Y-%m') = %s", (month,))
        total = cursor.fetchone()[0]

        conn.close()

        if total is None:
            total = 0

        return total

    def get_total_expense(self, month):
        config = {
             'user': 'root',
            'password': 'root123',
            'host': 'localhost',
            'database': 'dailywages'
        }

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM transections WHERE DATE_FORMAT(transection_date, '%Y-%m') = %s", (month,))
        total = cursor.fetchone()[0]

        conn.close()

        if total is None:
            total = 0

        return total

    def update_data(self):
        selected_month = self.month_var.get()
        total_expense = self.get_total_expense(selected_month)
        unpaid_amount = self.get_unpaid_amount(selected_month)
        worker_count = self.get_worker_count(selected_month)
        total_wages = self.get_total_wages(selected_month)

        self.total_expense_var.set(f"{total_expense:,.2f}")
        self.pending_payment_var.set(f"{unpaid_amount:,.2f}")
        self.worker_wages_var.set(f"{total_wages:,.2f}")
        self.worker_count_var.set(f"{worker_count}")

    def on_month_change(self, *args):
        self.update_data()

    def logout(self):
        self.root.destroy()
        subprocess.run([sys.executable, "login.py"], check=True)

    def open_invoice(self):
        self.root.withdraw()
        invoice_root = tk.Toplevel(self.root)
        InvoiceApp(invoice_root)

    # def show_pending(self):
    #     self.root.withdraw()
    #     pending_root = tk.Toplevel(self.root)
    #     PaymentApp(pending_root)

    def show_transection(self):
        self.root.withdraw()
        transection_root = tk.Toplevel(self.root)
        TransectionApp(transection_root)

    def show_worker_wages(self):
        self.root.withdraw()
        workerwages_root = tk.Toplevel(self.root)
        WorkerWagesApp(workerwages_root)

    def show_bill_records(self):
        self.root.withdraw()
        bill_root = tk.Toplevel(self.root)
        BillManagerApp(bill_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = HomeApp(root)
    root.mainloop()
