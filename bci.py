from brainflow.board_shim import BoardShim, BrainFlowInputParams
from scipy.signal import welch
from collections import deque
import time
import numpy as np
import tkinter as tk
import win32com.client

# ----------- Global variables (uninitialized until setup) ----------- #
board = None
FS = 250
selected_channels = []

################ Getting the BCI port automatically ######################
def get_bci_com_port(keyword="Cyton"):  #Make list of keywords later if necessary
    try:
        wmi = win32com.client.GetObject("winmgmts:")
        for port in wmi.InstancesOf("Win32_SerialPort"):
            desc = port.Name or port.Description
            if keyword.lower() in desc.lower():
                print(f"BCI device found: {desc} on {port.DeviceID}")
                return port.DeviceID
        print("BCI device not found.")
    except Exception as e:
        print(f"An error occurred while searching for the BCI device: {e}")
    return None

# ----------- BCI SETUP ----------- #
def setup_board():
    global board, FS, selected_channels  # Declare globals to modify them here
    params = BrainFlowInputParams()
    params.serial_port =  "COM15"  # get_bci_com_port() or Pass this into the function
    board_id = 0  # CYTON_BOARD = 0
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()

    eeg_channels = BoardShim.get_eeg_channels(board_id)
    selected_channels = eeg_channels[:6]  # Choose channels

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

def calibrate_confidence(duration=30):
    root = tk.Tk()
    root.title("Baseline Calculation Running")
    message = tk.Label(
        root,
        text="Calibrating baseline confidence... Please relax and stay still.",
        height=15,
        width=75,
        font=("Courier", 10)
    )
    message.pack()
        
    baseline_scores = []
    start_time = time.time()

    def update_baseline():
        current_time = time.time()
        elapsed = current_time - start_time
            
        if elapsed < duration:
            score = get_confidence_score()
            baseline_scores.append(score)
            print(f"Recorded: {score:.2f}")
            root.after(1000, update_baseline)
        else:
            mean = np.mean(baseline_scores)
            std = np.std(baseline_scores)
            print(f"Calibration Complete — Initial Threshold: {mean + 0.75 * std:.2f}")
            root.destroy()
        
    update_baseline()
    root.mainloop()
        
    return deque(baseline_scores[-10:], maxlen=10)

def cleanup():
    board.stop_stream()
    board.release_session()
