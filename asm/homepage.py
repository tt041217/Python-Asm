import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageOps
from cgpa import *
from homeworkPlanner import *
from reminders import *
from login import LoginWindow
from time import strftime


class HomePage:
    def __init__(self, master):
        self.master = master
        master.title("Application Home Page")
        master.state("zoomed")  # start fullscreen (Windows)

        # Create gradient background (initial size, will update on resize)
        self.bg_image = self.create_gradient(master.winfo_screenwidth(),
                                             master.winfo_screenheight(),
                                             "#74b9ff", "#a29bfe")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = tk.Label(master, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Update background when window resizes
        master.bind("<Configure>", self.resize_background)

        # Header (like a navbar)
        self.header = tk.Label(master, text="✨ Welcome to My TARUMT App ✨",
                               font=('Helvetica', 28, 'bold'),
                               bg="#74b9ff", fg="white", pady=15)
        self.header.pack(fill="x")

        # Clock
        self.clock_label = tk.Label(master, font=('Helvetica', 56, 'bold'),
                                    bg="#74b9ff", fg="white")
        self.clock_label.pack(pady=(30, 5))

        # Date
        self.date_label = tk.Label(master, font=('Helvetica', 20),
                                   bg="#74b9ff", fg="#dfe6e9")
        self.date_label.pack(pady=(0, 30))
        self.update_time()

        # Button frame (cards container)
        self.button_frame = tk.Frame(master, bg="#74b9ff")
        self.button_frame.pack(expand=True)

        # App cards
        self.create_app_card("cgpa.png", "CGPA & GPA Calculator", 0, 0)
        self.create_app_card("homework.png", "Homework Planner", 0, 1)
        self.create_app_card("reminder.png", "Simple Reminder", 0, 2)

        # Footer
        self.footer = tk.Label(master, text="✨ TARUMT Student Assistant App ✨",
                               font=('Arial', 16),
                               bg="#a29bfe", fg="white", pady=8)
        self.footer.pack(side='bottom', fill="x")
        # Logout button (top right)
        self.logout_btn = tk.Button(master, text="Logout", font=('Helvetica', 12, 'bold'), bg="#e17055", fg="white", command=self.logout, relief="flat", padx=15, pady=5)
        self.logout_btn.place(relx=0.98, rely=0.02, anchor="ne")
    def logout(self):
        self.master.destroy()
        # Reopen login window
        root = tk.Tk()
        def on_login_success():
            root.destroy()
            start_main_app()
        LoginWindow(root, on_success=on_login_success)
        root.mainloop()

    # Clock update function
    def update_time(self):
        current_time = strftime('%I:%M:%S %p')
        self.clock_label.config(text=current_time)
        current_date = strftime('%A, %B %d, %Y')
        self.date_label.config(text=current_date)
        self.clock_label.after(1000, self.update_time)

    def resize_background(self, event):
        """Resize background dynamically when window size changes"""
        w, h = event.width, event.height
        self.bg_image = self.create_gradient(w, h, "#74b9ff", "#a29bfe")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label.config(image=self.bg_photo)
        self.bg_label.image = self.bg_photo

    def create_app_card(self, image_file, text, row, col):
        card = tk.Frame(self.button_frame, bg="white", bd=0, relief="flat")
        card.grid(row=row, column=col, padx=50, pady=20, ipadx=15, ipady=15)

        # Shadow effect
        card.config(highlightbackground="#dfe6e9", highlightthickness=3)

        # Load image or placeholder
        if self.image_exists(image_file):
            img = Image.open(image_file).resize((180, 180), Image.LANCZOS)
        else:
            img = self.create_default_image(text)

        # Rounded corners
        img = img.convert("RGBA")
        radius = 30
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha = Image.new('L', img.size, 255)
        w, h = img.size
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        img.putalpha(alpha)

        img = ImageOps.expand(img, border=10, fill="white")
        photo = ImageTk.PhotoImage(img)

        btn = tk.Label(card, image=photo, bg="white", cursor="hand2")
        btn.image = photo
        btn.pack(pady=10)

        label = tk.Label(card, text=text, font=('Helvetica', 14, 'bold'),
                         bg="white", fg="#343a40")
        label.pack()

        # Click bindings
        btn.bind("<Button-1>", lambda e: self.open_application(text))
        label.bind("<Button-1>", lambda e: self.open_application(text))

        # Hover effects
        def on_enter(e):
            card.config(bg="#f8f9fa")
            label.config(fg="#0984e3")

        def on_leave(e):
            card.config(bg="white")
            label.config(fg="#343a40")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

    def create_gradient(self, width, height, color1, color2):
        """Generate vertical gradient background with Pillow"""
        base = Image.new("RGB", (width, height), color1)
        top = Image.new("RGB", (width, height), color2)
        mask = Image.new("L", (width, height))
        mask_data = []
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, (0, 0), mask)
        return base

    def image_exists(self, filename):
        try:
            with open(filename, 'rb'):
                return True
        except IOError:
            return False

    def create_default_image(self, text):
        img = Image.new('RGB', (180, 180), color='#dee2e6')
        draw = ImageDraw.Draw(img)
        draw.text((40, 80), text[:4], fill='black')
        return img

    def open_application(self, app_name):
        import subprocess
        if app_name == "CGPA & GPA Calculator":
            subprocess.Popen(["python", "cgpa.py"])
        elif app_name == "Homework Planner":
            subprocess.Popen(["python", "homeworkPlanner.py"])
        elif app_name == "Simple Reminder":
            subprocess.Popen(["python", "reminders.py"])
        else:
            messagebox.showinfo("Info", f"Opening {app_name}")


def start_main_app():
    root = tk.Tk()
    app = HomePage(root)
    root.mainloop()


if __name__ == "__main__":
    login_success = {"status": False}
    def on_login_success():
        login_success["status"] = True
        login_root.destroy()

    login_root = tk.Tk()
    LoginWindow(login_root, on_success=on_login_success)
    login_root.mainloop()

    if login_success["status"]:
        start_main_app()