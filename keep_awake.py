"""Keep Windows and its display awake until stopped with Ctrl+C or a hotkey."""

import ctypes
from ctypes import wintypes
import random
from threading import Event

import keyboard
import mouse

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
STOP_HOTKEY = "ctrl+c"


def set_execution_state(state: int) -> None:
    """Set the Windows execution state, raising an error if the call fails."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    set_state = kernel32.SetThreadExecutionState
    set_state.argtypes = (wintypes.DWORD,)
    set_state.restype = wintypes.DWORD

    if set_state(state) == 0:
        raise ctypes.WinError(ctypes.get_last_error())


def main() -> None:

    if not hasattr(ctypes, "WinDLL"):
        raise OSError("This script requires Windows.")

    keep_awake_state = (
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )
    stop_requested = Event()
    hotkey = None
    mouse_hook = None
    try:
        set_execution_state(keep_awake_state)
        hotkey = keyboard.add_hotkey(STOP_HOTKEY, stop_requested.set)
        mouse_hook = mouse.on_button(
            stop_requested.set,
            buttons=("left",),
            types=("down",),
        )
        print(
            "Keeping Windows and the display awake. "
            f"Left-click or press {STOP_HOTKEY.upper()} to stop."
        )
        while not stop_requested.wait(1.0):
            # mouse movement
            set_execution_state(keep_awake_state)
            cur_x, cur_y = mouse.get_position()
            new_y = cur_y + random.randint(-10, 10)
            mouse.move(cur_x, new_y, absolute=True, duration=0)
    finally:
        try:
            if mouse_hook is not None:
                mouse.unhook(mouse_hook)
        finally:
            try:
                if hotkey is not None:
                    keyboard.remove_hotkey(hotkey)
            finally:
                set_execution_state(ES_CONTINUOUS)

if __name__ == "__main__":
    main()
