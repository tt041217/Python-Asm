import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import json
import os
from datetime import datetime, timedelta
from tkcalendar import DateEntry  # <-- Add this import

DATA_FILE = "reminders.json"

class Reminder:
    def __init__(self, title, dt, note="", repeat="None", status="Pending"):
        self.title = title
        self.datetime = dt  # datetime object
        self.note = note
        self.repeat = repeat
        self.status = status  # "Pending" or "Notified"

    def to_dict(self):
        return {
            "title": self.title,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M"),
            "repeat": self.repeat,
            "note": self.note,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        dt = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
        repeat = data.get("repeat", "None")
        status = data.get("status", "Pending")
        if repeat in ("Daily", "Weekly"):
            return RecurringReminder(
                data["title"], dt, data.get("note", ""), repeat, status
            )
        else:
            return Reminder(
                data["title"], dt, data.get("note", ""), repeat, status
            )

class RecurringReminder(Reminder):
    def __init__(self, title, dt, note="", repeat="None", status="Pending"):
        super().__init__(title, dt, note, repeat, status)
    def next_occurrence(self):
        if self.repeat == "Daily":
            return self.datetime + timedelta(days=1)
        elif self.repeat == "Weekly":
            return self.datetime + timedelta(weeks=1)
        return None

class ReminderApp:
    def __init__(self, master):
        self.master = master
        master.title("Simple Reminder")
        master.geometry("400x500")
        master.configure(bg="#f7f7f7")

        self.reminders = []
        self.load_reminders()
        self.editing_index = None  # Track which reminder is being edited

        # --- Input Frame ---
        input_frame = tk.LabelFrame(master, text="Set a Reminder", bg="#e0f7fa", font=('Arial', 12, 'bold'))
        input_frame.pack(padx=15, pady=15, fill="x")

        tk.Label(input_frame, text="Title:", bg="#e0f7fa", font=('Arial', 11)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(input_frame, font=('Arial', 11))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        tk.Label(input_frame, text="Date:", bg="#e0f7fa", font=('Arial', 11)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = DateEntry(
            input_frame, font=('Arial', 11), date_pattern='yyyy-mm-dd',
            showweeknumbers=False, foreground='gray'
        )
        self.date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        # Simulate blank/placeholder by clearing the entry and setting gray text
        self.date_entry.delete(0, 'end')
        self.date_entry.configure(foreground='gray')

        def on_focus_in(event):
            if self.date_entry.get() == '':
                self.date_entry.configure(foreground='black')
        def on_focus_out(event):
            if self.date_entry.get() == '':
                self.date_entry.configure(foreground='gray')
        self.date_entry.bind("<FocusIn>", on_focus_in)
        self.date_entry.bind("<FocusOut>", on_focus_out)
        self.date_entry.configure(foreground='gray')

        tk.Label(input_frame, text="Time:", bg="#e0f7fa", font=('Arial', 11)).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Create a frame for time selection to avoid grid gaps
        time_frame = tk.Frame(input_frame, bg="#e0f7fa")
        time_frame.grid(row=2, column=1, padx=0, pady=5, sticky="w", columnspan=3)

        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        self.ampm_var = tk.StringVar(value="AM")
        hours = [f"{h:02d}" for h in range(1, 13)]
        minutes = [f"{m:02d}" for m in range(0, 60)]
        ampm = ["AM", "PM"]

        self.hour_menu = ttk.Combobox(time_frame, textvariable=self.hour_var, values=hours, width=2, state="readonly", font=('Arial', 11))
        self.hour_menu.pack(side="left", padx=(0,2))
        self.minute_menu = ttk.Combobox(time_frame, textvariable=self.minute_var, values=minutes, width=2, state="readonly", font=('Arial', 11))
        self.minute_menu.pack(side="left", padx=(0,2))
        self.ampm_menu = ttk.Combobox(time_frame, textvariable=self.ampm_var, values=ampm, width=3, state="readonly", font=('Arial', 11))
        self.ampm_menu.pack(side="left", padx=(0,2))

        tk.Label(input_frame, text="Repeat:", bg="#e0f7fa", font=('Arial', 11)).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.repeat_var = tk.StringVar(value="None")
        repeat_options = ["None", "Daily", "Weekly"]
        self.repeat_menu = ttk.Combobox(input_frame, textvariable=self.repeat_var, values=repeat_options, state="readonly", font=('Arial', 11))
        self.repeat_menu.grid(row=3, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        tk.Label(input_frame, text="Note (optional):", bg="#e0f7fa", font=('Arial', 11)).grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        self.note_text = tk.Text(input_frame, height=3, font=('Arial', 11))
        self.note_text.grid(row=4, column=1, padx=5, pady=5, sticky="ew", columnspan=3)

        input_frame.columnconfigure(1, weight=1)

        self.add_btn = tk.Button(input_frame, text="Add Reminder", command=self.add_reminder, bg="#00796b", fg="white", font=('Arial', 11, 'bold'))
        self.add_btn.grid(row=5, column=0, columnspan=4, pady=10)

        # --- Reminders List ---
        notebook = ttk.Notebook(master)
        notebook.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        # Upcoming Reminders Tab
        upcoming_frame = tk.Frame(notebook, bg="#e0f7fa")
        notebook.add(upcoming_frame, text="Upcoming Reminders")

        self.tree_upcoming = ttk.Treeview(
            upcoming_frame,
            columns=("No", "Title", "DateTime", "Repeat", "Note"),
            show="headings",
            height=8
        )
        for col in ("No", "Title", "DateTime", "Repeat", "Note"):
            self.tree_upcoming.heading(col, text=col)
            self.tree_upcoming.column(col, anchor="center")
        self.tree_upcoming.pack(fill="both", expand=True, padx=5, pady=5)

        # Status Tab
        status_frame = tk.Frame(notebook, bg="#e0f7fa")
        notebook.add(status_frame, text="Status")

        self.tree_status = ttk.Treeview(
            status_frame,
            columns=("No", "Title", "DateTime", "Repeat", "Note", "Status"),
            show="headings",
            height=8
        )
        for col in ("No", "Title", "DateTime", "Repeat", "Note", "Status"):
            self.tree_status.heading(col, text=col)
            self.tree_status.column(col, anchor="center")
        self.tree_status.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons for delete and edit
        btn_frame = tk.Frame(master, bg="#f7f7f7")
        btn_frame.pack(pady=5)
        self.del_btn = tk.Button(btn_frame, text="Delete Selected", command=self.delete_reminder, bg="#d32f2f", fg="white", font=('Arial', 11))
        self.del_btn.pack(side="left", padx=10)

        self.edit_btn = tk.Button(btn_frame, text="Edit Selected", command=self.edit_reminder, bg="#ffa000", fg="white", font=('Arial', 11))
        self.edit_btn.pack(side="left", padx=10)

        self.refresh_btn = tk.Button(btn_frame, text="Refresh", command=self.refresh_list, bg="#1976d2", fg="white", font=('Arial', 11))
        self.refresh_btn.pack(side="left", padx=10)

        self.refresh_list()
        self.running = True
        self.check_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.check_thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_reminder(self):
        title = self.title_entry.get().strip()
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d")
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        ampm = self.ampm_var.get()
        repeat = self.repeat_var.get()
        note = self.note_text.get("1.0", tk.END).strip()

        # Convert to 24-hour format
        if ampm == "PM" and hour != 12:
            hour += 12
        if ampm == "AM" and hour == 12:
            hour = 0
        time_str = f"{hour:02d}:{minute:02d}"

        if not title:
            messagebox.showwarning("Input Error", "Title is required.")
            return
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            if dt < datetime.now():
                messagebox.showwarning("Input Error", "Date and time must be in the future.")
                return
        except Exception:
            messagebox.showwarning("Input Error", "Invalid date or time format.")
            return

        # Use OOP classes
        if repeat in ("Daily", "Weekly"):
            reminder = RecurringReminder(title, dt, note, repeat)
        else:
            reminder = Reminder(title, dt, note, repeat)

        if self.editing_index is not None:
            # Update existing reminder
            self.reminders[self.editing_index] = reminder
            self.editing_index = None
            self.add_btn.config(text="Add Reminder", bg="#00796b")
            messagebox.showinfo("Reminder Updated", "Your reminder has been updated.")
        else:
            # Add new reminder
            self.reminders.append(reminder)
            messagebox.showinfo("Reminder Added", "Your reminder has been added.")

        self.save_reminders()
        self.refresh_list()
        self.clear_inputs()

    def edit_reminder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a reminder to edit.")
            return
        idx = int(selected[0])
        rem = self.reminders[idx]
        # Fill the input fields with the selected reminder's data
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, rem.title)
        dt = rem.datetime
        self.date_entry.set_date(dt)
        hour = dt.strftime("%I")
        minute = dt.strftime("%M")
        ampm = dt.strftime("%p")
        self.hour_var.set(hour)
        self.minute_var.set(minute)
        self.ampm_var.set(ampm)
        self.repeat_var.set(rem.repeat)
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", rem.note)
        self.editing_index = idx
        self.add_btn.config(text="Update Reminder", bg="#388e3c")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.date_entry.set_date(datetime.now())
        self.hour_var.set("12")
        self.minute_var.set("00")
        self.ampm_var.set("AM")
        self.repeat_var.set("None")
        self.note_text.delete("1.0", tk.END)
        self.editing_index = None
        self.add_btn.config(text="Add Reminder", bg="#00796b")

    def refresh_list(self):
        # Upcoming
        for row in self.tree_upcoming.get_children():
            self.tree_upcoming.delete(row)
        # Status
        for row in self.tree_status.get_children():
            self.tree_status.delete(row)

        now = datetime.now()
        idx_upcoming = 1
        idx_status = 1
        for rem in self.reminders:
            if not hasattr(rem, "title") or not hasattr(rem, "datetime") or not hasattr(rem, "repeat"):
                continue
            dt_str = rem.datetime.strftime("%Y-%m-%d %I:%M %p")
            repeat = rem.repeat
            note = rem.note
            display_note = (note[:40] + "...") if len(note) > 43 else note

            if rem.status == "Pending" and rem.datetime >= now:
                self.tree_upcoming.insert(
                    "", "end", iid=idx_upcoming,
                    values=(idx_upcoming, rem.title, dt_str, repeat, display_note)
                )
                idx_upcoming += 1
            else:
                self.tree_status.insert(
                    "", "end", iid=idx_status,
                    values=(idx_status, rem.title, dt_str, repeat, display_note, rem.status)
                )
                idx_status += 1

    def delete_reminder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a reminder to delete.")
            return
        idx = int(selected[0])
        del self.reminders[idx]
        self.save_reminders()
        self.refresh_list()
        messagebox.showinfo("Deleted", "Reminder deleted.")

    def load_reminders(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    loaded = json.load(f)
                    # Only keep valid reminders and use OOP
                    self.reminders = [
                        Reminder.from_dict(rem)
                        for rem in loaded
                        if all(k in rem for k in ("title", "datetime", "repeat"))
                    ]
            except Exception:
                self.reminders = []

    def save_reminders(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump([rem.to_dict() for rem in self.reminders], f, indent=4)
        except Exception:
            pass

    def check_reminders(self):
        while self.running:
            now = datetime.now().replace(second=0, microsecond=0)
            for rem in self.reminders:
                if rem.status == "Pending" and rem.datetime == now:
                    self.show_notification(rem)
                    rem.status = "Notified"
                    # Handle repeat using OOP
                    if isinstance(rem, RecurringReminder):
                        next_dt = rem.next_occurrence()
                        if next_dt:
                            rem.datetime = next_dt
                            rem.status = "Pending"
                    self.save_reminders()
                    self.refresh_list()
            time.sleep(30)  # Check every 30 seconds

    def show_notification(self, rem):
        def popup():
            note = rem.note
            msg = f"{rem.title}\n\n{note}" if note else rem.title
            messagebox.showinfo("Reminder!", msg)
        self.master.after(0, popup)

    def on_close(self):
        self.running = False
        self.save_reminders()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()

