import queue
from PIL import ImageTk, Image
import pandas as pd
import random
import tkinter as tk

# Setup
image_paths = [f"Constellations/{i+1}.jpeg" for i in range(35)]
image_queue = queue.Queue(maxsize=5)
reinsert_queue = queue.Queue()

# Load constellation names
constellation_key = pd.read_excel('constellation_key.xlsx', sheet_name='Sheet1')
constellation_names = constellation_key['Name'].tolist()

def generate_window(img_path, correct_button_num, options_dict):
    def check_correct(button_num):
        root.destroy()
        if button_num == correct_button_num:    #BCI confidence condition here
            print("Correct")
        else:
            print("Incorrect — Re-queuing image:", img_path)
            reinsert_queue.put((img_path, current_image_index))

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.title("4 the Memo")

    img = Image.open(img_path)
    img = img.resize((400, 400))
    photo = ImageTk.PhotoImage(img)
    img.close()

    display = tk.Label(root, image=photo)
    display.image = photo  # prevent garbage collection
    display.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    for i in range(1, 5):
        btn = tk.Button(
            btn_frame,
            text=options_dict[i],
            command=lambda n=i: check_correct(n),
            width=30,
            height=5
        )
        row = 0 if i in [1, 3] else 1
        col = 0 if i in [1, 2] else 1
        btn.grid(row=row, column=col, padx=10, pady=5)

    root.mainloop()

def process_image(img_path, img_index):
    global current_image_index
    current_image_index = img_index

    correct_name = constellation_names[img_index - 1]
    correct_btn = random.randint(1, 4)

    options = {}
    used = {correct_name}
    for i in range(1, 5):
        if i == correct_btn:
            options[i] = correct_name
        else:
            other = random.choice([n for n in constellation_names if n not in used])
            used.add(other)
            options[i] = other

    generate_window(img_path, correct_btn, options)

# Loop through all 35 images in batches of 5
img_counter = 1
for i in range(0, len(image_paths), 5):
    batch = image_paths[i:i+5]
    print(f"\nLoading batch {i//5 + 1}")

    # Load batch into queue
    for path in batch:
        image_queue.put((path, img_counter))
        img_counter += 1

    # Keep running current batch until all are answered correctly
    while not image_queue.empty():
        while not image_queue.empty():
            img_path, index = image_queue.get()
            process_image(img_path, index)
            image_queue.task_done()

        # Move reinserted (wrong) images back to the queue
        while not reinsert_queue.empty():
            path, idx = reinsert_queue.get()
            image_queue.put((path, idx))

print("\nAll images processed.")
