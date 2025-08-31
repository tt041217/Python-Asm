import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageOps
from cgpa import *
from reminders import *

class HomePage:
    def __init__(self, master):
        self.master = master
        master.title("Application Home Page")
        master.state("zoomed")  # ✅ start fullscreen (Windows)
        # master.attributes("-fullscreen", True)  # ✅ alternative fullscreen

        # Create gradient background (initial size, will update on resize)
        self.bg_image = self.create_gradient(master.winfo_screenwidth(),
                                             master.winfo_screenheight(),
                                             "#74b9ff", "#a29bfe")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        self.bg_label = tk.Label(master, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Update background when window resizes
        master.bind("<Configure>", self.resize_background)

        # Header
        self.header = tk.Label(master, text="✨ Welcome to My Application Suite ✨", 
                              font=('Helvetica', 26, 'bold'), bg="#3f6e9d", fg="white")
        self.header.pack(pady=30)
        
        # Button frame
        self.button_frame = tk.Frame(master, bg="#74b9ff")
        self.button_frame.pack(expand=True)

        # App cards
        self.create_app_card("cgpa.png", "CGPA & GPA Calculator", 0, 0)
        self.create_app_card("homework.png", "Homework Planner", 0, 1)
        self.create_app_card("reminder.png", "Simple Reminder", 0, 2)

        # Footer
        self.footer = tk.Label(master, text="© 2025 My Applications. All rights reserved.", 
                             font=('Arial', 10), bg="#796565", fg="white")
        self.footer.pack(side='bottom', pady=15)

    def resize_background(self, event):
        """Resize background dynamically when window size changes"""
        w, h = event.width, event.height
        self.bg_image = self.create_gradient(w, h, "#74b9ff", "#a29bfe")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label.config(image=self.bg_photo)
        self.bg_label.image = self.bg_photo

    def create_app_card(self, image_file, text, row, col):
        card = tk.Frame(self.button_frame, bg="white", bd=0, relief="flat")
        card.grid(row=row, column=col, padx=30, pady=10, ipadx=10, ipady=10)

        # Add shadow effect
        card.config(highlightbackground="#b2bec3", highlightthickness=4)

        if self.image_exists(image_file):
            img = Image.open(image_file).resize((180, 180), Image.LANCZOS)
        else:
            img = self.create_default_image(text)

        # Add rounded corners to image
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

        label = tk.Label(card, text=text, font=('Helvetica', 14, 'bold'), bg="white", fg="#343a40")
        label.pack()

        btn.bind("<Button-1>", lambda e: self.open_application(text))
        label.bind("<Button-1>", lambda e: self.open_application(text))

        def on_enter(e):
            card.config(bg="#f1f3f5")
            label.config(fg="#007bff")
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
        draw.text((20, 80), text[:5], fill='black')
        return img

    def open_application(self, app_name):
        if app_name == "CGPA & GPA Calculator":
            calc_window = tk.Toplevel(self.master)
            CalculatorApp(calc_window)
        elif app_name == "Homework Planner":
            messagebox.showinfo("Info", "Opening Homework Planner (to be implemented)")
        elif app_name == "Simple Reminder":
            reminders_window = tk.Toplevel(self.master)
            ReminderApp(reminders_window)
        else:
            messagebox.showinfo("Info", f"Opening {app_name}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HomePage(root)
    root.mainloop()
