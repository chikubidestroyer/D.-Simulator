"""The user interface for the game window where the game is running in."""

from typing import List, Tuple, Callable
import sqlite3
import math
from dsimulator.defs import MAIN_WIDTH, MAIN_HEIGHT
import dearpygui.dearpygui as dpg
import dsimulator.ui.main as main
import dsimulator.ui.save as save
import dsimulator.game as game


def close_details() -> None:
    """Close the detail views."""
    close_building_detail()
    close_inhabitant_detail()


def hide_windows() -> None:
    """Hide the pop-up windows."""
    dpg.hide_item(victim_window)
    dpg.hide_item(suspect_window)
    dpg.hide_item(lose_window)
    dpg.hide_item(win_window)
    dpg.hide_item(wrong_window)


def to_save() -> None:
    """Hide the game window show the save window."""
    save.update_save_window()
    hide_windows()
    dpg.hide_item(game_window)
    dpg.show_item(save.save_window)
    dpg.set_primary_window(save.save_window, True)


def to_main() -> None:
    """Hide the game window and go back to main window."""
    game.close_game()
    close_details()
    hide_windows()
    dpg.hide_item(game_window)
    dpg.show_item(main.main_window)
    dpg.set_primary_window(main.main_window, True)


def draw_inhabitants_table(data: Tuple[Tuple[str, ...], List[Tuple]]) -> None:
    """Draw a table about inhabitants given the name of the attributes and the tuples of inhabitants."""
    inhabitant_columns, inhabitant_rows = data

    with dpg.table(policy=dpg.mvTable_SizingStretchProp):
        for c in inhabitant_columns:
            dpg.add_table_column(label=c)
        dpg.add_table_column()

        for r in inhabitant_rows:
            with dpg.table_row():
                for c in r:
                    dpg.add_text(c)
                dpg.add_button(label='Details', callback=make_inhabitant_clicked(r[0]))


def make_building_clicked(buildings: List[Tuple[int, int, int]], b_size: int) -> Callable[[], None]:
    """Create a callback function that is called when any building is clicked."""
    def building_clicked() -> None:
        pos = dpg.get_drawing_mouse_pos()
        for b in buildings:
            if b[0] - b_size <= pos[0] <= b[0] + b_size and b[1] - b_size <= pos[1] <= b[1] + b_size:
                show_building_detail(b[2])
    return building_clicked


def show_building_detail(building_id: int) -> None:
    """Replace the game map with a view of building detail."""
    dpg.hide_item(map_view)

    building_name, lockdown, home = game.query_building_summary(building_id)
    with dpg.group(tag='building_detail', parent=left_view):
        with dpg.group(horizontal=True):
            dpg.add_text(building_name)
            dpg.add_button(label='Close', callback=close_building_detail)
            dpg.add_button(label='Set Lockdown', callback=make_set_lockdown(building_id))

        dpg.add_text(('Home, ' if home == 1 else 'Workplace, ')
                     + ('under lockdown' if lockdown == 1 else 'not under lockdown'))

        if home == 1:
            low, high = game.query_home_income(building_id)
            if high is None:
                dpg.add_text('Income equal or greater than {}'.format(low))
            else:
                dpg.add_text('Income between {} and {}'.format(low, high))

            inhabitant_data = game.query_inhabitant(home_building_id=building_id)
        else:
            dpg.add_separator()
            dpg.add_text('Occupations')
            occupation_columns, occupation_rows = game.query_workplace_occupation(building_id)
            with dpg.table(policy=dpg.mvTable_SizingStretchProp):
                for c in occupation_columns:
                    dpg.add_table_column(label=c)
                for r in occupation_rows:
                    with dpg.table_row():
                        for c in r:
                            dpg.add_text(c)

            inhabitant_data = game.query_inhabitant(workplace_building_id=building_id)

        dpg.add_separator()
        dpg.add_text('Inhabitants')
        draw_inhabitants_table(inhabitant_data)

        dpg.add_separator()
        dpg.add_text('Witness Counts')
        result = game.query_witness_count(building_id)
        with dpg.table(policy=dpg.mvTable_SizingStretchProp):
            dpg.add_table_column(label='inhabitant_id')
            dpg.add_table_column(label='first_name')
            dpg.add_table_column(label='last_name')
            dpg.add_table_column(label='count')
            dpg.add_table_column()

            for r in result:
                with dpg.table_row():
                    for c in r:
                        dpg.add_text(c)
                    dpg.add_button(label='Details', callback=make_inhabitant_clicked(r[0]))


def close_building_detail() -> None:
    """Close the building detail view."""
    if dpg.does_item_exist('building_detail'):
        dpg.delete_item('building_detail')
        dpg.show_item(map_view)


def make_set_lockdown(building_id: int) -> Callable[[], None]:
    """Return a function that sets a building to lockdown."""
    def set_lockdown() -> None:
        game.lockdown(building_id)
        close_building_detail()
        update_game_window()
        show_building_detail(building_id)
    return set_lockdown


