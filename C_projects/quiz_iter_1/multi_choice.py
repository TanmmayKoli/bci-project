import tkinter as tk
from PIL import ImageTk, Image

def generate_window(img, constellation_num, random_options):

    ###
    #constellation_name is the key where the correct constellation name is stored in the random_options dictionary
    #random_options is a dictionary containing the constellation_name and 3 other randomly selected constellations (all in random order int the dictionary)
    ###

    #This function will check whether the selected option was correct (and eventually whether confidence met the threshold)
    def check_correct(button_num):

        if button_num == constellation_num: ##Add confidence condition here
            print("Correct")
        else:   #Put the image back in the queue here
            print("Incorrect")

        #selected_option.set(button_name)
        #print("Button clicked:", selected_option.get())

    # Create the main window
    root = tk.Tk()
    root.attributes('-fullscreen', True)    #Makes tkinter window take full screen
    root.title("4 the Memo")

    constellation = ImageTk.PhotoImage(Image.open(f"{img}").resize((400,400)))       ###Change Later to actual constellation
    display_constellation = tk.Label(root, image=constellation)
    display_constellation.pack(pady=10)

    button_frame = tk.Frame(root)
    button_frame.pack()

    # Create 4 buttons
    option_1 = tk.Button(button_frame, text=random_options[1], command=lambda n=1: check_correct(n), width=30,height=5)
    option_2 = tk.Button(button_frame, text=random_options[2], command=lambda n=2: check_correct(n), width=30,height=5)
    option_3 = tk.Button(button_frame, text=random_options[3], command=lambda n=3: check_correct(n), width=30,height=5)
    option_4 = tk.Button(button_frame, text=random_options[4], command=lambda n=4: check_correct(n), width=30,height=5)

    #Add buttons to grid
    option_1.grid(row=0, column=0, padx=10, pady=5)
    option_2.grid(row=1, column=0, padx=10, pady=5)
    option_3.grid(row=0, column=1, padx=10, pady=5)
    option_4.grid(row=1, column=1, padx=10, pady=5)

    selected_option = tk.StringVar()

    # Start the GUI event loop
    root.mainloop()

#generate_window(img="Constellations/1.jpeg", constellation_num=2, random_options={1: "A", 2: "Apus", 3: "C", 4: "D"})