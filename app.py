import time
import tkinter as tk
from tkinter import ttk
import sv_ttk
import threading
import ctypes
from pynput import mouse
from pynput.mouse import Button as MouseButton, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener

user32 = ctypes.WinDLL('user32', use_last_error=True)

GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_DLGFRAME = 0x00400000
WS_BORDER = 0x00800000
WS_MAXIMIZEBOX = 0x00010000
WS_MINIMIZEBOX = 0x00020000
WS_SYSMENU = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WS_EX_WINDOWEDGE = 0x00000100
WS_EX_CLIENTEDGE = 0x00000200
SWP_FRAMECHANGED = 0x0020
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
SWP_NOACTIVATE = 0x0010

status = "idle"
click_count = 0
cps = 10
mode = "toggle"
button = "left"
trigger_key = "f6"
running = False
pressing = False
recording = False
recorded_key = None

mouse_controller = MouseController()

def get_mouse_button():
    if button == "left":
        return MouseButton.left
    else:
        return MouseButton.right

def click_loop():
    global click_count, running, status
    interval = 1.0 / max(cps, 1)
    btn = get_mouse_button()
    while running:
        if not running:
            break
        mouse_controller.click(btn)
        click_count += 1
        safe_update_ui()
        time.sleep(interval)

clicker_thread = None

def start_clicker():
    global running, clicker_thread, status, click_count
    if running:
        return
    running = True
    status = "running"
    safe_update_ui()
    clicker_thread = threading.Thread(target=click_loop, daemon=True)
    clicker_thread.start()

def stop_clicker():
    global running, status
    running = False
    status = "idle"
    safe_update_ui()

def toggle_clicker():
    if running:
        stop_clicker()
    else:
        start_clicker()

def safe_update_ui():
    try:
        root.after(0, update_ui)
    except Exception:
        pass

def update_ui():
    status_var.set(f"status: {status}")
    clicks_var.set(str(click_count))

def on_key_press(key):
    global pressing
    try:
        key_name = key.char.lower()
    except AttributeError:
        key_name = key.name.lower()

    if recording:
        return

    if key_name == trigger_key.lower():
        if mode == "toggle":
            toggle_clicker()
        elif mode == "press":
            pressing = True
            start_clicker()

def on_key_release(key):
    global pressing
    if mode != "press":
        return
    try:
        key_name = key.char.lower()
    except AttributeError:
        key_name = key.name.lower()
    if key_name == trigger_key.lower():
        pressing = False
        stop_clicker()

def start_recording():
    global recording, recorded_key, status
    if recording:
        return
    recording = True
    status = "recording"
    trigger_var.set("...")
    safe_update_ui()
    threading.Thread(target=record_input, daemon=True).start()

def record_input():
    global recording, recorded_key
    recorded_key = None
    stop_event = threading.Event()

    def on_click(x, y, btn, pressed):
        global recorded_key
        if pressed and recording:
            recorded_key = f"mouse_{str(btn).split('.')[-1]}"
            stop_event.set()
            return False

    m_listener = mouse.Listener(on_click=on_click)
    m_listener.start()

    def on_press(key):
        global recorded_key
        if recording:
            try:
                recorded_key = key.char.lower()
            except AttributeError:
                recorded_key = key.name.lower()
            stop_event.set()
            return False

    k_listener = KeyboardListener(on_press=on_press)
    k_listener.start()

    stop_event.wait()
    m_listener.stop()
    k_listener.stop()
    root.after(0, finish_recording)

def finish_recording():
    global recording, status, trigger_key
    recording = False
    status = "idle"
    if recorded_key:
        trigger_key = recorded_key
        trigger_var.set(trigger_key)
    else:
        trigger_var.set(trigger_key)
    safe_update_ui()

def on_cps_change(*args):
    global cps
    try:
        cps = int(cps_var.get())
    except ValueError:
        cps = 10

def on_mode_change():
    global mode
    mode = mode_var.get()

def on_button_change():
    global button
    button = button_var.get()

def reset_clicks():
    global click_count
    click_count = 0
    safe_update_ui()

hwnd = None

def get_hwnd():
    global hwnd
    if hwnd is None or hwnd == 0:
        tk_id = root.winfo_id()
        hwnd = ctypes.windll.user32.GetParent(tk_id)
        if hwnd == 0:
            hwnd = tk_id
    return hwnd

