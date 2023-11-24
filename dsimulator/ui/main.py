"""
The main window after game startup, containing the main menu.
"""

import dearpygui.dearpygui as dpg
import dsimulator.ui.load as load
import dsimulator.ui.game as ui_game
from dsimulator.game import init_game


def to_new_game():
    """Hide the main window and start a new game."""
    init_game()
    ui_game.update_game_window()
    dpg.hide_item(main_window)
    dpg.show_item(ui_game.game_window)
    dpg.set_primary_window(ui_game.game_window, True)


def to_load():
    """Hide the main window and show the load window."""
    dpg.hide_item(main_window)
    dpg.show_item(load.load_window)
    dpg.set_primary_window(load.load_window, True)


with dpg.window() as main_window:
    dpg.add_text('main window')
    dpg.add_button(label='new', callback=to_new_game)
    dpg.add_button(label='load', callback=to_load)
    dpg.add_button(label='quit', callback=dpg.stop_dearpygui)
    dpg.hide_item(main_window)