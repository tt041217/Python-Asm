import tkinter as tk
from tkinter import messagebox, simpledialog, font
import json
import hashlib
import os

USER_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    try:
        with open(USER_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        master.title("Secure Login")
        master.configure(bg="#130513")
        master.geometry("400x400") # Set a fixed size

        # Custom font
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=10, weight="bold")

        # Center frame for modern feel
        main_frame = tk.Frame(master, bg="#130513", padx=30, pady=30, bd=5)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # "Welcome!" label (remove bg="#794545")
        tk.Label(main_frame, text="Welcome!", font=self.label_font, bg="#130513", fg="white").pack(pady=(0, 20))

        # User ID input label (remove bg="#74b9ff")
        tk.Label(main_frame, text="User ID:", font=self.label_font, bg="#130513", fg="white").pack(anchor="w")

        self.id_entry = tk.Entry(main_frame, font=self.label_font, relief="flat", bd=2, width=30)
        self.id_entry.pack(pady=(0, 15))

        # Password input label (already correct)
        tk.Label(main_frame, text="Password:", font=self.label_font, bg="#130513", fg="white").pack(anchor="w")
        self.pw_entry = tk.Entry(main_frame, font=self.label_font, show="*", relief="flat", bd=2, width=30)
        self.pw_entry.pack(pady=(0, 25))

        # Login button
        tk.Button(main_frame, text="Login", font=self.button_font, command=self.login, bg="#3498db", fg="white", activebackground="#2980b9", relief="flat", padx=20, pady=5).pack(fill="x", pady=(0, 10))

        # Register button
        tk.Button(main_frame, text="Register", font=self.button_font, command=self.register, bg="#1abc9c", fg="white", activebackground="#16a085", relief="flat", padx=20, pady=5).pack(fill="x", pady=(0, 10))

        # Forgot Password button
        tk.Button(main_frame, text="Forgot Password", font=self.button_font, command=self.forgot_password, bg="#e74c3c", fg="white", activebackground="#c0392b", relief="flat", padx=20, pady=5).pack(fill="x")

    def login(self):
        user_id = self.id_entry.get().strip()
        pw = self.pw_entry.get()
        users = load_users()
        for user in users:
            if user["id"] == user_id and user["password"] == hash_password(pw):
                messagebox.showinfo("Success", "Login successful!", parent=self.master)
                self.on_success()  # <-- Add this line to trigger homepage
                return
        messagebox.showerror("Error", "Invalid ID or password.", parent=self.master)

    def register(self):
        user_id = self.id_entry.get().strip()
        pw = self.pw_entry.get()
        if not user_id or not pw:
            messagebox.showwarning("Input", "Please enter ID and password.", parent=self.master)
            return
        if len(pw) < 8:
            messagebox.showwarning("Input", "Password must be at least 8 characters.", parent=self.master)
            return
        users = load_users()
        if any(user["id"] == user_id for user in users):
            messagebox.showerror("Error", "User ID already exists.", parent=self.master)
            return
        users.append({"id": user_id, "password": hash_password(pw)})
        save_users(users)
        messagebox.showinfo("Success", "Registration successful!", parent=self.master)
        
    def forgot_password(self):
        user_id = self.id_entry.get().strip()
        if not user_id:
            messagebox.showwarning("Input", "Enter your User ID to reset password.", parent=self.master)
            return
        users = load_users()
        for user in users:
            if user["id"] == user_id:
                new_pw = simpledialog.askstring("Reset Password", "Enter new password (min 8 chars):", show="*", parent=self.master)
                if new_pw and len(new_pw) >= 8:
                    user["password"] = hash_password(new_pw)
                    save_users(users)
                    messagebox.showinfo("Success", "Password reset successful!", parent=self.master)
                else:
                    messagebox.showwarning("Input", "Password too short or invalid.", parent=self.master)
                return
        messagebox.showerror("Error", "User ID not found.", parent=self.master)

if __name__ == "__main__":
    root = tk.Tk()
    def on_login_success():
        # This function would be where you open the main application window
        print("Login was successful! Main application can now start.")
    app = LoginWindow(root, on_login_success)
    root.mainloop()