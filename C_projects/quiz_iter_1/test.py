import tkinter as tk
from PIL import ImageTk, Image

def on_button_click(button_name):
    selected_option.set(button_name)
    print("Button clicked:", selected_option.get())

# Create the main window
root = tk.Tk()
root.title("Quiz GUI")

constellation = ImageTk.PhotoImage(Image.open("Pikachu.jpg").resize((400,400)))       ###Change Later to actual constellation
display_constellation = tk.Label(root, image=constellation)
display_constellation.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack()

# Create 4 buttons
option_1 = tk.Button(button_frame, text="Pikachu", command=lambda n="Option 1": on_button_click(n), width=30,height=5)
option_2 = tk.Button(button_frame, text="Pichu", command=lambda n="Option 2": on_button_click(n), width=30,height=5)
option_3 = tk.Button(button_frame, text="Raichu", command=lambda n="Option 3": on_button_click(n), width=30,height=5)
option_4 = tk.Button(button_frame, text="Bulbasaur", command=lambda n="Option 4": on_button_click(n), width=30,height=5)

#Add buttons to grid
option_1.grid(row=0, column=0, padx=10, pady=5)
option_2.grid(row=1, column=0, padx=10, pady=5)
option_3.grid(row=0, column=1, padx=10, pady=5)
option_4.grid(row=1, column=1, padx=10, pady=5)

selected_option = tk.StringVar()

# Start the GUI event loop
root.mainloop()
