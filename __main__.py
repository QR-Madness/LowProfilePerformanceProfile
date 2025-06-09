from profile import L3PProfile
from tray import L3PTray
import threading

def run_dpg(l3p_profile: L3PProfile):
    l3p_profile.run()

def run_tray(show_profile_event):
    app = L3PTray(show_profile_event)
    app.run()

if __name__ == '__main__':
    # Create an event for showing/hiding the profile
    show_profile_event = threading.Event()

    # Create the profile instance
    l3p_profile = L3PProfile()

    # Create threads for DPG and tray
    tray_thread = threading.Thread(target=run_tray, args=(show_profile_event,))
    dpg_thread = threading.Thread(target=run_dpg, args=(l3p_profile,), daemon=True)

    # Start both threads
    tray_thread.start()

    while tray_thread.is_alive():
        if show_profile_event.is_set():
            dpg_thread.start()
            show_profile_event.clear()
        elif dpg_thread.is_alive():
            dpg_thread.join()
            dpg_thread = threading.Thread(target=run_dpg, args=(l3p_profile,), daemon=True)
        else:
            show_profile_event.wait(0.1)

    # Wait for threads to complete
    tray_thread.join()
    dpg_thread.join()
