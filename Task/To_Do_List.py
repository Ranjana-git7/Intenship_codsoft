import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence

# ---------- Config ----------
DATA_FILE = "tasks.json"
ICON_IMAGE = "anime_icon.jpg"
GIF_IMAGE = "anime_wave.gif"
# -----------------------------

root = Tk()
root.title("SUPER To-Do — Anime Edition")
root.geometry("900x600")
root.minsize(820, 520)

root.configure(bg="#1a1a1a")  # Dark background


# ---------- ICON ----------
def load_icon():
    try:
        img = Image.open(ICON_IMAGE).convert("RGBA")
        img = img.resize((60, 60))
        return ImageTk.PhotoImage(img)
    except:
        return None


icon = load_icon()


# ---------- HEADER ----------
title_frame = Frame(root, bg="#1a1a1a")
title_frame.pack(fill=X, pady=10)

if icon:
    Label(title_frame, image=icon, bg="#1a1a1a").pack(side=LEFT, padx=10)

Label(title_frame,
      text="SUPER TO-DO LIST",
      font=("Segoe UI", 26, "bold"),
      fg="white",
      bg="#1a1a1a").pack(side=LEFT)

# ---------- ENTRY + BUTTONS ----------
control = Frame(root, bg="#1a1a1a")
control.pack(fill=X, pady=10)

entry = ttk.Entry(control, width=50, font=("Segoe UI", 12))
entry.grid(row=0, column=0, padx=10)

btn_add = ttk.Button(control, text="Add")
btn_edit = ttk.Button(control, text="Edit")

btn_add.grid(row=0, column=1, padx=5)
btn_edit.grid(row=0, column=2, padx=5)

# ---------- MAIN AREA ----------
area = Frame(root, bg="#1a1a1a")
area.pack(fill=BOTH, expand=True)

# Pending panel
pending_panel = Frame(area, bg="#1a1a1a")
pending_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=20)

Label(pending_panel, text="Pending Tasks",
      font=("Segoe UI", 14, "bold"),
      fg="white", bg="#1a1a1a").pack(anchor="w")

pending_listbox = Listbox(pending_panel, font=("Segoe UI", 12),
                          bg="#2b2b2b", fg="white",
                          selectbackground="#6fa8dc")
pending_listbox.pack(fill=BOTH, expand=True, pady=10)

# Completed panel
completed_panel = Frame(area, bg="#1a1a1a")
completed_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=20)

Label(completed_panel, text="Completed",
      font=("Segoe UI", 14, "bold"),
      fg="#90ff9c", bg="#1a1a1a").pack(anchor="w")

completed_listbox = Listbox(completed_panel, font=("Segoe UI", 12),
                            bg="#2b2b2b", fg="#90ff9c",
                            selectbackground="#9fe6b0")
completed_listbox.pack(fill=BOTH, expand=True, pady=10)

# ---------- BOTTOM BUTTONS ----------
bottom = Frame(root, bg="#1a1a1a")
bottom.pack(pady=10)

btn_comp = ttk.Button(bottom, text="→ Mark Completed")
btn_pend = ttk.Button(bottom, text="← Move to Pending")
btn_del = ttk.Button(bottom, text="Delete")

btn_comp.grid(row=0, column=0, padx=10)
btn_pend.grid(row=0, column=1, padx=10)
btn_del.grid(row=0, column=2, padx=10)


# ---------- TASK FUNCTIONS ----------
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return {"pending": [], "completed": []}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"pending": [], "completed": []}


def save_tasks():
    data = {
        "pending": list(pending_listbox.get(0, END)),
        "completed": list(completed_listbox.get(0, END))
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_task():
    task = entry.get().strip()
    if not task:
        messagebox.showwarning("Warning", "Enter a task!")
        return
    pending_listbox.insert(END, task)
    entry.delete(0, END)
    save_tasks()


def edit_task():
    new = entry.get().strip()
    if not new:
        messagebox.showwarning("Warning", "Type new text")
        return

    if pending_listbox.curselection():
        idx = pending_listbox.curselection()[0]
        pending_listbox.delete(idx)
        pending_listbox.insert(idx, new)
    elif completed_listbox.curselection():
        idx = completed_listbox.curselection()[0]
        completed_listbox.delete(idx)
        completed_listbox.insert(idx, new)
    else:
        messagebox.showwarning("Warning", "Select a task")
        return

    entry.delete(0, END)
    save_tasks()


def mark_completed():
    if not pending_listbox.curselection():
        messagebox.showwarning("Warning", "Select a pending task")
        return
    idx = pending_listbox.curselection()[0]
    task = pending_listbox.get(idx)
    pending_listbox.delete(idx)
    completed_listbox.insert(END, task)
    save_tasks()


def mark_pending():
    if not completed_listbox.curselection():
        messagebox.showwarning("Warning", "Select a completed task")
        return
    idx = completed_listbox.curselection()[0]
    task = completed_listbox.get(idx)
    completed_listbox.delete(idx)
    pending_listbox.insert(END, task)
    save_tasks()


def delete_task():
    if pending_listbox.curselection():
        pending_listbox.delete(pending_listbox.curselection()[0])
    elif completed_listbox.curselection():
        completed_listbox.delete(completed_listbox.curselection()[0])
    else:
        messagebox.showwarning("Warning", "Select a task")
        return
    save_tasks()


# Bind button functions
btn_add.config(command=add_task)
btn_edit.config(command=edit_task)
btn_comp.config(command=mark_completed)
btn_pend.config(command=mark_pending)
btn_del.config(command=delete_task)


# ---------- GIF ANIMATION ----------
gif_frames = []
gif_index = 0

if os.path.exists(GIF_IMAGE):
    try:
        gif = Image.open(GIF_IMAGE)
        for frame in ImageSequence.Iterator(gif):
            f = frame.convert("RGBA").resize((120, 120))
            gif_frames.append(ImageTk.PhotoImage(f))
    except:
        gif_frames = []

gif_label = None

def animate():
    global gif_index
    if gif_frames:
        gif_label.config(image=gif_frames[gif_index])
        gif_index = (gif_index + 1) % len(gif_frames)
    root.after(120, animate)


if gif_frames:
    gif_label = Label(root, bg="#1a1a1a")
    gif_label.place(x=760, y=420)
    animate()


# ---------- Load saved tasks ----------
saved = load_tasks()
for t in saved["pending"]:
    pending_listbox.insert(END, t)
for t in saved["completed"]:
    completed_listbox.insert(END, t)

root.mainloop()
