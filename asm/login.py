import tkinter as tk
from tkinter import messagebox, simpledialog
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
    except Exception:
        return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

class LoginWindow:
    def __init__(self, master, on_success):
        self.master = master
        self.on_success = on_success
        master.title("Login")
        master.state("zoomed")  # For Windows fullscreen

        # Center frame
        center_frame = tk.Frame(master, bg="#f5f5f5")
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="User ID:").pack(pady=5)
        self.id_entry = tk.Entry(center_frame)
        self.id_entry.pack(pady=5)

        tk.Label(center_frame, text="Password:").pack(pady=5)
        self.pw_entry = tk.Entry(center_frame, show="*")
        self.pw_entry.pack(pady=5)

        tk.Button(center_frame, text="Login", command=self.login).pack(pady=5)
        tk.Button(center_frame, text="Register", command=self.register).pack(pady=5)
        tk.Button(center_frame, text="Forgot Password", command=self.forgot_password).pack(pady=5)

    def login(self):
        user_id = self.id_entry.get().strip()
        pw = self.pw_entry.get()
        users = load_users()
        for user in users:
            if user["id"] == user_id and user["password"] == hash_password(pw):
                messagebox.showinfo("Success", "Login successful!")
                self.master.destroy()  # Just close the login window
                return
        messagebox.showerror("Error", "Invalid ID or password.")

    def register(self):
        user_id = self.id_entry.get().strip()
        pw = self.pw_entry.get()
        if not user_id or not pw:
            messagebox.showwarning("Input", "Please enter ID and password.")
            return
        if len(pw) < 8:
            messagebox.showwarning("Input", "Password must be at least 8 characters.")
            return
        users = load_users()
        if any(user["id"] == user_id for user in users):
            messagebox.showerror("Error", "User ID already exists.")
            return
        users.append({"id": user_id, "password": hash_password(pw)})
        save_users(users)
        messagebox.showinfo("Success", "Registration successful!")

    def forgot_password(self):
        user_id = self.id_entry.get().strip()
        if not user_id:
            messagebox.showwarning("Input", "Enter your User ID to reset password.")
            return
        users = load_users()
        for user in users:
            if user["id"] == user_id:
                new_pw = simpledialog.askstring("Reset Password", "Enter new password (min 8 chars):", show="*")
                if new_pw and len(new_pw) >= 8:
                    user["password"] = hash_password(new_pw)
                    save_users(users)
                    messagebox.showinfo("Success", "Password reset successful!")
                else:
                    messagebox.showwarning("Input", "Password too short.")
                return
        messagebox.showerror("Error", "User ID not found.")