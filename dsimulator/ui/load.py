"""The window to select save slots to load from."""

import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main
import dsimulator.ui.game as ui_game
from dsimulator.game import list_save, read_save, delete_save
from typing import Callable


def to_main() -> None:
    """Hide the load window and go back to main window."""
    dpg.hide_item(load_window)
    dpg.show_item(main.main_window)
    dpg.set_primary_window(main.main_window, True)


with dpg.window() as load_window:
    dpg.add_text('Load Game')
    save_table = dpg.add_table(header_row=False, policy=dpg.mvTable_SizingStretchProp)
    dpg.add_button(label='Back', callback=to_main)
    dpg.hide_item(load_window)


def make_load(save_id: int) -> Callable[[], None]:
    """Create a callback function that loads the specific save slot."""
    def load() -> None:
        read_save(save_id)
        ui_game.update_game_window()
        dpg.hide_item(load_window)
        dpg.show_item(ui_game.game_window)
        dpg.set_primary_window(ui_game.game_window, True)
    return load


def make_delete(save_id: int) -> Callable[[], None]:
    """Create a callback function that deletes the specific save slot."""
    def delete() -> None:
        delete_save(save_id)
        update_load_window()
    return delete


def update_load_window() -> None:
    """Update the load window, reconstruct the save table."""
    dpg.delete_item(save_table, children_only=True)

    for _ in range(3):
        dpg.add_table_column(parent=save_table)

    save = list_save()
    for r in save:
        with dpg.table_row(parent=save_table):
            dpg.add_text('Save {}\tTime: {}'.format(r[0], r[1]))
            dpg.add_button(label='Load', callback=make_load(r[0]))
            dpg.add_button(label='Delete', callback=make_delete(r[0]))
