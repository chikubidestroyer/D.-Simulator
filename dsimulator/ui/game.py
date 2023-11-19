import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main

def to_main():
    dpg.hide_item(game_window)
    dpg.show_item(main.main_window)
    dpg.set_primary_window(main.main_window, True)

with dpg.window() as game_window:
    dpg.add_text('game window')
    dpg.add_button(label='quit', callback=to_main)
    dpg.hide_item(game_window)
