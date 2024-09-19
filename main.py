import tkinter as tk
from login import LoginApp
from home import HomeApp
from invoice import InvoiceApp
from pending import PaymentApp
from transection import TransectionApp
from workerwages import WorkerWagesApp
from bill import BillManagerApp

def run_login_app():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

def run_home_app():
    root = tk.Tk()
    app = HomeApp(root)
    root.mainloop()

def run_invoice_app():
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()

def run_payment_app():
    root = tk.Tk()
    app = PaymentApp(root)
    root.mainloop()

def run_transection_app():
    root = tk.Tk()
    app = TransectionApp(root)
    root.mainloop()

def run_worker_wages_app():
    root = tk.Tk()
    app = WorkerWagesApp(root)
    root.mainloop()

def run_bill_manager_app():
    root = tk.Tk()
    app = BillManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Choose which application to run
    run_login_app()
