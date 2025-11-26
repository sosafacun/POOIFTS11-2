from datetime import datetime

#my libs
from utils.rich_ui import RichUI as ui
from utils.year_builder import ensure_year_file
from utils.global_state import GlobalState
from utils.app_builder import AppBuilder

def main():
    ensure_year_file(datetime.now().year)

    # initialize all CSV + schedule memory
    GlobalState.initialize()

    controllers = AppBuilder().build()

    while True:
        choice = ui.simple_menu(
            "Final OOP Project     |\t\t       IFTS N°11",
            "Student: Facundo Sosa | Professor: Emiliano Billi",
            [
                ("1","Client Menu"),
                ("2","Employee Menu"),
                ("3","Schedule Menu"),
                ("Q","Exit Program")
            ]
        )

        if choice == "Q":
            ui.show_loading_message(". . .")
            break

        controller = controllers.get(choice)
        if controller:
            controller.run_menu(controller.crud_menu())


if __name__ == "__main__":
    main()
