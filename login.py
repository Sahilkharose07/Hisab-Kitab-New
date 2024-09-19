import tkinter as tk
import mysql.connector

from home import HomeApp

class LoginApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1920x1080")
        self.create_widgets()

    def create_widgets(self):
     # Create a shadow frame
     shadow_frame = tk.Frame(self.root, bg="#d1d1d1", padx=5, pady=5)
     shadow_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
     # Main Form Frame
     form_frame = tk.Frame(shadow_frame, bg="white", padx=50, pady=50)
     form_frame.grid(row=0, column=0, padx=10, pady=10)

     # Title Label
     title_label = tk.Label(form_frame, text="Login", font=("helvetica", 50), bg="white", fg="#6657f4")
     title_label.grid(row=0, column=0, columnspan=2, pady=(0, 50))
    
     # Username Entry
     self.username_var = tk.StringVar()
     tk.Label(form_frame, text="Username", bg="white", font=("helvetica",10)).grid(row=1, column=0, sticky="w", pady=(0, 20))
     self.username_entry = tk.Entry(form_frame, textvariable=self.username_var, width=50)
     self.username_entry.grid(row=1, column=1, pady=(0, 20))

     # Password Entry
     self.password_var = tk.StringVar()
     tk.Label(form_frame, text="Password", bg="white", font=("helvetica",10)).grid(row=2, column=0, sticky="w", pady=(0, 20))
     self.password_entry = tk.Entry(form_frame, textvariable=self.password_var, show="*", width=50)
     self.password_entry.grid(row=2, column=1, pady=(0, 20))

     # Toggle Password Button
     self.toggle_password_button = tk.Button(form_frame, font=("helvetica",10), text="Show", command=self.toggle_password, width=5, height=1)
     self.toggle_password_button.grid(row=3, column=1, pady=(0, 20), sticky="e")

     # Remember Me Checkbutton
     self.remember_me_var = tk.BooleanVar()
     self.remember_me_check = tk.Checkbutton(form_frame, font=("helvetica",10), text="Remember me", variable=self.remember_me_var, bg="white")
     self.remember_me_check.grid(row=3, column=0, columnspan=2, pady=(0, 20), sticky="w")

     # Login Button
     self.login_button = tk.Button(form_frame, font=("helvetica",10), text="Login", command=self.handle_login, bg="#6657f4", fg="white", width=10)
     self.login_button.grid(row=4, column=0, columnspan=2, pady=(0, 10))

     # Error Label
     self.error_label = tk.Label(form_frame, text="", fg="red", bg="white")
     self.error_label.grid(row=5, column=0, columnspan=2)

    def toggle_password(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.config(show="")
            self.toggle_password_button.config(text="Hide")
        else:
            self.password_entry.config(show="*")
            self.toggle_password_button.config(text="Show")

    def handle_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        remember_me = self.remember_me_var.get()

        if not username or not password:
            self.error_label.config(text="Username and Password are required")
            return

        # Connect to the MySQL database
        try:
            conn = mysql.connector.connect(
                host="localhost",          # Change if your MySQL server is on a different host
                user="root",
               password="root123",              # Your MySQL password
                database="dailywages"      # Your database name
            )
            cursor = conn.cursor()

            # Query to check username and password
            cursor.execute('''
            SELECT * FROM users WHERE username = %s AND password = %s
            ''', (username, password))

            registration = cursor.fetchone()
            conn.close()

            if registration:
                if remember_me:
                    # Save the username (you can save to a file or database)
                    with open("remembered_user.txt", "w") as f:
                        f.write(username)
                
                # Open home.py and close the current window
                self.open_home()
                
            else:
                self.error_label.config(text="Invalid Username or Password")
        except mysql.connector.Error as err:
            self.error_label.config(text=f"Error: {err}")

    def open_home(self):
        self.root.withdraw()
        home_root = tk.Toplevel(self.root)
        HomeApp(home_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
