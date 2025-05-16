import tkinter as tk
from tkinter import ttk
import sqlite3
import os
import subprocess
from quiz_window import quiz_window

# Database setup
def load_sets_from_db():
    sets = []
    db_path = "data/sets.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sets ORDER BY created_at DESC")
        sets = [row[0] for row in cursor.fetchall()]
        conn.close()
    return sets

def open_set(set_name):
    print(f"Opening set: {set_name}")   #Remove after debugging

    ###Add the bitchass quiz functionality over here
    #Use quiz_window function (check quiz_window.py for functionality)
    #root.destroy() #Kill the homepage.py window (will run it again at the end of quiz_window.py)
    quiz_window(os.path.join("sets", set_name))
    

def create_set():
    root.destroy()  #Close the fucking window
    subprocess.Popen(["python", "new_set.py"])  #Runs new_set.py file
    print("Create Set button clicked!")  # Remove after debugging

if __name__ == "__main__":
    # GUI Setup
    root = tk.Tk()
    root.title("Home Page")
    root.geometry("1000x600")
    root.configure(bg="white")

    # Title
    title_label = tk.Label(root, text="Adaptive Learning System", font=('Helvetica', 26, 'bold'), bg="white")
    title_label.pack(pady=(30, 10))

    # Frame for Sets: label and Create button
    top_bar = tk.Frame(root, bg="white")
    top_bar.pack(fill='x', padx=40, pady=(0, 10))

    sets_label = tk.Label(top_bar, text="Sets:", font=('Helvetica', 18), bg="white")
    sets_label.pack(side='left')

    create_set_btn = tk.Button(top_bar, text="+ Create New Set", font=('Helvetica', 12), command=create_set)
    create_set_btn.pack(side='right')

    # Scrollable area
    container = tk.Frame(root, bg="white")
    container.pack(fill='both', expand=True, padx=40)

    canvas = tk.Canvas(container, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="white")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Load real sets from the database
    real_sets = load_sets_from_db()

    if real_sets:
        for set_name in real_sets:
            btn = tk.Button(scroll_frame, text=set_name, font=('Helvetica', 14), height=2,
                            command=lambda name=set_name: open_set(name), anchor='w')
            btn.pack(fill='x', pady=5)
    else:
        empty_label = tk.Label(scroll_frame, text="No sets found. Create one to get started!", font=('Helvetica', 14), bg="white")
        empty_label.pack(pady=20)

    root.mainloop()
