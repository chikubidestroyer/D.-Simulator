"""
The user interface for the game window where the game is running in.
"""

import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main
import dsimulator.ui.save as save
from dsimulator.game import query_inhabitant


def to_save():
    """Hide the game window show the save window."""
    dpg.hide_item(game_window)
    dpg.show_item(save.save_window)
    dpg.set_primary_window(save.save_window, True)


def to_main():
    """Hide the game window and go back to main window."""
    dpg.hide_item(game_window)
    dpg.show_item(main.main_window)
    dpg.set_primary_window(main.main_window, True)


with dpg.window() as game_window:
    dpg.add_text('game window')
    query_table = dpg.add_table()
    dpg.add_button(label='save', callback=to_save)
    dpg.add_button(label='quit', callback=to_main)
    dpg.hide_item(game_window)


def update_game_window():
    "Update the query table/results in the game window."
    dpg.delete_item(query_table, children_only=True)
    inhabitant_columns, inhabitant_rows = query_inhabitant()
    for c in inhabitant_columns:
        dpg.add_table_column(label=c, parent=query_table)
    for r in inhabitant_rows:
        with dpg.table_row(parent=query_table):
            for c in r:
                dpg.add_text(c)