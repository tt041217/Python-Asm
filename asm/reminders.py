import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "reminders.json"

class Reminder:
    def __init__(self, title, dt, note="", repeat="None"):
        self.title = title
        self.datetime = dt  # datetime object
        self.note = note
        self.repeat = repeat

    def to_dict(self):
        return {
            "title": self.title,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M"),
            "repeat": self.repeat,
            "note": self.note
        }

    @classmethod
    def from_dict(cls, data):
        dt = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
        repeat = data.get("repeat", "None")
        if repeat in ("Daily", "Weekly"):
            return RecurringReminder(
                data["title"], dt, data.get("note", ""), repeat
            )
        else:
            return Reminder(
                data["title"], dt, data.get("note", ""), repeat
            )

class RecurringReminder(Reminder):
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
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        tk.Label(input_frame, text="Date (YYYY-MM-DD):", bg="#e0f7fa", font=('Arial', 11)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, font=('Arial', 11))
        self.date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        tk.Label(input_frame, text="Time (HH:MM):", bg="#e0f7fa", font=('Arial', 11)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.time_entry = tk.Entry(input_frame, font=('Arial', 11))
        self.time_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        tk.Label(input_frame, text="Repeat:", bg="#e0f7fa", font=('Arial', 11)).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.repeat_var = tk.StringVar(value="None")
        repeat_options = ["None", "Daily", "Weekly"]
        self.repeat_menu = ttk.Combobox(input_frame, textvariable=self.repeat_var, values=repeat_options, state="readonly", font=('Arial', 11))
        self.repeat_menu.grid(row=3, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        tk.Label(input_frame, text="Note (optional):", bg="#e0f7fa", font=('Arial', 11)).grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        self.note_text = tk.Text(input_frame, height=3, font=('Arial', 11))
        self.note_text.grid(row=4, column=1, padx=5, pady=5, sticky="ew", columnspan=2)

        input_frame.columnconfigure(1, weight=1)

        self.add_btn = tk.Button(input_frame, text="Add Reminder", command=self.add_reminder, bg="#00796b", fg="white", font=('Arial', 11, 'bold'))
        self.add_btn.grid(row=5, column=0, columnspan=3, pady=10)

        # --- Reminders List ---
        list_frame = tk.LabelFrame(master, text="Upcoming Reminders", bg="#e0f7fa", font=('Arial', 12, 'bold'))
        list_frame.pack(padx=15, pady=(0, 15), fill="both", expand=True)

        # Add "No" column as the first column
        self.tree = ttk.Treeview(
            list_frame,
            columns=("No", "Title", "DateTime", "Repeat", "Note"),
            show="headings",
            height=8
        )
        self.tree.heading("No", text="No")
        self.tree.heading("Title", text="Title")
        self.tree.heading("DateTime", text="Date & Time")
        self.tree.heading("Repeat", text="Repeat")
        self.tree.heading("Note", text="Note")
        self.tree.column("No", width=40, anchor="center")
        self.tree.column("Title", width=120, anchor="center")
        self.tree.column("DateTime", width=120, anchor="center")
        self.tree.column("Repeat", width=60, anchor="center")
        self.tree.column("Note", width=180, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

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
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        repeat = self.repeat_var.get()
        note = self.note_text.get("1.0", tk.END).strip()

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
        dt = rem.datetime.strftime("%Y-%m-%d %H:%M").split()
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, dt[0])
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, dt[1])
        self.repeat_var.set(rem.repeat)
        self.note_text.delete("1.0", tk.END)
        self.note_text.insert("1.0", rem.note)
        self.editing_index = idx
        self.add_btn.config(text="Update Reminder", bg="#388e3c")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.repeat_var.set("None")
        self.note_text.delete("1.0", tk.END)
        self.editing_index = None
        self.add_btn.config(text="Add Reminder", bg="#00796b")

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, rem in enumerate(self.reminders):
            # Skip reminders missing required fields
            if not hasattr(rem, "title") or not hasattr(rem, "datetime") or not hasattr(rem, "repeat"):
                continue
            dt = rem.datetime.strftime("%Y-%m-%d %H:%M")
            repeat = rem.repeat
            note = rem.note
            display_note = (note[:40] + "...") if len(note) > 43 else note
            self.tree.insert(
                "", "end", iid=idx,
                values=(idx + 1, rem.title, dt, repeat, display_note)
            )

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
            for rem in self.reminders[:]:
                if rem.datetime == now:
                    self.show_notification(rem)
                    # Handle repeat using OOP
                    if isinstance(rem, RecurringReminder):
                        next_dt = rem.next_occurrence()
                        if next_dt:
                            rem.datetime = next_dt
                            self.save_reminders()
                        else:
                            self.reminders.remove(rem)
                            self.save_reminders()
                    else:
                        self.reminders.remove(rem)
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