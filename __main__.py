from profile import L3PProfile
from tray import L3PTray
import threading

def run_dpg():
    # profile = L3PProfile()
    # profile.run()
    pass

def run_tray():
    app = L3PTray()
    app.run()

if __name__ == '__main__':
    # Create threads for DPG and tray
    dpg_thread = threading.Thread(target=run_dpg, daemon=True)
    tray_thread = threading.Thread(target=run_tray)

    # Start both threads
    dpg_thread.start()
    tray_thread.start()

    # Wait for threads to complete
    tray_thread.join()
    dpg_thread.join()
