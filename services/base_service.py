from abc import ABC, abstractmethod
from utils.rich_ui import RichUI as ui
from utils.global_state import GlobalState
from dataclasses import fields

class BaseService(ABC):

    def __init__(self, state_key, model_class):
        GlobalState.initialize()

        self.state_key = state_key
        self.model_class = model_class

        self.items = getattr(GlobalState, state_key)

    def create(self):
        try:
            data = {}

            for key, label in self.field_map:
                while True:
                    value = ui.prompt_user(f"{label} (or type 'exit' to cancel)")

                    if value.lower() == "exit":
                        ui.warning_message("Creation cancelled.")
                        return None

                    error = self._validate_field(key, value)
                    if error:
                        ui.warning_message(error)
                        ui.pause()
                        continue

                    data[key] = value
                    break

            obj = self.model_class(**data)
            self.items.append(obj)

            confirmed = ui.confirm_action(
                f"Register new {self.model_class.__name__}?",
                "\n".join(f"{label}: {data[key]}" for key, label in self.field_map)
            )

            if not confirmed:
                ui.warning_message("Operation cancelled.")
                return None

            try:
                self._save()
                self._propagate_changes(None, obj)
                ui.show_message("Changes saved successfully!.")
            except Exception as e:
                ui.throw_exception("Error saving", e)

            return obj
        except KeyError as e:
            ui.throw_exception("create() requires field_map on subclass", e)

    def read(self):
        if not self.items:
            self._no_items_found()
            return
        else:
            ui.show_paginated_cards(self.items)

    def update(self):
        if not self.items:
            self._no_items_found()
            return

        target = ui.live_search(self.items, f"Select {self.model_class.__name__} to update")

        if not target:
            ui.warning_message("Operation cancelled.")
            ui.pause()
            return

        before_data = {
            f.name: getattr(target, f.name)
            for f in fields(self.model_class)
            if f.init
        }
        before = self.model_class(**before_data)

        updates = ui.edit_object(target, self.field_map)

        if not ui.confirm_action(f"Apply changes to {self.model_class.__name__}?", updates):
            ui.warning_message("Operation cancelled.")
            return

        for field, value in updates.items():
            setattr(target, field, value)

        if hasattr(target, "internal_id"):
            target.internal_id = f"{target.prefix}{target.id}"

        for idx, item in enumerate(self.items):
            if item is target:
                self.items[idx] = target
                break
                
        try:
            self._propagate_changes(before, target)
            self._save()
            ui.show_message("Changes saved successfully!.")
        except Exception as e:
                ui.throw_exception("Error saving", e)

    def delete(self):
        target = self._live_search()
        if not target:
            return

        identifier = getattr(target, "internal_id", None) or getattr(target, "id", None)

        if not ui.confirm_action(
            f"Delete {self.model_class.__name__}?",
            f"{identifier}"
        ):
            ui.warning_message("Delete cancelled.")
            ui.pause()
            return
        #44885577,test,test,1997-07-06,1155442200
        #64011833,Veronica,Salas,1997-03-28,1165904410
        try:
            self.items.remove(target)
            self._propagate_changes(target, None)
            self._save()
            ui.show_message("Changes saved successfully!.")
        except ValueError:
            ui.throw_exception("Delete failed", f"{target}")

    def search(self):
        if not self.items:
            self._no_items_found()
            return

        result = self._live_search()

        ui.show_cards_static([result])
        ui.pause()
   
    def _validate_field(self, field, value):
        if field == "id":
            if not value.isdigit() or len(value) != 8:
                return "ID must be exactly 8 digits."
            
            # uniqueness check
            if any(str(item.id) == value for item in self.items):
                return "Someone with this ID already exists."

        if field in ("name", "last_name"):
            allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-' ")
            if not all(ch in allowed for ch in value):
                return "Names may only contain letters, spaces, apostrophes ('), and hyphens (-)."

        if field == "phone":
            if not value.isdigit() or len(value) != 10:
                return "Phone number must be a 10-digit number."

            if any(str(item.phone) == value for item in self.items):
                return "This phone number is already registered."

        if field == "dob":
            from datetime import datetime
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return "Date must be formatted YYYY-MM-DD."

        return None
    
    def _propagate_changes(self, before, after):
        schedule_service = getattr(GlobalState, "schedule_service", None)
        if not schedule_service:
            return
        schedule_service.apply_changes(before=before, after=after)

    def _live_search(self):
        if not self.items:
            ui.warning_message(f"No {self.model_class.__name__.lower()}s found.")
            ui.pause()
            return None

        result = ui.live_search(self.items, f"Search {self.model_class.__name__}")

        if not result:
            ui.warning_message("No match found or cancelled.")
            ui.pause()
            return None

        return result

    def _save(self):
        GlobalState.save()
        self.items = getattr(GlobalState, self.state_key)
    
    def _no_items_found(self):
        ui.warning_message(f"No {self.model_class.__name__.lower()}s found.")
        ui.pause()
        return