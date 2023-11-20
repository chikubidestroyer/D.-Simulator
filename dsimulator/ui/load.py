"""
The window to select save files to load from.
"""

import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main


def to_main():
    """Hide the load window and go back to main window."""
    dpg.hide_item(load_window)
    dpg.show_item(main.main_window)
    dpg.set_primary_window(main.main_window, True)


with dpg.window() as load_window:
    dpg.add_text('load window')
    dpg.add_button(label='back', callback=to_main)
    dpg.hide_item(load_window)
