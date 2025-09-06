import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

DATA_FILE = "homework.json"
REMINDER_FILE = "reminders.json"

# ---------- Global Fonts ----------
DEFAULT_FONT = ("Arial", 14)
BOLD_FONT = ("Arial", 14, "bold")
TITLE_FONT = ("Arial", 16, "bold")
SMALL_FONT = ("Arial", 12)

# ---------- JSON Helpers ----------
def load_tasks_from_json():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except Exception:
        return []

def save_tasks_to_json(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def load_reminders_from_json():
    if not os.path.exists(REMINDER_FILE):
        return []
    try:
        with open(REMINDER_FILE, "r") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except Exception:
        return []

def save_reminders_to_json(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

# ---------------- Homework Planner ----------------
class HomeworkPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Homework Planner (Enhanced)")
        self.root.configure(bg="#f4f4f9")
        self.root.state("zoomed")

        # Main Notebook
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_tasks = tk.Frame(notebook, bg="#ffffff")
        self.tab_add = tk.Frame(notebook, bg="#ffffff")

        notebook.add(self.tab_tasks, text="📋 All Tasks")
        notebook.add(self.tab_add, text="➕ Add Task")

        self.setup_tasks_tab()
        self.setup_add_tab()
        self.load_tasks()

        # Status bar with clock
        self.status_bar = tk.Label(root, text="Ready", anchor="w", bg="#333", fg="white", font=SMALL_FONT)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_clock()

    # ---------------- Clock ----------------
    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.config(text=f"📅 {now}")
        self.root.after(1000, self.update_clock)

    # ---------------- Tasks Tab ----------------
    def setup_tasks_tab(self):
        filter_frame = tk.Frame(self.tab_tasks, bg="#e8eaf6", pady=15, padx=20)
        filter_frame.pack(fill=tk.X, anchor="w")

        tk.Label(filter_frame, text="Filter by Status:", bg="#e8eaf6", font=DEFAULT_FONT)\
            .grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.status_filter = ttk.Combobox(filter_frame, values=["all", "todo", "done"], width=15, font=DEFAULT_FONT)
        self.status_filter.set("all")
        self.status_filter.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        tk.Label(filter_frame, text="Filter by Subject:", bg="#e8eaf6", font=DEFAULT_FONT)\
            .grid(row=1, column=0, sticky="w", padx=5, pady=10)
        self.subject_filter = ttk.Combobox(filter_frame, values=["all"], width=15, font=DEFAULT_FONT)
        self.subject_filter.set("all")
        self.subject_filter.grid(row=1, column=1, sticky="w", padx=10, pady=10)

        tk.Label(filter_frame, text="Search:", bg="#e8eaf6", font=DEFAULT_FONT)\
            .grid(row=2, column=0, sticky="w", padx=5, pady=10)
        self.search_entry = tk.Entry(filter_frame, width=25, font=DEFAULT_FONT)
        self.search_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)

        tk.Button(filter_frame, text="Apply", bg="#4caf50", fg="white", font=DEFAULT_FONT,
                command=self.load_tasks)\
            .grid(row=3, column=0, columnspan=2, pady=20)

        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=DEFAULT_FONT)
        style.configure("Treeview.Heading", font=BOLD_FONT)
        style.map("Treeview", background=[("selected", "#2196f3")], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            self.tab_tasks,
            columns=("Title", "Subject", "Due", "Priority", "Status"),
            show="headings",
        )
        for col in ("Title", "Subject", "Due", "Priority", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btns = tk.Frame(self.tab_tasks, pady=5, bg="#ffffff")
        btns.pack()
        tk.Button(btns, text="Mark Done", command=self.mark_done, bg="#4caf50", fg="white", font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Edit Task", command=self.edit_task, bg="#2196f3", fg="white", font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="Delete Task", command=self.delete_task, bg="#f44336", fg="white", font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)

    # ---------------- Add Tab ----------------
    def setup_add_tab(self):
        form = tk.Frame(self.tab_add, pady=15, bg="#ffffff")
        form.pack()

        tk.Label(form, text="Title:", bg="#ffffff", font=BOLD_FONT).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        tk.Label(form, text="Subject:", bg="#ffffff", font=BOLD_FONT).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        tk.Label(form, text="Due Date:", bg="#ffffff", font=BOLD_FONT).grid(row=2, column=0, sticky="e", pady=5, padx=5)
        tk.Label(form, text="Priority (1-5):", bg="#ffffff", font=BOLD_FONT).grid(row=3, column=0, sticky="e", pady=5, padx=5)
        tk.Label(form, text="Details:", bg="#ffffff", font=BOLD_FONT).grid(row=4, column=0, sticky="ne", pady=5, padx=5)

        self.title_entry = tk.Entry(form, width=40, font=DEFAULT_FONT)
        self.title_entry.grid(row=0, column=1, pady=5, padx=5)

        self.subject_entry = tk.Entry(form, width=40, font=DEFAULT_FONT)
        self.subject_entry.grid(row=1, column=1, pady=5, padx=5)

        years = [str(y) for y in range(datetime.now().year, datetime.now().year + 6)]
        months = [str(m).zfill(2) for m in range(1, 13)]
        days = [str(d).zfill(2) for d in range(1, 32)]

        date_frame = tk.Frame(form, bg="#ffffff")
        date_frame.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        self.year_box = ttk.Combobox(date_frame, values=years, width=6, state="readonly", font=DEFAULT_FONT)
        self.year_box.set(str(datetime.now().year))
        self.year_box.pack(side=tk.LEFT, padx=2)

        self.month_box = ttk.Combobox(date_frame, values=months, width=4, state="readonly", font=DEFAULT_FONT)
        self.month_box.set(str(datetime.now().month).zfill(2))
        self.month_box.pack(side=tk.LEFT, padx=2)

        self.day_box = ttk.Combobox(date_frame, values=days, width=4, state="readonly", font=DEFAULT_FONT)
        self.day_box.set(str(datetime.now().day).zfill(2))
        self.day_box.pack(side=tk.LEFT, padx=2)

        self.priority_entry = tk.Entry(form, width=40, font=DEFAULT_FONT)
        self.priority_entry.insert(0, "3")
        self.priority_entry.grid(row=3, column=1, pady=5, padx=5)

        self.details_entry = tk.Text(form, width=40, height=6, font=DEFAULT_FONT)
        self.details_entry.grid(row=4, column=1, pady=5, padx=5)

        tk.Button(
            form, text="Add Task", command=self.add_task,
            bg="#673ab7", fg="white", font=DEFAULT_FONT, width=20
        ).grid(row=5, column=0, columnspan=2, pady=15)

    # ---------------- JSON Actions ----------------
    def add_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing", "Title is required")
            return
        subject = self.subject_entry.get().strip()
        try:
            due = f"{self.year_box.get()}-{self.month_box.get()}-{self.day_box.get()}"
            datetime.strptime(due, "%Y-%m-%d")
        except:
            due = None
        try:
            priority = int(self.priority_entry.get())
        except:
            priority = 3
        details = self.details_entry.get("1.0", "end").strip()

        tasks = load_tasks_from_json()
        new_id = max([t["id"] for t in tasks], default=0) + 1
        new_task = {
            "id": new_id,
            "title": title,
            "subject": subject,
            "due_at": due,
            "priority": priority,
            "status": "todo",
            "details": details,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        tasks.append(new_task)
        save_tasks_to_json(tasks)

        self.clear_add_form()
        self.load_tasks()

        # --- Prompt to add reminder ---
        if messagebox.askyesno("Add Reminder", "Do you want to add a reminder for this task?"):
            self.add_reminder_from_task(new_task)

    def add_reminder_from_task(self, task):
        win = tk.Toplevel(self.root)
        win.title("Add Reminder for Task")
        win.geometry("400x350")
        win.grab_set()

        tk.Label(win, text="Title:", font=DEFAULT_FONT).pack(pady=5)
        title_var = tk.StringVar(value=task["title"])
        title_entry = tk.Entry(win, textvariable=title_var, font=DEFAULT_FONT, width=30)
        title_entry.pack(pady=5)

        tk.Label(win, text="Date (YYYY-MM-DD):", font=DEFAULT_FONT).pack(pady=5)
        date_var = tk.StringVar(value=task["due_at"] or datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(win, textvariable=date_var, font=DEFAULT_FONT, width=30)
        date_entry.pack(pady=5)

        tk.Label(win, text="Time (HH:MM, 24h):", font=DEFAULT_FONT).pack(pady=5)
        time_var = tk.StringVar(value="09:00")
        time_entry = tk.Entry(win, textvariable=time_var, font=DEFAULT_FONT, width=30)
        time_entry.pack(pady=5)

        tk.Label(win, text="Note:", font=DEFAULT_FONT).pack(pady=5)
        note_text = tk.Text(win, font=DEFAULT_FONT, width=30, height=3)
        note_text.insert("1.0", task.get("details", ""))
        note_text.pack(pady=5)

        def confirm():
            title = title_var.get().strip()
            date_str = date_var.get().strip()
            time_str = time_var.get().strip()
            note = note_text.get("1.0", tk.END).strip()
            if not title or not date_str or not time_str:
                tk.messagebox.showwarning("Missing", "Please fill in all fields.")
                return
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except Exception:
                tk.messagebox.showwarning("Format", "Invalid date or time format.")
                return

            reminders = load_reminders_from_json()
            # Remove any existing reminder for this task_id
            reminders = [r for r in reminders if r.get("task_id") != task["id"]]
            reminder = {
                "task_id": task["id"],
                "title": title,
                "datetime": dt.strftime("%Y-%m-%d %H:%M"),
                "repeat": "None",
                "note": note,
                "status": "Pending"
            }
            reminders.append(reminder)
            save_reminders_to_json(reminders)
            tk.messagebox.showinfo("Success", "Reminder added and synced!")
            win.destroy()

        tk.Button(win, text="Confirm & Add Reminder", command=confirm, bg="#388e3c", fg="white", font=DEFAULT_FONT).pack(pady=15)
        tk.Button(win, text="Cancel", command=win.destroy, bg="#f44336", fg="white", font=DEFAULT_FONT).pack()

    def clear_add_form(self):
        self.title_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, "3")
        self.details_entry.delete("1.0", tk.END)

    def load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        tasks = load_tasks_from_json()
        tasks.sort(key=lambda x: x.get("due_at") or "")

        subjects = {"all"}
        for r in tasks:
            if r.get("subject"):
                subjects.add(r["subject"])
        self.subject_filter["values"] = list(subjects)

        status_f = self.status_filter.get()
        subject_f = self.subject_filter.get()
        search_q = self.search_entry.get().strip().lower()

        for r in tasks:
            if status_f != "all" and r["status"] != status_f:
                continue
            if subject_f != "all" and r["subject"] != subject_f:
                continue
            if search_q and search_q not in r["title"].lower():
                continue

            tags = ()
            if r["status"] == "done":
                tags = ("done",)
            elif r["due_at"]:
                try:
                    due_date = datetime.strptime(r["due_at"], "%Y-%m-%d")
                    if due_date < datetime.now():
                        tags = ("overdue",)
                    elif due_date.date() == datetime.today().date():
                        tags = ("today",)
                except:
                    pass

            self.tree.insert("", tk.END, iid=r["id"],
                             values=(r["title"], r["subject"], r["due_at"] or "—", r["priority"], r["status"]),
                             tags=tags)

        self.tree.tag_configure("done", background="#c8e6c9")
        self.tree.tag_configure("overdue", background="#ffcdd2")
        self.tree.tag_configure("today", background="#fff9c4")

    def mark_done(self):
        sel = self.tree.selection()
        if not sel:
            return
        task_id = int(sel[0])
        tasks = load_tasks_from_json()
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "done"
                break
        save_tasks_to_json(tasks)
        self.load_tasks()

    def edit_task(self):
        sel = self.tree.selection()
        if not sel:
            return
        task_id = int(sel[0])
        tasks = load_tasks_from_json()
        row = next((t for t in tasks if t["id"] == task_id), None)
        if not row:
            return

        win = tk.Toplevel(self.root)
        win.title("Edit Task")
        win.configure(bg="#ffffff")
        win.geometry("500x450")

        tk.Label(win, text="Title:", bg="#ffffff", font=BOLD_FONT).grid(row=0, column=0, pady=5, padx=5, sticky="e")
        e_title = tk.Entry(win, width=30, font=DEFAULT_FONT)
        e_title.insert(0, row["title"])
        e_title.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(win, text="Subject:", bg="#ffffff", font=BOLD_FONT).grid(row=1, column=0, pady=5, padx=5, sticky="e")
        e_subject = tk.Entry(win, width=30, font=DEFAULT_FONT)
        e_subject.insert(0, row["subject"])
        e_subject.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(win, text="Due Date:", bg="#ffffff", font=BOLD_FONT).grid(row=2, column=0, pady=5, padx=5, sticky="e")

        years = [str(y) for y in range(datetime.now().year, datetime.now().year + 6)]
        months = [str(m).zfill(2) for m in range(1, 13)]
        days = [str(d).zfill(2) for d in range(1, 32)]

        date_frame = tk.Frame(win, bg="#ffffff")
        date_frame.grid(row=2, column=1, pady=5, padx=5, sticky="w")

        e_year = ttk.Combobox(date_frame, values=years, width=6, state="readonly", font=DEFAULT_FONT)
        e_month = ttk.Combobox(date_frame, values=months, width=4, state="readonly", font=DEFAULT_FONT)
        e_day = ttk.Combobox(date_frame, values=days, width=4, state="readonly", font=DEFAULT_FONT)

        if row["due_at"]:
            try:
                due_date = datetime.strptime(row["due_at"], "%Y-%m-%d")
                e_year.set(str(due_date.year))
                e_month.set(str(due_date.month).zfill(2))
                e_day.set(str(due_date.day).zfill(2))
            except:
                e_year.set(str(datetime.now().year))
                e_month.set(str(datetime.now().month).zfill(2))
                e_day.set(str(datetime.now().day).zfill(2))
        else:
            e_year.set(str(datetime.now().year))
            e_month.set(str(datetime.now().month).zfill(2))
            e_day.set(str(datetime.now().day).zfill(2))

        e_year.pack(side=tk.LEFT, padx=2)
        e_month.pack(side=tk.LEFT, padx=2)
        e_day.pack(side=tk.LEFT, padx=2)

        tk.Label(win, text="Priority:", bg="#ffffff", font=BOLD_FONT).grid(row=3, column=0, pady=5, padx=5, sticky="e")
        e_priority = tk.Entry(win, width=30, font=DEFAULT_FONT)
        e_priority.insert(0, str(row["priority"]))
        e_priority.grid(row=3, column=1, pady=5, padx=5)

        tk.Label(win, text="Details:", bg="#ffffff", font=BOLD_FONT).grid(row=4, column=0, pady=5, padx=5, sticky="ne")
        e_details = tk.Text(win, width=30, height=5, font=DEFAULT_FONT)
        e_details.insert("1.0", row["details"])
        e_details.grid(row=4, column=1, pady=5, padx=5)

        def save():
            try:
                due = f"{e_year.get()}-{e_month.get()}-{e_day.get()}"
                datetime.strptime(due, "%Y-%m-%d")
            except:
                due = None

            row["title"] = e_title.get()
            row["subject"] = e_subject.get()
            row["due_at"] = due
            row["priority"] = int(e_priority.get())
            row["details"] = e_details.get("1.0", "end").strip()
            save_tasks_to_json(tasks)
            win.destroy()
            self.load_tasks()

            # --- Sync reminder if exists ---
            reminders = load_reminders_from_json()
            for rem in reminders:
                if rem.get("task_id") == row["id"]:
                    rem["title"] = row["title"]
                    rem["note"] = row["details"]
                    rem["datetime"] = (due + " 09:00") if due else rem["datetime"]
                    rem["status"] = "Pending"
            save_reminders_to_json(reminders)

        tk.Button(win, text="Save", command=save, bg="#4caf50", fg="white", font=DEFAULT_FONT, width=15).grid(row=5, column=0, columnspan=2, pady=15)

    def delete_task(self):
        sel = self.tree.selection()
        if not sel:
            return
        task_id = int(sel[0])
        if messagebox.askyesno("Delete", "Are you sure?"):
            tasks = load_tasks_from_json()
            tasks = [t for t in tasks if t["id"] != task_id]
            save_tasks_to_json(tasks)
            # Also delete corresponding reminder
            reminders = load_reminders_from_json()
            reminders = [r for r in reminders if r.get("task_id") != task_id]
            save_reminders_to_json(reminders)
            self.load_tasks()

# ---------------- Main ----------------
def main():
    root = tk.Tk()
    app = HomeworkPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()