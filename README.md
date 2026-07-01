# Modern Auto Clicker

A sleek, modern auto clicker built with Python, `sv_ttk`, and `pynput`. Features a borderless dark-themed UI, global hotkey support, and real-time key/mouse binding.

![License](https://img.shields.io/badge/License-MIT-green.svg)
## Download

[Download App](https://github.com/senanto/auto-clicker/releases/download/v1/auto-clicker.exe)
---
## Preview
<img width="418" height="462" alt="image" src="https://github.com/user-attachments/assets/9e369a7e-565c-49a6-977d-20cece37f165" />

## Features

- **Dark Modern UI** — Clean borderless window with `sv_ttk` Sun Valley theme
- **Global Hotkey** — Trigger works even when the app is not focused
- **Keybind Recording** — Press any key or mouse button to set the trigger instantly
- **Press / Toggle Modes** — Hold to click or toggle on/off
- **Mouse Button Selection** — Left or Right click
- **Live Click Counter** — Real-time click tracking
- **Adjustable CPS** — Set clicks per second on the fly

## Requirements

```bash
pip install sv_ttk pynput
```

## Usage

```bash
python app.py
```

| Setting | Description |
|---------|-------------|
| **clicks/s** | Clicks per second (e.g. `10`, `50`, `100`) |
| **trigger** | The key/mouse button that starts/stops clicking |
| **Set Keybind** | Click to record a new trigger key or mouse button |
| **press** | Hold the trigger to click, release to stop |
| **toggle** | Press the trigger once to start, again to stop |
| **left / right** | Choose which mouse button to simulate |

## License

This project is licensed under the [MIT License](LICENSE).

