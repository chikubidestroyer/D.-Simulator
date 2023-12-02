"""The main entry point of the program."""

import sys
import os
import dearpygui.dearpygui as dpg
from dsimulator.defs import MAIN_WIDTH, MAIN_HEIGHT, RES_DIR

# For handling segfaults such as those coming from DearPyGui.
import faulthandler
faulthandler.enable()


def main() -> int:
    """Initialize DearPyGui, load GUI fonts, invoke the main window, and handle cleanup."""
    dpg.create_context()

    with dpg.font_registry():
        default_font = dpg.add_font(os.path.join(
            RES_DIR, 'VenrynSans-Regular.ttf'), 42)
    dpg.bind_font(default_font)

    # Callback is managed manually in the rendering loop,
    # where they run on the same thread as the rendering thread.
    # This is to prevent mult-threading issues that may arise when,
    # for example, when a button that deletes itself was clicked many times.
    # This button could call the callback function when being clicked
    # while simultaneously being deleted.
    #
    # Segfaults have happened before with this turned off!
    dpg.configure_app(manual_callback_management=True)

    dpg.create_viewport(title='D. Simulator', width=MAIN_WIDTH,
                        height=MAIN_HEIGHT, resizable=False, decorated=False)

    from dsimulator.ui.main import main_window
    dpg.show_item(main_window)
    dpg.set_primary_window(main_window, True)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        jobs = dpg.get_callback_queue()
        dpg.run_callbacks(jobs)
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

    return 0


sys.exit(main())
