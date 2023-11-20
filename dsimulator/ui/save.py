"""
The window to select save slots to save into.
"""

import dearpygui.dearpygui as dpg
import dsimulator.ui.game as game_ui


def to_game():
    """Hide the save window and go back to game window."""
    dpg.hide_item(save_window)
    dpg.show_item(game_ui.game_window)
    dpg.set_primary_window(game_ui.game_window, True)


with dpg.window() as save_window:
    dpg.add_text('save window')
    dpg.add_button(label='back', callback=to_game)
    dpg.hide_item(save_window)
