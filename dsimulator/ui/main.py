import dearpygui.dearpygui as dpg
import dsimulator.ui.load as load
import dsimulator.ui.game as ui_game
from dsimulator.game import init_game

def to_new_game():
    init_game()
    dpg.hide_item(main_window)
    dpg.show_item(ui_game.game_window)
    dpg.set_primary_window(ui_game.game_window, True)

def to_load():
    dpg.hide_item(main_window)
    dpg.show_item(load.load_window)
    dpg.set_primary_window(load.load_window, True)

with dpg.window() as main_window:
    dpg.add_text('main window')
    dpg.add_button(label='new', callback=to_new_game)
    dpg.add_button(label='load', callback=to_load)
    dpg.hide_item(main_window)
