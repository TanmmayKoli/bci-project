import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Load and process the CSV data ---
df = pd.read_csv("confidence_log.csv")

# Assign question numbers for x-axis (Basically how many questions have been answered total)
df['ImageNum'] = range(1, len(df) + 1)

# Convert string "True"/"False" to actual booleans if needed
if df['Correct'].dtype == object:
    df['Correct'] = df['Correct'].map({'True': True, 'False': False})

# --- Setup GUI ---
root = tk.Tk()
root.geometry("1100x750")
root.title("Study Analytics")
root.configure(bg="white")

title_label = tk.Label(root, text="Study Insights", font=('Helvetica', 26, 'bold'), bg="white")
title_label.pack(pady=(20, 10))

# --- Create a Frame to Hold Graphs ---
frame = tk.Frame(root, bg="white")
frame.pack(pady=10)

# --- Plot 1: Confidence vs Question Number ---
fig1, ax1 = plt.subplots(figsize=(5, 3), dpi=100)
ax1.plot(df['ImageNum'], df['Confidence'], label='Confidence', marker='o')
ax1.plot(df['ImageNum'], df['Threshold'], label='Threshold', linestyle='--', color='red')
ax1.set_title('Confidence Score Over Questions')
ax1.set_xlabel('Question Number')
ax1.set_ylabel('Confidence')
ax1.legend()
ax1.grid(True)

fig1.tight_layout()

canvas1 = FigureCanvasTkAgg(fig1, master=frame)
canvas1.draw()
canvas1.get_tk_widget().grid(row=0, column=0, padx=20, pady=10)

# --- Plot 2: Accuracy by Confidence Bucket ---

#Calculating lower quartile of confidence
lower_quartile = df['Confidence'].quantile(0.25)
print(lower_quartile)
#Calculating Median of confidence
median = df['Confidence'].quantile(0.5)
print(median)
#Calculating upper quartile of confidence
upper_quartile = df['Confidence'].quantile(0.75)
print(upper_quartile)

df['confidence_bin'] = pd.cut(
    df['Confidence'],
    bins=[-float('inf'), lower_quartile, median, upper_quartile, float('inf')],
    labels=['Very Low', 'Low', 'Medium', 'High']
)
accuracy_by_bin = df.groupby('confidence_bin')['Correct'].mean() * 100

fig2, ax2 = plt.subplots(figsize=(5, 3), dpi=100)
accuracy_by_bin.plot(kind='bar', color=['darkred', 'tomato', 'orange', 'mediumseagreen'], ax=ax2)
ax2.set_title('Accuracy by Confidence Level')
ax2.set_ylabel('Accuracy (%)')
ax2.set_ylim(0, 100)
ax2.set_xlabel('Confidence Level')
ax2.grid(axis='y')

fig2.tight_layout()

canvas2 = FigureCanvasTkAgg(fig2, master=frame)
canvas2.draw()
canvas2.get_tk_widget().grid(row=0, column=1, padx=20, pady=10)

# --- Run the GUI ---
root.mainloop()