def make_accuse(inhabitant_id: int) -> Callable[[], None]:
    """Return a function that accuses the given inhabitant."""
    def accuse() -> None:
        if game.end_game_condition(inhabitant_id)[1]:
            dpg.show_item(win_window)
        else:
            dpg.show_item(wrong_window)
    return accuse


def make_modify_suspect(inhabitant_id: int) -> Callable[[], None]:
    """Return a function that set/unset given inhabitant in suspect."""
    def f() -> None:
        game.modify_suspect(inhabitant_id)
        update_suspect()
    return f


def make_inhabitant_clicked(inhabitant_id: int) -> Callable[[], None]:
    """Create a callback function that is called when a inhabitant row is clicked."""
    def inhabitant_clicked() -> None:
        close_inhabitant_detail()
        dpg.hide_item(query_view)
        with dpg.group(tag='inhabitant_detail', parent=right_view):
            with dpg.group(horizontal=True):
                dpg.add_text('Inhabitant Detail')
                dpg.add_button(label='Close', callback=close_inhabitant_detail)
                dpg.add_button(label='Accuse', callback=make_accuse(inhabitant_id))
                dpg.add_button(label='Toggle Suspect', callback=make_modify_suspect(inhabitant_id))

            keys, values = game.query_inhabitant_detail(inhabitant_id)
            with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
                dpg.add_table_column()
                dpg.add_table_column()

                for k, v in zip(keys, values):
                    with dpg.table_row():
                        dpg.add_text(k)
                        dpg.add_text(v)

            dpg.add_separator()
            dpg.add_text('Relationships')

            relationship_rows = game.query_inhabitant_relationship(inhabitant_id)
            with dpg.table(policy=dpg.mvTable_SizingStretchProp):
                dpg.add_table_column(label='inhabitant_id')
                dpg.add_table_column(label='object_first_name')
                dpg.add_table_column(label='object_last_name')
                dpg.add_table_column(label='description')
                dpg.add_table_column()

                for r in relationship_rows:
                    with dpg.table_row():
                        for c in r:
                            dpg.add_text(c)
                        dpg.add_button(label='Details', callback=make_inhabitant_clicked(r[0]))

    return inhabitant_clicked


def close_inhabitant_detail() -> None:
    """Close the inhabitant detail view."""
    if dpg.does_item_exist('inhabitant_detail'):
        dpg.delete_item('inhabitant_detail')
        dpg.show_item(query_view)


def show_victim() -> None:
    """Show all the victims in a window."""
    update_victim()
    dpg.show_item(victim_window)


def update_victim() -> None:
    """Update the victim window."""
    dpg.delete_item(victim_window, children_only=True)
    with dpg.group(parent=victim_window):
        draw_inhabitants_table(game.query_inhabitant(dead=True))


def show_suspect() -> None:
    """Show all the victims in a window."""
    update_suspect()
    dpg.show_item(suspect_window)


def update_suspect() -> None:
    """Update the suspect window."""
    dpg.delete_item(suspect_window, children_only=True)
    with dpg.group(parent=suspect_window):
        draw_inhabitants_table(game.query_inhabitant(suspect=True))


def next_turn() -> None:
    """Execute one turn of the game."""
    game.next_day()
    hide_windows()
    update_game_window()


