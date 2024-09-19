import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFile
import os
import mysql.connector

# Ensure the image file does not get truncated
ImageFile.LOAD_TRUNCATED_IMAGES = True

class BillManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bill Record")

        # Set the window size to match the desktop screen size
        self.root.geometry("1920x1080")

        self.images = []  # To store file paths of uploaded images
        self.image_labels = []  # To keep track of image labels in the UI
        self.selected_images = set()  # To keep track of selected images

        # Configure grid layout
        root.grid_rowconfigure(0, weight=0)  # Header row
        root.grid_rowconfigure(1, weight=1)  # Main content row
        root.grid_rowconfigure(2, weight=0)  # Footer row
        root.grid_columnconfigure(0, weight=1)

        # Header Frame
        self.header_frame = tk.Frame(root, bg="lightblue", relief="groove")
        self.header_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        # Header Buttons
        self.create_header_buttons()

        # Main Content Frame (for images and buttons)
        self.main_content_frame = tk.Frame(root)
        self.main_content_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # Button frame for upload, delete, and close
        self.button_frame = tk.Frame(self.main_content_frame, bg="lightgrey", relief="groove", padx=10, pady=10)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        # Upload Button
        self.upload_button = tk.Button(self.button_frame, text="Upload Bills", command=self.upload_bills, font=("helvetica", 10), width=15, bg="white")
        self.upload_button.grid(row=0, column=0, padx=10)

        # Delete Selected Button
        self.delete_selected_button = tk.Button(self.button_frame, text="Delete Selected", command=self.delete_selected_images, font=("helvetica", 10), width=15, bg="white")
        self.delete_selected_button.grid(row=0, column=1, padx=10)

        # Close Button
        self.close_button = tk.Button(self.button_frame, text="Close", command=root.quit, font=("helvetica", 10), width=15, bg="white")
        self.close_button.grid(row=0, column=2, padx=10)

        # Frame for images with vertical scrolling capability
        self.canvas_frame = tk.Frame(self.main_content_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas widget
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create vertical scrollbar and attach it to the canvas
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=self.scrollbar_y.set)

        # Create a frame inside the canvas which will hold the image labels
        self.image_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.image_frame, anchor="nw")

        # Bind frame resize event to update canvas scroll region
        self.image_frame.bind("<Configure>", self.on_frame_configure)

        # Footer Frame
        self.footer_frame = tk.Frame(root, bg="lightgrey", relief="groove")
        self.footer_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

        # Footer Labels
        self.create_footer_labels()

        # Make sure the canvas expands with the window
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Initialize database connection
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="dailywages"
        )
        self.db_cursor = self.db_connection.cursor()

        self.create_table_if_not_exists()
        self.load_images_from_db()

    def create_header_buttons(self):
        buttons = [
            ("Home", lambda: self.navigate('home')),
            ("Invoice", lambda: self.navigate('invoice')),
            ("Pending Payment", lambda: self.navigate('pendingpayment')),
            ("Transaction", lambda: self.navigate('transaction')),
            ("Worker Wages", lambda: self.navigate('workerwages')),
            ("Bill Records", lambda: self.navigate('billrecords')),
            ("Logout", lambda: self.navigate('login'))
        ]
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(self.header_frame, text=text, bg="white", font=("helvetica", 10), width=15, command=command)
            btn.grid(row=0, column=i, padx=10, pady=10)

    def create_footer_labels(self):
        left_label = tk.Label(self.footer_frame, text="2024 © All Rights Reserved By Hisab Kitab", bg="lightgrey", anchor="w", font=("helvetica", 10))
        left_label.pack(side=tk.LEFT, padx=10)

        right_label = tk.Label(self.footer_frame, text="Made By Sprier Technology Consultancy", bg="lightgrey", anchor="e", font=("helvetica", 10))
        right_label.pack(side=tk.RIGHT, padx=10, pady=10)

    def upload_bills(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.images:
                    self.images.append(file_path)
                    self.display_image(file_path)
                    self.save_image_to_db(file_path)

    def display_image(self, file_path):
        try:
            image = Image.open(file_path)
            image.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(image)

            row = len(self.image_labels) // 5
            column = len(self.image_labels) % 5

            image_frame = tk.Frame(self.image_frame, bg="white")
            image_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

            select_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(image_frame, variable=select_var, command=lambda: self.toggle_selection(file_path))
            checkbox.pack()

            label = tk.Label(image_frame, image=photo, cursor="hand2", bg="white")
            label.image = photo  # Keep a reference to avoid garbage collection
            label.pack()
            label.bind("<Button-1>", lambda e, path=file_path: self.open_image_with_default_viewer(path))
            self.image_labels.append((file_path, image_frame))

            self.image_frame.grid_columnconfigure(column, weight=1)
            self.image_frame.grid_rowconfigure(row, weight=1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def toggle_selection(self, file_path):
        if file_path in self.selected_images:
            self.selected_images.remove(file_path)
        else:
            self.selected_images.add(file_path)

    def open_image_with_default_viewer(self, file_path):
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            elif os.name == 'posix':
                subprocess.call(['open', file_path])  # For macOS
            else:
                subprocess.call(['xdg-open', file_path])  # For Linux
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def delete_selected_images(self):
        if not self.selected_images:
            messagebox.showwarning("Warning", "No images selected to delete")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected images?")
        if confirm:
            for file_path in self.selected_images:
                delete_query = "DELETE FROM bills WHERE file_path = %s"
                self.db_cursor.execute(delete_query, (file_path,))
                self.db_connection.commit()

                if file_path in self.images:
                    self.images.remove(file_path)

            self.selected_images.clear()
            self.refresh_image_grid()
            messagebox.showinfo("Info", "Selected images deleted successfully")

    def refresh_image_grid(self):
        for _, image_frame in self.image_labels:
            image_frame.destroy()

        self.image_labels.clear()

        for file_path in self.images:
            self.display_image(file_path)

    def create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS bills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_path VARCHAR(255) NOT NULL
        )
        """
        self.db_cursor.execute(create_table_query)
        self.db_connection.commit()

    def save_image_to_db(self, file_path):
        insert_query = "INSERT INTO bills (file_path) VALUES (%s)"
        self.db_cursor.execute(insert_query, (file_path,))
        self.db_connection.commit()

    def load_images_from_db(self):
        query = "SELECT file_path FROM bills"
        self.db_cursor.execute(query)
        for (file_path,) in self.db_cursor.fetchall():
            self.images.append(file_path)
            self.display_image(file_path)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def navigate(self, page_name):
        scripts = {
            'home': "home.py",
            'invoice': "invoice.py",
            'pendingpayment': "pending.py",
            'transaction': "transaction.py",
            'workerwages': "workerwages.py",
            'billrecords': "bill.py",
            'login': "login.py",
        }
        if page_name in scripts:
            self.root.destroy()
            subprocess.Popen([sys.executable, scripts[page_name]])

if __name__ == "__main__":
    root = tk.Tk()
    app = BillManagerApp(root)
    root.mainloop()
