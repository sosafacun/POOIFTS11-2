from utils.rich_ui import RichUI as ui
from datetime import datetime
from utils.year_builder import ensure_year_file, read_filtered


def main():

    #init or read year file.
    current_year = datetime.now().year
    ensure_year_file(current_year)

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
            controller.run_menu(build_crud_menu(controller))

if __name__ == "__main__":
    main()