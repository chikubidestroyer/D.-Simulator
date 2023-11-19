import dearpygui.dearpygui as dpg
import dsimulator.ui.load as load

def to_load():
    dpg.hide_item(main_window)
    dpg.show_item(load.load_window)
    dpg.set_primary_window(load.load_window, True)

with dpg.window() as main_window:
    dpg.add_text('main window')
    dpg.add_button(label='load', callback=to_load)
    dpg.hide_item(main_window)
