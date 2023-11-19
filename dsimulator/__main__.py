import sys
import os
import dearpygui.dearpygui as dpg
from dsimulator.defs import RES_DIR

def main():
    dpg.create_context()
    # dpg.show_style_editor()
    dpg.create_viewport(title='D. Simulator', width=640, height=480)

    with dpg.font_registry():
        default_font = dpg.add_font(os.path.join(RES_DIR, 'VenrynSans-Regular.ttf'), 64)
    dpg.bind_font(default_font)

    from dsimulator.ui.main import main_window
    dpg.show_item(main_window)
    dpg.set_primary_window(main_window, True)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    return 0

sys.exit(main())
