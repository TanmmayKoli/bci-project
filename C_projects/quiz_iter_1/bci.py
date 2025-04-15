from brainflow.board_shim import BoardShim, BrainFlowInputParams
import numpy as np
import time
import pandas as pd
from scipy.signal import welch
import tkinter as tk

# Function to calculate band power
def bandpower(eeg_data, fs, band): 
    freqs, psd = welch(eeg_data, fs, nperseg=256)
    idx_band = np.logical_and(freqs >= band[0], freqs <= band[1])
    return np.trapz(psd[idx_band], freqs[idx_band])

# Sampling rate (typically 250 Hz for OpenBCI Cyton)
fs = 250

# Initialize BoardShim
params = BrainFlowInputParams()
params.serial_port = "COM15"  # Change based on your OpenBCI setup

board_id = 0  # Use BoardShim.CYTON_BOARD instead of hardcoded ID
board = BoardShim(board_id, params)
board.prepare_session()
board.start_stream()

# Get all EEG channels
all_eeg_channels = BoardShim.get_eeg_channels(board_id)

# Select 6 specific channels (modify these based on your setup)
selected_channels = all_eeg_channels[:6]  # First 6 EEG channels

# Initialize Excel logging
log_file = "confidence_log.xlsx"
data_log = pd.DataFrame(columns=["Seconds", "Confidence Score"])
start_time = time.time()  # Track elapsed time

# ------ Tkinter GUI for Visualization ------
root = tk.Tk()
root.title("Confidence Level Visualization")

canvas = tk.Canvas(root, width=400, height=200, bg="black")
canvas.pack()

# Confidence bar background
canvas.create_rectangle(50, 75, 350, 125, fill="gray")

# Confidence bar (will update dynamically)
bar = canvas.create_rectangle(50, 75, 50, 125, fill="green")

# Label to display score
label = tk.Label(root, text="Confidence Score: --", font=("Arial", 14), fg="white", bg="black")
label.pack()

def update_bar():
    """Continuously update confidence score from live EEG data and log it to Excel"""
    global board, data_log
    
    # Get latest EEG data buffer
    data = board.get_current_board_data(256)
    
    alpha_power_total = 0
    theta_power_total = 0

    for ch in selected_channels:
        eeg_data = data[ch]
        alpha_power_total += bandpower(eeg_data, fs, [8, 12])
        theta_power_total += bandpower(eeg_data, fs, [4, 7])

    if theta_power_total == 0:
        confidence_score = 0  # Avoid division by zero
    else:
        confidence_score = (alpha_power_total / len(selected_channels)) / (theta_power_total / len(selected_channels))

    # Update GUI
    new_width = min(300, max(10, confidence_score * 100))  # Limit bar size
    canvas.coords(bar, 50, 75, 50 + new_width, 125)
    label.config(text=f"Confidence Score: {confidence_score:.2f}")

    # Log results in Excel
    elapsed_time = int(time.time() - start_time)
    new_data = pd.DataFrame({"Seconds": [elapsed_time], "Confidence Score": [confidence_score]})
    data_log = pd.concat([data_log, new_data], ignore_index=True)

    # Save log every update
    data_log.to_excel(log_file, index=False)

    # Refresh every second
    root.after(1000, update_bar)

# Start updating UI
update_bar()
root.mainloop()

# Stop the board when GUI is closed
board.stop_stream()
board.release_session()