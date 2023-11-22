"""
The window to select save slots to save into.
"""

import dearpygui.dearpygui as dpg
import dsimulator.ui.game as game_ui
from dsimulator.game import list_save, write_save, delete_save
from typing import Callable


def to_game():
    """Hide the save window and go back to game window."""
    dpg.hide_item(save_window)
    dpg.show_item(game_ui.game_window)
    dpg.set_primary_window(game_ui.game_window, True)


def new_save():
    write_save()
    update_save_window()


with dpg.window() as save_window:
    dpg.add_text('Save Game')
    save_table = dpg.add_table(header_row=False, policy=dpg.mvTable_SizingStretchProp)
    dpg.add_button(label='New Save', callback=new_save)
    dpg.add_button(label='Back', callback=to_game)
    dpg.hide_item(save_window)


def make_write(save_id: int) -> Callable[[], None]:
    """Create a callback function that overwrites the specific save slot."""
    def write() -> None:
        write_save(save_id)
        update_save_window()
    return write


def make_delete(save_id: int) -> Callable[[], None]:
    """Create a callback function that deletes the specific save slot."""
    def delete() -> None:
        delete_save(save_id)
        update_save_window()
    return delete


def update_save_window() -> None:
    """Update the save window, reconstruct the save table."""
    dpg.delete_item(save_table, children_only=True)

    for _ in range(3):
        dpg.add_table_column(parent=save_table)

    save = list_save()
    for r in save:
        with dpg.table_row(parent=save_table):
            dpg.add_text('Save {}\tTime: {}'.format(r[0], r[1]))
            dpg.add_button(label='Overwrite', callback=make_write(r[0]))
            dpg.add_button(label='Delete', callback=make_delete(r[0]))
