import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from cgpa import *

class HomePage:
    def __init__(self, master):
        self.master = master
        master.title("Application Home Page")
        master.geometry("800x600")
        master.configure(bg='#f0f0f0')
        
        # Header
        self.header = tk.Label(master, text="Welcome to My Application Suite", 
                              font=('Arial', 24, 'bold'), bg='#f0f0f0')
        self.header.pack(pady=20)
        
        # Button frame
        self.button_frame = tk.Frame(master, bg='#f0f0f0')
        self.button_frame.pack(expand=True)
        
        # Create buttons
        self.create_image_buttons()
        
        # Footer
        self.footer = tk.Label(master, text="© 2025 My Applications. All rights reserved.", 
                             font=('Arial', 10), bg='#f0f0f0')
        self.footer.pack(side='bottom', pady=10)
    
    def create_image_buttons(self):
        # Button 1 - CGPA/GPA Calculator
        try:
            img1 = Image.open("cgpa.png") if self.image_exists("cgpa.png") else self.create_default_image("CGPA\nGPA")
            img1 = img1.resize((300, 400), Image.LANCZOS)
            self.photo1 = ImageTk.PhotoImage(img1)
            self.btn1 = tk.Button(self.button_frame, image=self.photo1, 
                                 command=lambda: self.open_application("CGPA & GPA Calculator"),
                                 borderwidth=0, bg='#f0f0f0')
            self.btn1.grid(row=0, column=0, padx=20, pady=10)
            self.label1 = tk.Label(self.button_frame, text="CGPA & GPA\nCalculator", 
                                 font=('Arial', 20), bg='#f0f0f0')
            self.label1.grid(row=1, column=0)
        except Exception:
            self.create_text_button("CGPA & GPA Calculator", 0)
            
        
        # Button 2 - Homework Planner
        try:
            img2 = Image.open("homework.png") if self.image_exists("homework.png") else self.create_default_image("Homework")
            img2 = img2.resize((300, 400), Image.LANCZOS)
            self.photo2 = ImageTk.PhotoImage(img2)
            self.btn2 = tk.Button(self.button_frame, image=self.photo2, 
                                 command=lambda: self.open_application("Homework Planner"),
                                 borderwidth=0, bg='#f0f0f0')
            self.btn2.grid(row=0, column=1, padx=20, pady=10)
            self.label2 = tk.Label(self.button_frame, text="Homework Planner", 
                                 font=('Arial', 20), bg='#f0f0f0')
            self.label2.grid(row=1, column=1)
        except Exception:
            self.create_text_button("Homework Planner", 1)
        
        # Button 3 - Simple Reminder
        try:
            img3 = Image.open("reminder.png") if self.image_exists("reminder.png") else self.create_default_image("Reminder")
            img3 = img3.resize((300, 400), Image.LANCZOS)
            self.photo3 = ImageTk.PhotoImage(img3)
            self.btn3 = tk.Button(self.button_frame, image=self.photo3, 
                                 command=lambda: self.open_application("Simple Reminder"),
                                 borderwidth=0, bg='#f0f0f0')
            self.btn3.grid(row=0, column=2, padx=20, pady=10)
            self.label3 = tk.Label(self.button_frame, text="Simple Reminder", 
                                 font=('Arial', 20), bg='#f0f0f0')
            self.label3.grid(row=1, column=2)
        except Exception:
            self.create_text_button("Simple Reminder", 2)
    
    def image_exists(self, filename):
        try:
            with open(filename, 'rb'):
                return True
        except IOError:
            return False
    
    def create_default_image(self, text):
        from PIL import ImageDraw
        img = Image.new('RGB', (200, 200), color='#cccccc')
        draw = ImageDraw.Draw(img)
        draw.text((50, 90), text, fill='black')
        return img
    
    def create_text_button(self, text, column):
        btn = tk.Button(self.button_frame, text=text, 
                        command=lambda: self.open_application(text),
                        font=('Arial', 14), width=15, height=5)
        btn.grid(row=0, column=column, padx=20, pady=10)
        label = tk.Label(self.button_frame, text=text, 
                         font=('Arial', 12), bg='#f0f0f0')
        label.grid(row=1, column=column)
    
    def open_application(self, app_name):
        if app_name == "CGPA & GPA Calculator":
            calc_window = tk.Toplevel(self.master)
            CalculatorApp(calc_window)
        elif app_name == "Homework Planner":
            messagebox.showinfo("Info", "Opening Homework Planner (to be implemented)")
        elif app_name == "Simple Reminder":
            messagebox.showinfo("Info", "Opening Simple Reminder (to be implemented)")
        else:
            messagebox.showinfo("Info", f"Opening {app_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HomePage(root)
    root.mainloop()
