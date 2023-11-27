"""The user interface for the game window where the game is running in."""

import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main
import dsimulator.ui.save as save
from dsimulator.game import close_game, query_inhabitant


def to_save() -> None:
    """Hide the game window show the save window."""
    save.update_save_window()
    dpg.hide_item(game_window)
    dpg.show_item(save.save_window)
    dpg.set_primary_window(save.save_window, True)


def to_main() -> None:
    """Hide the game window and go back to main window."""
    close_game()
    dpg.hide_item(game_window)
    dpg.show_item(main.main_window)
    dpg.set_primary_window(main.main_window, True)


with dpg.window() as game_window:
    dpg.add_text('Query Result')
    query_table = dpg.add_table(policy=dpg.mvTable_SizingStretchProp)
    dpg.add_button(label='Save Game', callback=to_save)
    dpg.add_button(label='Quit to Main Menu', callback=to_main)
    dpg.hide_item(game_window)


def update_game_window() -> None:
    """Update the query table/results in the game window."""
    dpg.delete_item(query_table, children_only=True)
    inhabitant_columns, inhabitant_rows = query_inhabitant()
    for c in inhabitant_columns:
        dpg.add_table_column(label=c, parent=query_table)
    for r in inhabitant_rows:
        with dpg.table_row(parent=query_table):
            for c in r:
                dpg.add_text(c)
