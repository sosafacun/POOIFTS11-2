from datetime import date
from repository.models.schedule import Schedule
from utils.rich_ui import RichUI as ui
from utils.year_builder import read_filtered
from utils.global_state import GlobalState


class ScheduleService:
    def __init__(self, employees, slots):
        self.employees = employees
        self.slots = slots
        self.today = date.today()

    @property
    def schedule(self):
        if GlobalState.schedule is None:
            GlobalState.schedule = {}

        sched = Schedule(self.employees, self.slots)
        sched.data = GlobalState.schedule
        return sched

    def create(self):
        if not GlobalState.clients:
            ui.warning_message("No clients found. Register one first.")
            ui.pause()
            return

        client = ui.live_search(GlobalState.clients, "Find Client")
        if not client:
            return

        target_day = self._pick_day()
        if not target_day:
            return

        employee = ui.pick_employee(GlobalState.employees)
        if not employee:
            return

        slots = self._select_slots(target_day, mode="create")[0]
        if not slots:
            ui.warning_message("No free slots for this employee.")
            ui.pause()
            return

        flat = [(employee.internal_id, s, None) for s in slots]
        indices = range(len(flat))
        self._apply_changes(target_day, flat, indices, client.id)

        ui.show_message(f"Saved {len(slots)} appointment(s).")

    def read(self):
        groups = self._day_to_dict(self.today)

        if not groups:
            ui.show_message(f"No booked appointments for {self.today}")
            ui.pause()
            return

        ui.paginate_sectioned(groups)

    def update(self):
        target_day, data, error = self._get_day_and_slots(mode="update")
        if error:
            ui.warning_message(error); ui.pause(); return

        flat, _ = data

        new_client = ui.live_search(GlobalState.clients, "Assign client")
        if not new_client:
            return

        self._apply_changes(target_day, flat, range(len(flat)), new_client.id)
        ui.show_message(f"Updated {len(flat)} appointment(s).")

    def delete(self):
        target_day, data, error = self._get_day_and_slots(mode="delete")
        if error:
            ui.warning_message(error); ui.pause(); return

        flat, _ = data

        if not ui.confirm_action(f"Delete {len(flat)} appointment(s)?", ""):
            return

        self._apply_changes(target_day, flat, range(len(flat)), "free")
        ui.show_message(f"Deleted {len(flat)} appointment(s).")

    def search(self):
        pass

    def get_day(self, day: date):
        return self.schedule.get_day(day)

    def apply_changes(self, before, after):
        schedule = GlobalState.schedule

        old_client_id = getattr(before, "id", None) if before else None
        new_client_id = getattr(after, "id", None) if after else None

        old_employee_id = getattr(before, "internal_id", None) if before else None
        new_employee_id = getattr(after, "internal_id", None) if after else None

        #deletions
        if before and not after:
            
            #on employee delete, remove all their schedules
            if old_employee_id:
                for day in list(schedule.keys()):
                    if day < self.today:
                        continue
                    schedule[day].pop(old_employee_id, None)
                return

            #on employee delete, remove all their schedules from the employees
            if old_client_id:
                for day, employees in schedule.items():
                    if day < self.today:
                        continue
                    for emp, slots in employees.items():
                        for slot, value in slots.items():
                            if value == old_client_id:
                                slots[slot] = "free"
                return
        
        #on employee id change, move their schedules to the new id
        if old_employee_id and new_employee_id and old_employee_id != new_employee_id:
            for day, employees in schedule.items():
                if old_employee_id in employees:
                    employees[new_employee_id] = employees.pop(old_employee_id)

        #on client id change, move their schedules to the new id
        if old_client_id and new_client_id and old_client_id != new_client_id:
            for day, employees in schedule.items():
                for emp, slots in employees.items():
                    for slot, value in slots.items():
                        if value == old_client_id:
                            slots[slot] = new_client_id

    def _day_to_dict(self, target_day):
        day = GlobalState.schedule.get(target_day.isoformat(), {})
        result = {}

        for emp_id, slots in day.items():
            employee = next((e for e in GlobalState.employees if e.internal_id == emp_id), None)
            if not employee:
                continue

            entry_list = []
            for time_slot, client_id in slots.items():

                if client_id == "free":
                    entry_list.append(f"{time_slot} → (free)")
                else:
                    client = next((c for c in GlobalState.clients if c.id == client_id), None)
                    name = f"{client.last_name}, {client.name}" if client else "UNKNOWN"
                    entry_list.append(f"{time_slot} → {name} ({client_id})")

            header = f"{employee.last_name}, {employee.name} ({emp_id})"
            result[header] = entry_list

        return result

    def _pick_day(self):
        rows = read_filtered(date.today().year)
        if not rows:
            return None

        ui._show_calendar(rows)
        valid = {str(i+1): r["date"] for i, r in enumerate(rows)}
        choice = ui._option_select(list(valid.keys()), "1")

        return date.fromisoformat(valid[choice])

    def _pick_client(self):
        return ui.live_search(GlobalState.clients, "Select new client")

    def _select_slots(self, target_day, mode="update"):
        groups = self._day_to_dict(target_day)
        if not groups:
            return None, None

        merged = {}
        for header, items in groups.items():
            emp_id = header.split("(")[-1].strip(")")
            for line in items:
                slot = line.split("→")[0].strip()
                merged[f"{emp_id}|{slot}"] = line

        slot_state = {}

        for key, line in merged.items():
            is_free = "(free)" in line

            if mode == "create":
                slot_state[key] = "free" if is_free else "taken"
            else:
                slot_state[key] = "free"

        selected_keys = ui.pick_slots(slot_state)
        if not selected_keys:
            return None, None

        flat = []
        for key in selected_keys:
            emp_id, slot = key.split("|")
            flat.append((emp_id, slot, merged[key]))

        return flat, list(range(len(flat)))

    def _get_day_and_slots(self, mode="update"):
        target_day = self._pick_day()
        if not target_day:
            return None, None, "No schedules available."

        flat, selected = self._select_slots(target_day, mode)
        if not flat:
            return None, None, "Nothing found for that day."

        return target_day, (flat, selected), None

    def _apply_changes(self, target_day, flat, indices, value):
        sched = self.schedule
        for i in indices:
            emp_id, slot, _ = flat[i]
            sched.set_slot(target_day, emp_id, slot, value)

        GlobalState.schedule = sched.data
        GlobalState.save()

    def _pick_free_slots(self, target_day, employee_id):
        day = self.schedule.get_day(target_day)
        slots = day.get(employee_id, {})

        free = [slot for slot, val in slots.items() if val == "free"]
        if not free:
            return None

        selected = ui.pick_slots(slots)
        return selected