def make_borderless_taskbar():
    root.update_idletasks()
    h = get_hwnd()
    if not h:
        root.after(50, make_borderless_taskbar)
        return
    style = ctypes.windll.user32.GetWindowLongW(h, GWL_STYLE)
    exstyle = ctypes.windll.user32.GetWindowLongW(h, GWL_EXSTYLE)

    style &= ~(WS_CAPTION | WS_THICKFRAME | WS_DLGFRAME | WS_BORDER | WS_MAXIMIZEBOX)
    style |= WS_MINIMIZEBOX | WS_SYSMENU
    exstyle &= ~WS_EX_TOOLWINDOW
    exstyle |= WS_EX_APPWINDOW
    exstyle &= ~(WS_EX_WINDOWEDGE | WS_EX_CLIENTEDGE)

    ctypes.windll.user32.SetWindowLongW(h, GWL_STYLE, style)
    ctypes.windll.user32.SetWindowLongW(h, GWL_EXSTYLE, exstyle)
    ctypes.windll.user32.SetWindowPos(
        h, 0, 0, 0, 0, 0,
        SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER |
        SWP_NOACTIVATE | SWP_SHOWWINDOW
    )

def minimize_window():
    root.wm_iconify()

def close_window():
    root.destroy()

def start_move(event):
    global x, y
    x = event.x
    y = event.y

def on_move(event):
    deltax = event.x - x
    deltay = event.y - y
    new_x = root.winfo_x() + deltax
    new_y = root.winfo_y() + deltay
    root.geometry(f"+{new_x}+{new_y}")

root = tk.Tk()
root.title("Senanto Auto Clicker")
root.geometry("320x370")
root.resizable(False, False)

sv_ttk.set_theme("dark")
root.after(10, make_borderless_taskbar)

title_frame = ttk.Frame(root)
title_frame.pack(fill=tk.X, pady=(0, 5))

title_label = ttk.Label(title_frame, text="Senanto Auto Clicker", font=("Segoe UI", 10, "bold"))
title_label.pack(side=tk.LEFT, padx=10)

for w in (title_frame, title_label):
    w.bind("<Button-1>", start_move)
    w.bind("<B1-Motion>", on_move)

btn_frame_title = ttk.Frame(title_frame)
btn_frame_title.pack(side=tk.RIGHT, padx=5)

ttk.Button(btn_frame_title, text="─", width=3, command=minimize_window).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_frame_title, text="✕", width=3, command=close_window).pack(side=tk.LEFT, padx=2)

main_frame = ttk.Frame(root, padding=15)
main_frame.pack(fill=tk.BOTH, expand=True)

status_var = tk.StringVar(value="status: idle")
ttk.Label(main_frame, textvariable=status_var, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 10))

settings_frame = ttk.Frame(main_frame)
settings_frame.pack(fill=tk.X, pady=5)

ttk.Label(settings_frame, text="# clicks").grid(row=0, column=0, sticky=tk.W, pady=3)
clicks_var = tk.StringVar(value="0")
ttk.Entry(settings_frame, textvariable=clicks_var, state="readonly", width=10).grid(row=0, column=1, sticky=tk.E, pady=3)

ttk.Label(settings_frame, text="clicks/s").grid(row=1, column=0, sticky=tk.W, pady=3)
cps_var = tk.StringVar(value=str(cps))
cps_entry = ttk.Entry(settings_frame, textvariable=cps_var, width=10)
cps_entry.grid(row=1, column=1, sticky=tk.E, pady=3)
cps_var.trace_add('write', on_cps_change)

ttk.Label(settings_frame, text="trigger").grid(row=2, column=0, sticky=tk.W, pady=3)
trigger_var = tk.StringVar(value=trigger_key)
trigger_entry = ttk.Entry(settings_frame, textvariable=trigger_var, state="readonly", width=10)
trigger_entry.grid(row=2, column=1, sticky=tk.E, pady=3)

record_btn = ttk.Button(main_frame, text="Set Keybind", command=start_recording)
record_btn.pack(fill=tk.X, pady=5)

bottom_frame = ttk.Frame(main_frame)
bottom_frame.pack(fill=tk.X, pady=10)

mode_frame = ttk.LabelFrame(bottom_frame, text="press / toggle", padding=5)
mode_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
mode_var = tk.StringVar(value=mode)
ttk.Radiobutton(mode_frame, text="press", variable=mode_var, value="press", command=on_mode_change).pack(anchor=tk.W)
ttk.Radiobutton(mode_frame, text="toggle", variable=mode_var, value="toggle", command=on_mode_change).pack(anchor=tk.W)

btn_frame = ttk.LabelFrame(bottom_frame, text="mouse button", padding=5)
btn_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
button_var = tk.StringVar(value=button)
ttk.Radiobutton(btn_frame, text="left", variable=button_var, value="left", command=on_button_change).pack(anchor=tk.W)
ttk.Radiobutton(btn_frame, text="right", variable=button_var, value="right", command=on_button_change).pack(anchor=tk.W)

keyboard_listener = KeyboardListener(on_press=on_key_press, on_release=on_key_release)
keyboard_listener.start()

root.mainloop()