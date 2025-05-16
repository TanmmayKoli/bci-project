import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import sqlite3
from datetime import datetime
import subprocess

# Global state
selected_images = []
selected_answer_key = None

# Setup database
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/sets.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            image_count INTEGER,
            answer_key_path TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Image upload
def upload_images():
    global selected_images
    file_paths = filedialog.askopenfilenames(
        title="Select Image Files",
        filetypes=[("Images", "*.jpg *.jpeg *.png")]
    )
    if file_paths:
        selected_images = list(file_paths)
        messagebox.showinfo("Upload Successful", f"{len(selected_images)} images selected.")

# Answer key upload
def upload_answer_key():
    global selected_answer_key
    file_path = filedialog.askopenfilename(
        title="Select Answer Key",
        filetypes=[("Excel Files", "*.xlsx *.xls"), ("CSV Files", "*.csv")]
    )
    if file_path:
        selected_answer_key = file_path
        messagebox.showinfo("Upload Successful", "Answer key uploaded.")

# Create set
def create_set():
    set_name = set_name_entry.get().strip()

    if not set_name:
        messagebox.showerror("Error", "Please enter a set name.")
        return
    if not selected_images:
        messagebox.showerror("Error", "Please upload images.")
        return
    if not selected_answer_key:
        messagebox.showerror("Error", "Please upload an answer key.")
        return

    # Create folders
    set_folder = os.path.join("sets", set_name)
    images_folder = os.path.join(set_folder, "images")
    os.makedirs(images_folder, exist_ok=True)

    # Copy and rename images
    for i, image_path in enumerate(selected_images, start=1):
        ext = os.path.splitext(image_path)[1]
        dest_path = os.path.join(images_folder, f"{i}{ext}")
        shutil.copy(image_path, dest_path)

    # Copy answer key
    answer_key_name = os.path.basename(selected_answer_key)
    key_dest = os.path.join(set_folder, answer_key_name)
    shutil.copy(selected_answer_key, key_dest)

    # Add to database
    conn = sqlite3.connect("data/sets.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sets (name, image_count, answer_key_path, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            set_name,
            len(selected_images),
            key_dest,
            datetime.now().isoformat()
        ))
        conn.commit()
        messagebox.showinfo("Success", f"Set '{set_name}' created!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"A set named '{set_name}' already exists.")
    finally:
        conn.close()

    #Needs to terminate window and open the homepage again
    root.destroy()
    subprocess.Popen(["python", "homepage.py"]) #Runs homepage.py

# Initialize DB
init_db()

# UI
root = tk.Tk()
root.geometry("750x500")
root.configure(bg="white")
root.title("Add New Set")

# Title
title_label = tk.Label(root, text="Create a New Set", font=('Helvetica', 26, 'bold'), bg="white")
title_label.pack(pady=(30, 20))

# Set Name Entry
set_name_frame = tk.Frame(root, bg="white")
set_name_frame.pack(pady=10)

set_name_label = tk.Label(set_name_frame, text="Set Name:", font=('Helvetica', 14), bg="white")
set_name_label.pack(side="left", padx=(0, 10))

set_name_entry = tk.Entry(set_name_frame, font=('Helvetica', 14), width=30)
set_name_entry.pack(side="left")

# Upload Buttons
upload_frame = tk.Frame(root, bg="white")
upload_frame.pack(pady=30)

upload_images_btn = tk.Button(upload_frame, text="Upload Images", font=('Helvetica', 12), width=20, command=upload_images)
upload_images_btn.pack(pady=10)

upload_key_btn = tk.Button(upload_frame, text="Upload Answer Key", font=('Helvetica', 12), width=20, command=upload_answer_key)
upload_key_btn.pack(pady=10)

# Create Set Button
create_set_btn = tk.Button(root, text="Create Set", font=('Helvetica', 14), width=20, height=2, command=create_set)
create_set_btn.pack(pady=20)

root.mainloop()
