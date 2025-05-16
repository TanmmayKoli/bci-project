import win32com.client

def get_bci_com_port(keyword="Cyton"):
    """Returns the COM port of the BCI device matching a keyword in the description."""
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

# Example usage
if __name__ == "__main__":
    com_port = get_bci_com_port()
    if com_port:
        print(f"Using COM port: {com_port}")
    else:
        print("Please connect the BCI device.")
