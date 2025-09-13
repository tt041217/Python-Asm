import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
from PIL import Image, ImageTk, ImageDraw, ImageFont 
import os # For file existence checks
import json # For data persistence

# Set a file path for data persistence. This file will be created in the same
# directory as the script.
DATA_FILE = "gpa_data.json"

# ==============================================================================
# CGPA & GPA Calculation Logic
# (The core calculation function from your original code, kept as-is)
# ==============================================================================
def calculate_gpa_cgpa(Semester_data):
    """
    Calculates GPA for a single Semester and CGPA for a list of Semesters based on the
    TARUMT grading scheme. It returns a formatted string of the results.

    Args:
        Semester_data (list of lists of dict): A list where each inner list represents
                                                a Semester. Each inner list contains
                                                dictionaries, with each dictionary
                                                representing a course with its
                                                'grade' and 'credit_hours'.

    Returns:
        str: A formatted string containing the GPA for each Semester and the final CGPA.
    """
    # 1. Convert Grades to Grade Points
    # This dictionary has been updated to match your specific grading scheme.
    tarumt_grades = {
        'A' : 4.00, 'A-': 3.67,
        'B+': 3.33, 'B' : 3.00, 'B-': 2.67,
        'C+': 2.33, 'C' : 2.00,
        'F' : 0.00, 'S' : 0.00, 
    }
    
    # Initialize accumulators for CGPA calculation
    results_string = ""
    total_quality_points_all = 0.0
    total_credit_hours_all = 0.0
    
    # Grades that contribute to GPA/CGPA. Note: 'S', 'P', 'W', etc. do not.
    gpa_contributing_grades = {k for k, v in tarumt_grades.items() if v > 0}

    # Iterate through each Semester
    for i, Semester in enumerate(Semester_data):
        results_string += f"\n=================================\n"
        results_string += f"       Semester {i + 1} Results       \n"
        results_string += f"=================================\n\n"
        
        # Initialize accumulators for this Semester
        total_quality_points_Semester = 0.0
        total_credit_hours_Semester = 0.0
        
        # 2. Calculate Quality Points for Each Course
        for course in Semester:
            grade = course['grade'].upper()
            credit_hours = course['credit_hours']
            
            # Check if the grade contributes to GPA before calculation
            if grade in gpa_contributing_grades:
                grade_points = tarumt_grades[grade]
                quality_points = grade_points * credit_hours
                
                total_quality_points_Semester += quality_points
                total_credit_hours_Semester += credit_hours
                
                results_string += (f"Course: {course['course_name']}\n"
                                  f"Grade: {grade} | Credits: {credit_hours}\n"
                                  f"Quality Points: {quality_points:.2f}\n\n")
            elif grade in tarumt_grades:
                results_string += (f"Course: {course['course_name']}\n"
                                  f"Grade: {grade} | Credits: {credit_hours} (Non-contributing)\n\n")
            else:
                results_string += (f"Warning: Grade '{grade}' for {course['course_name']} not recognized.\n\n")

        # 3. Calculate Your GPA
        if total_credit_hours_Semester > 0:
            gpa = total_quality_points_Semester / total_credit_hours_Semester
            results_string += f"--- GPA for Semester {i + 1}: {gpa:.2f} ---\n"
        else:
            results_string += f"--- GPA for Semester {i + 1}: N/A ---\n"
        
        total_quality_points_all += total_quality_points_Semester
        total_credit_hours_all += total_credit_hours_Semester
        
        results_string += "\n"

    # 4. Calculate Your CGPA
    results_string += f"=================================\n"
    results_string += f"        Final CGPA Result        \n"
    results_string += f"=================================\n\n"
    if total_credit_hours_all > 0:
        cgpa = total_quality_points_all / total_credit_hours_all
        results_string += f"Total Quality Points: {total_quality_points_all:.2f}\n"
        results_string += f"Total Credit Hours: {total_credit_hours_all}\n"
        results_string += f"Overall CGPA: {cgpa:.2f}\n"
    else:
        results_string += "Final CGPA: N/A\n"
    results_string += "=================================\n"
    
    return results_string

