import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import mysql.connector
from datetime import datetime

class InvoiceApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice")
        self.root.geometry("1920x1080")

        # Initialize database connection
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root123",
                database="dailywages"
            )
            self.db_cursor = self.db_connection.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
            self.root.destroy()
            return

        # Header Frame
        self.header_frame = tk.Frame(root, bg='lightblue', padx=10, pady=10)
        self.header_frame.pack(fill=tk.X)

        # Header Buttons
        buttons = ['Home', 'Invoice', 'Pending Payment', 'Transection', 'Worker Wages', 'Bill Records', 'Logout']
        for btn in buttons:
            button = tk.Button(self.header_frame, font=("helvetica", 10), width=15, text=btn, bg='white', command=lambda b=btn: self.navigate(b))
            button.pack(side=tk.LEFT, padx=10)

        # Form Frame
        self.form_frame = tk.Frame(root)
        self.form_frame.pack(pady=10)

        self.create_form()

        # Search Frame
        self.search_frame = tk.Frame(root)
        self.search_frame.pack(pady=10)

        self.create_search_box()

        # Table Frame
        self.table_frame = tk.Frame(root)
        self.table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.create_table()

        # Footer Frame
        self.footer_frame = tk.Frame(root, bg='lightgray')
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_footer()

        # Load existing data
        self.load_data()

    def create_form(self):
        labels = ['Name', 'Description', 'Date', 'Price', 'Quantity', 'GST Rate']
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.form_frame, text=label, font=("helvetica", 10)).grid(row=i, column=0, padx=10, pady=5, sticky='e')

        self.entries['name'] = tk.Entry(self.form_frame, width=50)
        self.entries['description'] = tk.Entry(self.form_frame, width=50)
        self.entries['date'] = tk.Entry(self.form_frame, width=50)
        self.entries['price'] = tk.Entry(self.form_frame, width=50)
        self.entries['quantity'] = tk.Entry(self.form_frame, width=50)

        gst_options = ['0', '18', '21']
        self.entries['gst'] = ttk.Combobox(self.form_frame, values=gst_options, width=47)
        self.entries['gst'].set('0')

        self.entries['name'].grid(row=0, column=1, padx=10, pady=5)
        self.entries['description'].grid(row=1, column=1, padx=10, pady=5)
        self.entries['date'].grid(row=2, column=1, padx=10, pady=5)
        self.entries['price'].grid(row=3, column=1, padx=10, pady=5)
        self.entries['quantity'].grid(row=4, column=1, padx=10, pady=5)
        self.entries['gst'].grid(row=5, column=1, padx=10, pady=5)

        self.button_frame = tk.Frame(self.form_frame)
        self.button_frame.grid(row=6, column=1, pady=10, sticky='e')
 
        self.submit_button = tk.Button(self.button_frame, width=10, font=("helvetica", 10), text='Submit', command=self.add_to_table)
        self.submit_button.grid(row=0, column=0, padx=10)

        self.edit_button = tk.Button(self.button_frame, width=10, font=("helvetica", 10), text='Edit', command=self.edit_row, state=tk.DISABLED)
        self.edit_button.grid(row=0, column=1, padx=10)

        self.delete_button = tk.Button(self.button_frame, width=10, font=("helvetica", 10), text='Delete', command=self.delete_row, state=tk.DISABLED)
        self.delete_button.grid(row=0, column=2, padx=10)

    def create_search_box(self):
        tk.Label(self.search_frame, text="Search by Name", font=("helvetica", 10)).grid(row=0, column=0, padx=10, pady=5, sticky='e')
        tk.Label(self.search_frame, text="Search by Date", font=("helvetica", 10)).grid(row=1, column=0, padx=10, pady=5, sticky='e')

        self.search_name_entry = tk.Entry(self.search_frame, width=50)
        self.search_date_entry = tk.Entry(self.search_frame, width=50)

        self.search_name_entry.grid(row=0, column=1, padx=10, pady=5)
        self.search_date_entry.grid(row=1, column=1, padx=10, pady=5)

        search_button = tk.Button(self.search_frame, width=10, font=("helvetica", 10), text="Generate PDF", command=self.generate_pdf)
        search_button.grid(row=2, column=1, pady=10)

    def create_table(self):
        columns = ['Name', 'Description', 'Date', 'Price', 'Quantity', 'GST Rate', 'CGST', 'SGST', 'Total (Without GST)', 'Grand Total (With GST)']

        table_container = tk.Frame(self.table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)

        self.table = ttk.Treeview(table_container, columns=columns, show='headings')

        column_widths = [200, 200, 100, 100, 100, 100, 100, 100, 200, 200]
        for col, width in zip(columns, column_widths):
            self.table.heading(col, text=col)
            self.table.column(col, width=width)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.table.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.table.configure(yscrollcommand=self.scrollbar.set)

        self.table.bind('<<TreeviewSelect>>', self.on_select_row)

        self.total_label = tk.Label(self.table_frame, text='Total (Without GST): 0.00')
        self.total_label.pack()

    def create_footer(self):
        left_text = tk.Label(self.footer_frame, font=("helvetica",10), text="2024 © All Rights Reserved By Hisab Kitab.", bg='lightgray')
        left_text.pack(side=tk.LEFT, padx=10, pady=10)

        right_text = tk.Label(self.footer_frame, font=("helvetica",10), text="Made By Sprier Technology Consultancy.", bg='lightgray')
        right_text.pack(side=tk.RIGHT, padx=10, pady=10)

    def load_data(self):
        query = """
        SELECT name, description, date, price, quantity, `gst rate`, cgst, sgst, `total (without gst)`, `grand total (with gst)`
        FROM invoice
        """
        try:
            self.db_cursor.execute(query)
            rows = self.db_cursor.fetchall()

            for row in rows:
                self.table.insert('', 'end', values=row)

            self.update_totals()  # Update totals when data is loaded
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def add_to_table(self):
        try:
            name = self.entries['name'].get()
            description = self.entries['description'].get()
            date = self.entries['date'].get()

            # Validate and format date
            if not self.validate_date(date):
                raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

            price = float(self.entries['price'].get())
            quantity = int(self.entries['quantity'].get())
            gst_rate = float(self.entries['gst'].get())

            # Calculate GST
            cgst = sgst = (price * quantity * gst_rate) / 200
            total_without_gst = (price * quantity)
            grand_total = total_without_gst + cgst + sgst

            # Insert into the database
            insert_query = """
            INSERT INTO invoice (name, description, date, price, quantity, `gst rate`, cgst, sgst, `total (without gst)`, `grand total (with gst)`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, description, date, price, quantity, gst_rate, cgst, sgst, total_without_gst, grand_total)
            self.db_cursor.execute(insert_query, values)
            self.db_connection.commit()

            # Insert into the table view
            self.table.insert('', 'end', values=(name, description, date, price, quantity, gst_rate, cgst, sgst, total_without_gst, grand_total))

            self.clear_form()
            self.update_totals()

            messagebox.showinfo("Success", "Record added successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def on_select_row(self, event):
        selected_item = self.table.selection()
        if selected_item:
            item_values = self.table.item(selected_item)['values']
            self.entries['name'].delete(0, tk.END)
            self.entries['name'].insert(0, item_values[0])
            self.entries['description'].delete(0, tk.END)
            self.entries['description'].insert(0, item_values[1])
            self.entries['date'].delete(0, tk.END)
            self.entries['date'].insert(0, item_values[2])
            self.entries['price'].delete(0, tk.END)
            self.entries['price'].insert(0, item_values[3])
            self.entries['quantity'].delete(0, tk.END)
            self.entries['quantity'].insert(0, item_values[4])
            self.entries['gst'].set(item_values[5])

            self.edit_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)

    def edit_row(self):
        selected_item = self.table.selection()
        if selected_item:
            item_values = self.table.item(selected_item)['values']

            # Update database record
            try:
                name = self.entries['name'].get()
                description = self.entries['description'].get()
                date = self.entries['date'].get()

                if not self.validate_date(date):
                    raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

                price = float(self.entries['price'].get())
                quantity = int(self.entries['quantity'].get())
                gst_rate = float(self.entries['gst'].get())

                # Calculate GST
                cgst = sgst = (price * quantity * gst_rate) / 200
                
                total_without_gst = (price * quantity)
                grand_total = total_without_gst + cgst + sgst

                update_query = """
                UPDATE invoice
                SET description=%s, date=%s, price=%s, quantity=%s, `gst rate`=%s, cgst=%s, sgst=%s, `total (without gst)`=%s, `grand total (with gst)`=%s
                WHERE name=%s AND date=%s
                """
                self.db_cursor.execute(update_query, (description, date, price, quantity, gst_rate, cgst, sgst, total_without_gst, grand_total, item_values[0], item_values[2]))
                self.db_connection.commit()

                # Update table view
                self.table.item(selected_item, values=(name, description, date, price, quantity, gst_rate, cgst, sgst, total_without_gst, grand_total))

                self.clear_form()
                self.edit_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)

                self.update_totals()
                messagebox.showinfo("Success", "Record updated successfully!")

            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_row(self):
        selected_item = self.table.selection()
        if selected_item:
            item_values = self.table.item(selected_item)['values']
            name = item_values[0]
            date = item_values[2]

            # Delete from database
            delete_query = "DELETE FROM invoice WHERE name=%s AND date=%s"
            self.db_cursor.execute(delete_query, (name, date))
            self.db_connection.commit()

            # Delete from table view
            self.table.delete(selected_item)
            self.update_totals()
            messagebox.showinfo("Success", "Record deleted successfully!")

    def update_totals(self):
        total_without_gst = 0
        grand_total_with_gst = 0

        for item in self.table.get_children():
            values = self.table.item(item)['values']
            total_without_gst += values[8]  # 9th column
            grand_total_with_gst += values[9]  # 10th column

        self.total_label.config(text=f'Total (Without GST): {total_without_gst:.2f}')

    def generate_pdf(self):
        name_search = self.search_name_entry.get().strip()
        invoice_number = 'INV-001'
        current_date = datetime.now().strftime("%Y-%m-%d")
        rows = []
        total_without_gst = 0
        grand_total_with_gst = 0

        for item in self.table.get_children():
            values = self.table.item(item)['values']
            if name_search.lower() in values[0].lower():
                rows.append(values)
                total_without_gst += values[8]
                grand_total_with_gst += values[9]

        if not rows:
            messagebox.showwarning("No Records", f"No records found for the name: {name_search}")
            return

        pdf_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if pdf_file_path:
            width = 17 * inch
            height = 10 * inch
            c = canvas.Canvas(pdf_file_path, pagesize=(width, height))

            # Header
            c.setFont("Helvetica-Bold", 20)
            c.drawString(30, height - 30, "Invoice Report")
            c.setFont("Helvetica", 12)
            c.drawString(30, height - 50, "Your Company Name")
            c.drawString(30, height - 70, "Address Line 1")
            c.drawString(30, height - 90, "Address Line 2")
            c.drawString(30, height - 110, "Phone: 9998548565")
            c.drawString(width - 200, height - 110, f"Invoice Number: {invoice_number}")
            c.drawString(width - 200, height - 130, f"Date: {current_date}")
            c.drawString(width - 200, height - 150, f"Search Name: {name_search}")

            # Draw a line for separation
            c.line(30, height - 170, width - 30, height - 170)

            # Table Header (excluding "Name")
            columns = ['Description', 'Date', 'Price', 'Quantity', 'GST Rate', 'CGST', 'SGST', 'Total (Without GST)', 'Grand Total (With GST)']
            c.setFont("Helvetica-Bold", 10)
            y = height - 180
            for idx, col in enumerate(columns):
                c.drawString(30 + idx * 100, y, col)
            y -= 20

            # Draw Table Rows (excluding "Name")
            c.setFont("Helvetica", 10)
            for row in rows:
                for idx, field in enumerate(row[1:]):  # Start from index 1 to skip "Name"
                    c.drawString(30 + idx * 100, y, str(field))
                y -= 20

            # Draw totals with clear labels
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y - 10, f"Total (Without GST): {total_without_gst:.2f}")
            c.drawString(30, y - 30, f"Grand Total (With GST): {grand_total_with_gst:.2f}")

            # Save the PDF
            c.save()
            messagebox.showinfo("Success", "Invoice PDF generated successfully!")

    def navigate(self, section):
        messagebox.showinfo("Navigation", f"Navigating to {section}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
