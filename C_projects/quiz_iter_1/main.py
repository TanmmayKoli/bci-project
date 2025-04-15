import queue
from PIL import ImageTk, Image
import time
import pandas as pd
import random
#from multi_choice import generate_window
import tkinter as tk

# Creating list of all 35 image names and file paths
image_paths = [f"Constellations/{i+1}.jpeg" for i in range(35)]

# Create a queue with max size 5
image_queue = queue.Queue(maxsize=5)

reinsert_queue = queue.Queue()

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

def process_image(img, img_num):
    # Simulate image processing
    print(f"Processing {img.filename}")
    
    #Get correct value of images name
    constellation_key = pd.read_excel('constellation_key.xlsx', sheet_name='Sheet1')
    constellation_name = constellation_key.at[img_num-1, 'Name']    #Finding the name of each constellation

    correct_answer_location = random.randint(1,4)
    options_given = {}
    #Create dictionary with constellation_name and 3 other randomly selected names
    for i in range(1,5):
        if i == correct_answer_location:
            options_given[i] = constellation_name
            i += 1
        else:
            options_given[i] = constellation_key.at[(random.randint(1,35))-1, 'Name']

    #Send images to tkinter GUI over here (call function in multi__choice.py)
    generate_window(img=f"Constellations/{img_num}.jpeg", constellation_num=correct_answer_location, random_options=options_given)

    img.close()


img_counter = 1
# Process in batches of 5
for i in range(0, len(image_paths), 5):
    batch = image_paths[i:i+5]

    print(f"\nLoading batch {i//5 + 1}")

    # Fill the queue with the batch
    for path in batch:
        img = Image.open(path)
        image_queue.put(img)  # This will block if the queue is full

    # Process all items in the queue
    while not image_queue.empty():
        img = image_queue.get()
        process_image(img, img_counter)
        img_counter+=1
        image_queue.task_done()  # Mark the task as done

print("\nAll images processed.")