# ==============================================================================
# CGPA & GPA Calculator Application Class
# (Refactored for improved usability and a cleaner look)
# ==============================================================================
class CalculatorApp:
    def __init__(self, master):
        self.master = master
        master.title("CGPA & GPA Calculator")
        master.geometry("500x700")
        master.configure(bg='#e6f2ff')

        # List of all valid grades for the dropdown menu
        self.tarumt_grades_list = [
            'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C',
            'S', 'F',
        ]
        
        # This is where your data is stored. Each inner list is a Semester.
        self.Semesters_data = [[]]
        self.load_data()
        # Ensure the app saves data when the user closes the window
        master.protocol("WM_DELETE_WINDOW", self.save_data_and_close)

        self.current_Semester_index = 0
        self.selected_course_index = None

        # --- UI LAYOUT IMPROVEMENTS ---
        # Using a grid for a more organized, form-like layout
        self.input_frame = tk.LabelFrame(master, text="Enter Course Data", font=('Arial', 14, 'bold'), bg='#cce6ff', padx=15, pady=15, relief='flat', bd=2)
        self.input_frame.pack(pady=20, padx=20, fill='x')

        self.display_frame = tk.LabelFrame(master, text="Courses Added", font=('Arial', 14, 'bold'), bg='#cce6ff', padx=15, pady=15, relief='flat', bd=2)
        self.display_frame.pack(pady=(0, 20), padx=20, fill='both', expand=True)

        self.button_frame = tk.Frame(master, bg='#e6f2ff')
        self.button_frame.pack(pady=(0, 20))

        # Semester Selector
        self.Semester_label = tk.Label(self.input_frame, text="Semester:", bg='#cce6ff', font=('Arial', 12))
        self.Semester_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.Semester_var = tk.StringVar(master)
        
        self.Semester_menu = tk.OptionMenu(self.input_frame, self.Semester_var, "")
        self.Semester_menu.config(font=('Arial', 12), bg='white')
        self.Semester_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew', columnspan=2)

        # Course Name Input
        self.course_name_label = tk.Label(self.input_frame, text="Course Name:", bg='#cce6ff', font=('Arial', 12))
        self.course_name_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.course_name_entry = tk.Entry(self.input_frame, font=('Arial', 12))
        self.course_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew', columnspan=2)
        
        # Grade Dropdown (Replaced Entry for better usability)
        self.grade_label = tk.Label(self.input_frame, text="Grade:", bg='#cce6ff', font=('Arial', 12))
        self.grade_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.grade_var = tk.StringVar(master)
        self.grade_menu = tk.OptionMenu(self.input_frame, self.grade_var, *self.tarumt_grades_list)
        self.grade_menu.config(font=('Arial', 12), bg='white')
        self.grade_menu.grid(row=2, column=1, padx=5, pady=5, sticky='ew', columnspan=2)
        
        # Credit Hours Input
        self.credits_label = tk.Label(self.input_frame, text="Credit Hours:", bg='#cce6ff', font=('Arial', 12))
        self.credits_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.credits_entry = tk.Entry(self.input_frame, font=('Arial', 12))
        self.credits_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew', columnspan=2)

        # Action Buttons Frame
        self.action_btn_frame = tk.Frame(self.input_frame, bg='#cce6ff')
        self.action_btn_frame.grid(row=4, column=1, columnspan=3, pady=10)
        
        # Define a consistent button size
        btn_width = 12
        btn_height = 2

        # Save/Update button. This button's text and command will change.
        self.add_update_btn = tk.Button(
        self.action_btn_frame, text="Add Course", command=self.save_course,font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white', relief='flat',width=btn_width, height=btn_height)
        self.add_update_btn.pack(side='left',  padx= 5 )

        # The edit and delete buttons are outside the action frame to improve clarity
        self.edit_btn = tk.Button(
        self.button_frame, text="Edit Selected", command=self.edit_course,font=('Arial', 14, 'bold'), bg='#FFC107', relief='flat',width=btn_width, height=btn_height)
        self.edit_btn.pack(side='left', padx=10, pady=5)

        self.delete_btn = tk.Button(
        self.button_frame, text="Delete Selected", command=self.delete_course,font=('Arial', 14, 'bold'), bg='#F44336', fg='white', relief='flat',width=btn_width, height=btn_height)
        self.delete_btn.pack(side='left', padx=10, pady=5)

        self.cancel_edit_btn = tk.Button(
        self.button_frame, text="Cancel Edit", command=self.cancel_edit,font=('Arial', 14), bg='#9E9E9E', relief='flat',width=btn_width, height=btn_height)
        self.cancel_edit_btn.pack(side='left', padx=10, pady=5)
        self.cancel_edit_btn.pack_forget()

        # Listbox to display added courses
        self.listbox = Listbox(
        self.display_frame, font=('Arial', 12), selectmode=tk.SINGLE,bg='white', relief='flat', bd=2)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select) # Added event handler

        self.scrollbar = Scrollbar(self.display_frame, command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # Bottom buttons
        self.calc_btn = tk.Button(
        self.button_frame, text="Calculate CGPA", command=self.calculate,font=('Arial', 14, 'bold'), bg='#2196F3', fg='white', relief='flat',width=btn_width, height=btn_height)
        self.calc_btn.pack(side='left', padx=10)

        self.clear_btn = tk.Button(
        self.button_frame, text="Clear All Data", command=self.clear_data,font=('Arial', 14, 'bold'), bg='#607D8B', fg='white', relief='flat',width=btn_width, height=btn_height)
        self.clear_btn.pack(side='left', padx=10)
        
        self.clear_btn = tk.Button(
        self.button_frame, text="Back ", command=self.back_to_homepage,font=('Arial', 14, 'bold'), bg='#607D8B', fg='white', relief='flat',width=btn_width, height=btn_height)
        self.clear_btn.pack(side='left', padx=10)
        
        self.update_Semester_menu()
        self.update_display()
        self.grade_var.set(self.tarumt_grades_list[0]) # Set initial grade selection
        
        self.footer = tk.Label(master, text="✨ TARUMT Student Assistant App ✨",
                               font=('Arial', 16),
                               bg="#a29bfe", fg="white", pady=8)
        self.footer.pack(side='bottom', fill="x")
    
    def on_listbox_select(self, event):
        """
        Handles listbox selection to automatically set up the edit state.
        """
        selected_indices = self.listbox.curselection()
        if selected_indices:
            self.selected_course_index = selected_indices[0]
            self.edit_course()

    def update_Semester_menu(self):
        """
        Refreshes the OptionMenu with the current list of Semesters and the
        'Add New Semester' option.
        """
        menu = self.Semester_menu['menu']
        menu.delete(0, 'end')
        
        Semester_options = [f"Semester {i + 1}" for i in range(len(self.Semesters_data))]
        Semester_options.append("Add New Semester...")
        
        for option in Semester_options:
            menu.add_command(label=option, command=tk._setit(self.Semester_var, option, self.on_menu_select))
        
        if not self.Semesters_data:
            self.Semester_var.set("Add New Semester...")
        else:
            self.Semester_var.set(f"Semester {self.current_Semester_index + 1}")

    def validate_input(self, course_name, credits_str):
        """
        Helper function to validate user input.
        Returns a tuple: (is_valid, error_message, credit_hours)
        """
        if not course_name.strip():
            return (False, "Course name cannot be empty.", None)
            
        try:
            credit_hours = int(credits_str)
            if credit_hours <= 0:
                return (False, "Credit hours must be a positive integer.", None)
        except ValueError:
            return (False, "Credit hours must be a number.", None)
            
        return (True, "", credit_hours)
        
    def on_menu_select(self, value):
        if value == "Add New Semester...":
            self.add_new_Semester()
        else:
            try:
                Semester_number = int(value.split()[1])
                self.current_Semester_index = Semester_number - 1
                self.update_display()
            except (ValueError, IndexError):
                pass

    def add_new_Semester(self):
        new_index = len(self.Semesters_data)
        self.Semesters_data.append([])
        
        self.update_Semester_menu()
        self.current_Semester_index = new_index
        self.update_display()
        
    def clear_input_fields(self):
        self.course_name_entry.delete(0, tk.END)
        self.grade_var.set(self.tarumt_grades_list[0]) # Reset dropdown
        self.credits_entry.delete(0, tk.END)
        self.course_name_entry.focus()
        
    def save_course(self):
        course_name = self.course_name_entry.get()
        grade = self.grade_var.get()
        credits_str = self.credits_entry.get()
        
        is_valid, error_msg, credit_hours = self.validate_input(course_name, credits_str)
        
        if not is_valid:
            messagebox.showwarning("Input Error", error_msg)
            return

        # Check if we are in 'edit' mode or 'add' mode
        if self.selected_course_index is None:
            # We are adding a new course
            course_data = {'course_name': course_name.strip(), 'grade': grade.upper().strip(), 'credit_hours': credit_hours}
            self.Semesters_data[self.current_Semester_index].append(course_data)
            messagebox.showinfo("Success", f"'{course_name.strip()}' has been added to Semester {self.current_Semester_index + 1}.")
            
        else:
            # We are updating an existing course
            self.update_course(course_name.strip(), grade.upper().strip(), credit_hours)
            
        self.update_display()
        self.clear_input_fields()

    def update_course(self, new_course_name, new_grade, new_credit_hours):
        """
        Updates the data of a previously selected course.
        """
        try:
            course_list = self.Semesters_data[self.current_Semester_index]
            
            course_list[self.selected_course_index]['course_name'] = new_course_name
            course_list[self.selected_course_index]['grade'] = new_grade
            course_list[self.selected_course_index]['credit_hours'] = new_credit_hours
            
            messagebox.showinfo("Success", f"Course '{new_course_name}' has been updated.")
            
            # Reset the edit state
            self.selected_course_index = None
            self.add_update_btn.config(text="Add Course", bg='#4CAF50')
            self.cancel_edit_btn.pack_forget()
            
        except (IndexError, ValueError):
            messagebox.showerror("Update Error", "Could not update the course. Please try again.")

    def delete_course(self):
        """
        Deletes the currently selected course from the Semester data.
        """
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a course to delete.")
            return

        index_to_delete = selected_indices[0]
        course_list = self.Semesters_data[self.current_Semester_index]
        course_name = course_list[index_to_delete]['course_name']
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{course_name}'?"):
            del course_list[index_to_delete]
            messagebox.showinfo("Success", f"'{course_name}' has been deleted.")
            self.update_display()
            self.clear_input_fields()
    
    def edit_course(self):
        """
        Loads the data of the selected course into the input fields for editing.
        """
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select a course to edit.")
            return

        self.selected_course_index = selected_indices[0]
        course_to_edit = self.Semesters_data[self.current_Semester_index][self.selected_course_index]
        
        # Populate input fields with the selected course's data
        self.course_name_entry.delete(0, tk.END)
        self.course_name_entry.insert(0, course_to_edit['course_name'])
        
        self.grade_var.set(course_to_edit['grade']) # Set the dropdown value
        
        self.credits_entry.delete(0, tk.END)
        self.credits_entry.insert(0, str(course_to_edit['credit_hours']))
        
        # Change button text and show the 'Cancel' button
        self.add_update_btn.config(text="Update Course", bg='#2196F3')
        self.cancel_edit_btn.pack(side='left', padx=10, pady=5)

    def cancel_edit(self):
        """
        Cancels the edit operation and resets the input fields and buttons.
        """
        self.selected_course_index = None
        self.add_update_btn.config(text="Add Course", bg='#4CAF50')
        self.cancel_edit_btn.pack_forget()
        self.clear_input_fields()

    def update_display(self):
        """
        Reads and displays the courses for the current Semester in the Listbox.
        """
        self.listbox.delete(0, tk.END)
        if self.current_Semester_index < len(self.Semesters_data):
            current_Semester_courses = self.Semesters_data[self.current_Semester_index]
            
            if not current_Semester_courses:
                self.listbox.insert(tk.END, "(No courses added yet)")
            else:
                for course in current_Semester_courses:
                    course_str = f"Course: {course['course_name']}, Grade: {course['grade']}, Credits: {course['credit_hours']}"
                    self.listbox.insert(tk.END, course_str)
        else:
             self.listbox.insert(tk.END, "(No courses added yet)")

    def calculate(self):
        if not any(self.Semesters_data) or all(not Semester for Semester in self.Semesters_data):
            messagebox.showwarning("No Data", "Please add at least one course to calculate.")
            return

        results_string = calculate_gpa_cgpa(self.Semesters_data)
        self.show_results_window(results_string)

    def show_results_window(self, results_text):
        """
        Creates a new window to display the calculation results.
        """
        results_window = tk.Toplevel(self.master)
        results_window.title("Calculation Results")
        results_window.geometry("450x600")
        results_window.configure(bg='#e6f2ff')
        
        results_frame = tk.Frame(results_window, bg='#e6f2ff', padx=15, pady=15)
        results_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(results_frame, wrap='word', font=('Courier', 12),
                              bg='#cce6ff', fg='#333333', relief='flat')
        text_widget.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(results_frame, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, results_text)
        text_widget.config(state='disabled')
        
        close_btn = tk.Button(results_window, text="Close", command=results_window.destroy,
                              font=('Arial', 12, 'bold'), bg='#2196F3', fg='white', relief='flat')
        close_btn.pack(pady=10)

    def clear_data(self):
        """
        Clears all data and the data file.
        """
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear ALL course data? This action is permanent."):
            self.Semesters_data = [[]]
            self.current_Semester_index = 0
            self.update_Semester_menu()
            self.update_display()
            self.save_data() # Save the now-empty data to the file
            messagebox.showinfo("Data Cleared", "All course data has been cleared.")
            
    def load_data(self):
        """
        Loads the Semesters data from a JSON file if it exists.
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as file:
                    loaded_data = json.load(file)
                    # Check if the loaded data has the correct structure before using it
                    if isinstance(loaded_data, list) and all(isinstance(t, list) for t in loaded_data):
                        self.Semesters_data = loaded_data
                        # Ensure we have at least one Semester list, even if it's empty
                        if not self.Semesters_data:
                            self.Semesters_data.append([])
                        self.current_Semester_index = 0
                    else:
                        print("Warning: Data file content is not in the expected format. Starting with empty data.")
            except json.JSONDecodeError:
                print("Warning: Could not decode JSON from file. File might be corrupted. Starting with empty data.")
            
    def save_data(self):
        """
        Saves the current Semesters data to a JSON file.
        """
        try:
            with open(DATA_FILE, 'w') as file:
                json.dump(self.Semesters_data, file, indent=4)
        except IOError:
            messagebox.showerror("Save Error", "Could not save data to file. Check file permissions.")
    
    def save_data_and_close(self):
        """
        Saves data and then closes the window. This is bound to the window's close button.
        """
        self.save_data()
        self.master.destroy()
        
    # In the CalculatorApp class
    def back_to_homepage(self):
     """
     Closes the current Toplevel window (the calculator) to return to the homepage.
     """
     self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()