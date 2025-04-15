import queue
from PIL import ImageTk, Image
import time
import pandas as pd
import random
import tkinter as tk
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from scipy.signal import welch
import numpy as np

# ----------- BCI SETUP ----------- #
params = BrainFlowInputParams()
params.serial_port = "COM7"  # Change this to setup
board_id = 0
board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream()
eeg_channels = BoardShim.get_eeg_channels(board_id)
selected_channels = eeg_channels[:6]  # first 6 EEG channels

def bandpower(eeg_data, fs, band):
    freqs, psd = welch(eeg_data, fs, nperseg=256)
    idx_band = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx_band], freqs[idx_band])

def get_confidence_score():
    data = board.get_current_board_data(256)
    alpha_total = 0
    theta_total = 0

    for ch in selected_channels:
        eeg = data[ch]
        alpha_total += bandpower(eeg, FS, [8, 12])
        theta_total += bandpower(eeg, FS, [4, 7])

    if theta_total == 0:
        return 0
    return (alpha_total / len(selected_channels)) / (theta_total / len(selected_channels))

def calibrate_confidence(duration=30):
    print("Calibrating baseline confidence... Please relax and stay still.")
    baseline_scores = []

    start = time.time()
    while time.time() - start < duration:
        score = get_confidence_score()
        baseline_scores.append(score)
        print(f"Recorded: {score:.2f}")
        time.sleep(1)  # Sample every second

    baseline_scores = np.array(baseline_scores)
    mean = np.mean(baseline_scores)
    std = np.std(baseline_scores)
    
    dynamic_thresh = mean + 0.75 * std
    print(f"\nCalibration Complete — Dynamic Threshold set to: {dynamic_thresh:.2f}")
    return dynamic_thresh

# ----------- CONFIG ----------- #
CONFIDENCE_THRESHOLD = calibrate_confidence()
FS = 250  # EEG sample rate

# ----------- QUEUE SETUP ----------- #
image_paths = [f"Constellations/{i+1}.jpeg" for i in range(35)]
image_queue = queue.Queue(maxsize=5)
constellation_key = pd.read_excel('constellation_key.xlsx', sheet_name='Sheet1')

def generate_window(img_path, constellation_num, options_given):
    result = {"status": None}  # To pass result back out of tkinter

    def check_answer(button_num):
        confidence = get_confidence_score()
        print(f"Confidence: {confidence:.2f}")

        if button_num == constellation_num and confidence >= CONFIDENCE_THRESHOLD:
            print("Correct and confident")
            result["status"] = "correct"
        else:
            print("Incorrect or unconfident")
            result["status"] = "incorrect"
        root.destroy()

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.title("4 the Memo")

    constellation = ImageTk.PhotoImage(Image.open(img_path).resize((400, 400)))
    display = tk.Label(root, image=constellation)
    display.pack(pady=10)

    button_frame = tk.Frame(root)
    button_frame.pack()

    for i in range(1, 5):
        btn = tk.Button(button_frame, text=options_given[i], command=lambda n=i: check_answer(n),
                        width=30, height=5)
        row = 0 if i in [1, 3] else 1
        col = 0 if i in [1, 2] else 1
        btn.grid(row=row, column=col, padx=10, pady=5)

    root.mainloop()
    return result["status"]

def process_image(img_path, img_num):
    name = constellation_key.at[img_num-1, 'Name']
    correct_index = random.randint(1, 4)

    options = {}
    for i in range(1, 5):
        if i == correct_index:
            options[i] = name
        else:
            options[i] = constellation_key.at[random.randint(0, 34), 'Name']

    return generate_window(img_path, correct_index, options)

# ----------- MAIN LOOP ----------- #
img_counter = 1
for i in range(0, len(image_paths), 5):
    batch = image_paths[i:i+5]
    print(f"\nLoading batch {i//5 + 1}")

    for path in batch:
        image_queue.put((path, img_counter))
        img_counter += 1

    while not image_queue.empty():
        img_path, img_num = image_queue.get()
        result = process_image(img_path, img_num)
        if result == "incorrect":
            print("Re-adding image to queue...")
            image_queue.put((img_path, img_num))
        image_queue.task_done()

# ----------- CLEANUP ----------- #
board.stop_stream()
board.release_session()
print("\nAll images processed.")