def update_game_window() -> None:
    """Update the status, game map, and query result in the game window."""
    dpg.set_value(day_text, 'Current Day {}'.format(game.day))
    dpg.set_value(resig_text, 'Resignation Day {}'.format(game.resig_day))
    if game.end_game_condition()[0]:
        dpg.show_item(lose_window)

    dpg.delete_item(game_map, children_only=True)
    scale = 180
    offset = 1
    for x, y in game.list_vertex():
        dpg.draw_circle(((x + offset) * scale, (y + offset) * scale), 10, color=(255, 255, 255, 255), fill=(255, 255, 255, 255), parent=game_map)

    font_size = 20
    shift = 12
    for sx, sy, ex, ey, c in game.list_edge():
        s = ((sx + offset) * scale, (sy + offset) * scale)
        e = ((ex + offset) * scale, (ey + offset) * scale)

        dx = e[0] - s[0]
        dy = e[1] - s[1]
        length = math.sqrt(dx**2 + dy**2)
        shift_x = -shift * dy / length
        shift_y = shift * dx / length

        dpg.draw_line(s, e, thickness=4, color=(255, 255, 255, 255), parent=game_map)
        dpg.draw_text(((s[0] / 3 + 2 * e[0] / 3) - font_size / 2 + shift_x, (s[1] / 3 + 2 * e[1] / 3) - font_size / 2 + shift_y),
                      str(c), size=font_size, parent=game_map)

    buildings = []
    b_size = 20
    for x, y, building_id, building_name in game.list_building():
        xd = (x + offset) * scale
        yd = (y + offset) * scale
        dpg.draw_rectangle((xd - b_size, yd - b_size), (xd + b_size, yd + b_size), color=(255, 0, 0, 255), fill=(255, 0, 0, 255), parent=game_map)
        dpg.draw_text((xd - b_size, yd + b_size), building_name, size=font_size, color=(255, 0, 0, 255), parent=game_map)
        buildings.append((xd, yd, building_id))

    with dpg.item_handler_registry() as map_handler:
        dpg.add_item_clicked_handler(callback=make_building_clicked(buildings, b_size))
    dpg.bind_item_handler_registry(game_map, map_handler)

    dpg.delete_item(query_table, children_only=True)

    try:
        income_lo = dpg.get_value(income_lo_input)
        income_lo = int(income_lo) if len(income_lo) > 0 else None
        income_hi = dpg.get_value(income_hi_input)
        income_hi = int(income_hi) if len(income_hi) > 0 else None
        occupation = dpg.get_value(occupation_input)
        occupation = occupation if len(occupation) > 0 else None
        gender = dpg.get_value(gender_input)
        gender = gender if len(gender) > 0 else None
        dead = dpg.get_value(dead_input)
        dead = (int(dead) == 1) if len(dead) > 0 else None
        home_building_name = dpg.get_value(home_building_name_input)
        home_building_name = home_building_name if len(home_building_name) > 0 else None
        workplace_building_name = dpg.get_value(workplace_building_name_input)
        workplace_building_name = workplace_building_name if len(workplace_building_name) > 0 else None
        custody = dpg.get_value(custody_input)
        custody = (int(custody) == 1) if len(custody) > 0 else None
        suspect = dpg.get_value(suspect_input)
        suspect = (int(suspect) == 1) if len(suspect) > 0 else None

        inhabitant_columns, inhabitant_rows = game.query_inhabitant(
            income_lo=income_lo, income_hi=income_hi, occupation=occupation,
            gender=gender, dead=dead,
            home_building_name=home_building_name, workplace_building_name=workplace_building_name,
            custody=custody, suspect=suspect)

    except ValueError:
        dpg.add_table_column(label='Input Error', parent=query_table)

    except sqlite3.OperationalError:
        dpg.add_table_column(label='Query Error', parent=query_table)

    else:
        for c in inhabitant_columns:
            dpg.add_table_column(label=c, parent=query_table)
        dpg.add_table_column(parent=query_table)

        for r in inhabitant_rows:
            with dpg.table_row(parent=query_table):
                for c in r:
                    dpg.add_text(c)
                dpg.add_button(label='Details', callback=make_inhabitant_clicked(r[0]))


with dpg.window() as game_window:
    with dpg.group(height=0.93 * MAIN_HEIGHT, horizontal=True):
        with dpg.child_window(width=0.4 * MAIN_WIDTH, horizontal_scrollbar=True) as left_view:
            with dpg.group() as map_view:
                dpg.add_text('Map')
                game_map = dpg.add_drawlist(width=3000, height=3000)

        with dpg.child_window() as right_view:
            with dpg.group() as query_view:
                dpg.add_text('Query Result')

                with dpg.group(horizontal=True):
                    dpg.add_text('income_lo: ')
                    income_lo_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('income_hi: ')
                    income_hi_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('occupation: ')
                    occupation_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('gender: ')
                    gender_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('dead: ')
                    dead_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('home_building_name: ')
                    home_building_name_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('workplace_building_name: ')
                    workplace_building_name_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('custody: ')
                    custody_input = dpg.add_input_text()
                with dpg.group(horizontal=True):
                    dpg.add_text('suspect: ')
                    suspect_input = dpg.add_input_text()

                dpg.add_button(label='Search', callback=update_game_window)
                query_table = dpg.add_table(policy=dpg.mvTable_SizingStretchProp)

    with dpg.group(horizontal=True):
        dpg.add_button(label='Save Game', callback=to_save)
        dpg.add_button(label='Quit to Main Menu', callback=to_main)

        dpg.add_spacer()

        dpg.add_button(label='Victim', callback=show_victim)
        dpg.add_button(label='Suspect', callback=show_suspect)

        dpg.add_spacer()

        day_text = dpg.add_text()
        resig_text = dpg.add_text()
        dpg.add_button(label='Next Turn', callback=next_turn)
    dpg.hide_item(game_window)

victim_window = dpg.add_window(label='Victim', width=MAIN_WIDTH / 2, height=MAIN_HEIGHT / 2)
dpg.hide_item(victim_window)
suspect_window = dpg.add_window(label='Suspect', width=MAIN_WIDTH / 2, height=MAIN_HEIGHT / 2)
dpg.hide_item(suspect_window)

with dpg.window(label='You Lose', width=MAIN_WIDTH / 2, height=MAIN_HEIGHT / 2) as lose_window:
    dpg.add_text('You have resigned after failing to catch the killer on time.')
dpg.hide_item(lose_window)

with dpg.window(label='You Win', width=MAIN_WIDTH / 2, height=MAIN_HEIGHT / 2) as win_window:
    dpg.add_text('You have caught the killer.')
dpg.hide_item(win_window)

with dpg.window(label='Wrong Person', width=MAIN_WIDTH / 2, height=MAIN_HEIGHT / 2) as wrong_window:
    dpg.add_text('The person accused is not the killer.')
dpg.hide_item(wrong_window)
