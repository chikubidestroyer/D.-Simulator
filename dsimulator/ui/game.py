"""The user interface for the game window where the game is running in."""

import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main
import dsimulator.ui.save as save
from dsimulator.game import close_game, list_inhabitant, list_vertex, list_edge, list_building
from dsimulator.defs import MAIN_WIDTH, MAIN_HEIGHT
import math
from typing import List, Tuple, Callable


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


def make_building_clicked(buildings: List[Tuple[int, int, int]], b_size: int) -> Callable[[], None]:
    """Create a callback function that is called when any building is clicked."""
    def building_clicked() -> None:
        pos = dpg.get_drawing_mouse_pos()
        for b in buildings:
            if b[0] - b_size <= pos[0] <= b[0] + b_size and b[1] - b_size <= pos[1] <= b[1] + b_size:
                print('Clicked building: {}'.format(b[2]))
    return building_clicked


with dpg.window() as game_window:
    with dpg.group(height=0.93 * MAIN_HEIGHT, horizontal=True):
        with dpg.child_window(width=0.4 * MAIN_WIDTH, horizontal_scrollbar=True):
            dpg.add_text('Map')
            game_map = dpg.add_drawlist(width=1500, height=1500)

        with dpg.child_window():
            dpg.add_text('Query Result')
            query_table = dpg.add_table(policy=dpg.mvTable_SizingStretchProp)

    with dpg.group(horizontal=True):
        dpg.add_button(label='Save Game', callback=to_save)
        dpg.add_button(label='Quit to Main Menu', callback=to_main)
    dpg.hide_item(game_window)


def update_game_window() -> None:
    """Update the game map and query result in the game window."""
    dpg.delete_item(game_map, children_only=True)
    scale = 140
    offset = 1
    for x, y in list_vertex():
        dpg.draw_circle(((x + offset) * scale, (y + offset) * scale), 10, color=(255, 255, 255, 255), fill=(255, 255, 255, 255), parent=game_map)

    buildings = []
    b_size = 20
    for x, y, id in list_building():
        xd = (x + offset) * scale
        yd = (y + offset) * scale
        dpg.draw_rectangle((xd - b_size, yd - b_size), (xd + b_size, yd + b_size), color=(255, 0, 0, 255), fill=(255, 0, 0, 255), parent=game_map)
        buildings.append((xd, yd, id))

    with dpg.item_handler_registry() as handler:
        dpg.add_item_clicked_handler(callback=make_building_clicked(buildings, b_size))
    dpg.bind_item_handler_registry(game_map, handler)

    font_size = 20
    shift = 12
    for sx, sy, ex, ey, c in list_edge():
        s = ((sx + offset) * scale, (sy + offset) * scale)
        e = ((ex + offset) * scale, (ey + offset) * scale)

        dx = e[0] - s[0]
        dy = e[1] - s[1]
        len = math.sqrt(dx**2 + dy**2)
        shift_x = -shift * dy / len
        shift_y = shift * dx / len

        dpg.draw_line(s, e, thickness=4, color=(255, 255, 255, 255), parent=game_map)
        dpg.draw_text(((s[0] / 3 + 2 * e[0] / 3) - font_size / 2 + shift_x, (s[1] / 3 + 2 * e[1] / 3) - font_size / 2 + shift_y),
                      str(c), size=font_size, parent=game_map)

    dpg.delete_item(query_table, children_only=True)
    inhabitant_columns, inhabitant_rows = list_inhabitant()
    for c in inhabitant_columns:
        dpg.add_table_column(label=c, parent=query_table)
    for r in inhabitant_rows:
        with dpg.table_row(parent=query_table):
            for c in r:
                dpg.add_text(c)
