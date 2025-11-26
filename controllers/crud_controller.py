from utils.rich_ui import RichUI as ui

class CRUDController():
    #to create a controller you need the name (used for the ui), a service (used to control what each handler does)
    #and the ui to avoid from utils.rich_ui import RichUI as ui
    def __init__(self, name, service, ui):
        self.name = name
        self.service = service
        self.ui = ui

    def crud_menu(self):
        return [
            ("1", f"Register new {self.name}"),
            ("2", f"View all {self.name}"),
            ("3", f"Update existing {self.name}"),
            ("4", f"Delete existing {self.name}"),
            ("5", f"Search for {self.name}"),
            ("Q", "Go back to the main menu")
        ]

    #run_menu is just RichUI's simple_menu on steroids. It launches the menu creation.    
    def run_menu(self, menu_items):
        while True:
            choice = self.ui.simple_menu(self.name, "CRUD + Search", menu_items)
            if choice == "Q":
                return
            self.handle(choice)

    #handler for each choice.
    def handle(self, choice):
        actions = {
            "1": self.service.create,
            "2": self.service.read,
            "3": self.service.update,
            "4": self.service.delete,
            "5": self.service.search
        }
        action = actions.get(choice)
        
        try:
            if action:
                action()
        except Exception as e:
            ui.throw_exception("Exception", e)
            