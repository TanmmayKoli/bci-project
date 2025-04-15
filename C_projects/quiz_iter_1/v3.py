import queue
from PIL import ImageTk, Image
import time
import pandas as pd
import random
import tkinter as tk
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from scipy.signal import welch
import numpy as np
from collections import deque
import csv
import os

# ----------- BCI SETUP ----------- #
FS = 250  # EEG sample rate
params = BrainFlowInputParams()
params.serial_port = "COM7"  # Change to setup
board_id = 0
board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream()
eeg_channels = BoardShim.get_eeg_channels(board_id)
selected_channels = eeg_channels[:6]

# ----------- Confidence Computation ----------- #
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

def calibrate_confidence(duration=30):  #will run for 30 seconds to calculate baseline
    print("Calibrating baseline confidence... Please relax and stay still.")    #Need to give verbal instruction or display on screen
    baseline_scores = []
    start = time.time()
    while time.time() - start < duration:
        score = get_confidence_score()
        baseline_scores.append(score)
        print(f"Recorded: {score:.2f}") #Remove after debugging
        time.sleep(1)   #Pacing it out so that it doesnt record a single cluster of data in a few seconds
    mean = np.mean(baseline_scores)
    std = np.std(baseline_scores)   #Finds standard deviation
    print(f"Calibration Complete — Initial Threshold: {mean + 0.75 * std:.2f}") #Remove after debugging
    return deque(baseline_scores[-20:], maxlen=20)  # Keep latest 20 for moving threshold

def compute_dynamic_threshold(buffer):
    scores = np.array(buffer)
    return np.mean(scores) + 0.75 * np.std(scores)

# ----------- Logging Setup ----------- #
log_filename = "confidence_log.csv"
if not os.path.exists(log_filename):
    with open(log_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "ImageNum", "Confidence", "Threshold", "Correct", "Confident", "Final Verdict"])

def log_result(img_num, confidence, threshold, correct, confident):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    verdict = "correct" if correct and confident else "unconfident" if correct else "wrong"
    with open(log_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, img_num, f"{confidence:.2f}", f"{threshold:.2f}", correct, confident, verdict])

# ----------- Queue Setup ----------- #
image_paths = [f"Constellations/{i+1}.jpeg" for i in range(35)]
image_queue = queue.Queue(maxsize=5)
constellation_key = pd.read_excel('constellation_key.xlsx', sheet_name='Sheet1')

# ----------- GUI & Image Processing ----------- #
def generate_window(img_path, constellation_num, options_given, img_num, conf_buffer):
    result = {"status": None}

    def check_answer(button_num):
        confidence = get_confidence_score()
        conf_buffer.append(confidence)
        threshold = compute_dynamic_threshold(conf_buffer)
        correct = button_num == constellation_num
        confident = confidence >= threshold
        final = "correct" if correct and confident else "incorrect"

        print(f"Confidence: {confidence:.2f} | Threshold: {threshold:.2f} | Answer: {'✅' if correct else '❌'} | Verdict: {final}")    #Remove after debugging

        log_result(img_num, confidence, threshold, correct, confident)
        result["status"] = final
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

def process_image(img_path, img_num, conf_buffer):
    name = constellation_key.at[img_num-1, 'Name']
    correct_index = random.randint(1, 4)
    options = {i: constellation_key.at[random.randint(0, 34), 'Name'] for i in range(1, 5)}
    options[correct_index] = name
    return generate_window(img_path, correct_index, options, img_num, conf_buffer)

# ----------- MAIN LOOP ----------- #
confidence_buffer = calibrate_confidence()
img_counter = 1

for i in range(0, len(image_paths), 5):
    batch = image_paths[i:i+5]
    print(f"\nLoading batch {i//5 + 1}")

    #Adding all 5 image paths from batch into queue
    for path in batch:
        image_queue.put((path, img_counter))
        img_counter += 1

    #Repeating till queue is empty
    while not image_queue.empty():
        img_path, img_num = image_queue.get()
        result = process_image(img_path, img_num, confidence_buffer)
        if result != "correct":
            print("Re-adding image to queue...")    #Remove after debugging
            image_queue.put((img_path, img_num))
        image_queue.task_done()

# ----------- CLEANUP ----------- #
board.stop_stream()
board.release_session()
print("\nAll images processed.")    #Remove after debugging
