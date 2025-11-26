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
        ui.show_loading_message("Schedule Menu")

        if not GlobalState.clients:
            ui.warning_message("No clients found. Register one first.")
            ui.pause()
            return

        client = ui.live_search(GlobalState.clients, "Find Client")
        if not client:
            ui.warning_message("Operation cancelled.")
            ui.pause()
            return

        client_id = client.id

        rows = read_filtered(date.today().year)
        target_date = ui.pick_calendar_date(rows)
        if not target_date:
            return

        employee = ui.pick_employee(GlobalState.employees)
        if not employee:
            return

        employee_id = employee.internal_id

        day_data = self.schedule.get_day(target_date)
        slots_for_employee = day_data.get(employee_id, {})

        free_slots = [
            slot for slot, status in slots_for_employee.items()
            if status == "free"
        ]

        if not free_slots:
            ui.warning_message("No available slots for that employee.")
            ui.pause()
            return

        selected_slots = ui.pick_slots(slots_for_employee)
        if not selected_slots:
            return

        try:
            for slot in selected_slots:
                self._reserve(target_date, employee_id, slot, client_id)

            ui.center(
                ui.make_panel(
                    "Appointment Saved",
                    f"{client_id} → {target_date} {slot} | {employee}"
                )
            )
        except Exception as e:
            ui.throw_exception("Error creating appointment", e)

        ui.pause()

    def read(self):
        groups = self._day_to_dict(self.today, False)

        if not groups:
            ui.show_message(f"No booked appointments for {self.today}")
            ui.pause()
            return

        ui.paginate_sectioned(groups)

    def update(self):
        pass

    def delete(self):
        pass

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

    def _reserve(self, target_date, employee_id, slot, value):
        sched = self.schedule

        sched.ensure_day(target_date)

        if not sched.is_slot_free(target_date, employee_id, slot):
            raise ValueError("Slot unavailable.")

        sched.set_slot(target_date, employee_id, slot, value)

        GlobalState.schedule = sched.data
        GlobalState.save()

    def _day_to_dict(self, target_date, filter_free):
        day = GlobalState.schedule.get(target_date.isoformat(), {})
        result = {}

        for emp_id, slots in day.items():
            employee = next((e for e in GlobalState.employees if e.internal_id == emp_id), None)
            if not employee:
                continue

            entry_list = []
            for time_slot, client_id in slots.items():

                if filter_free and client_id == "free":
                    continue

                if client_id == "free":
                    entry_list.append(f"{time_slot} → (free)")
                else:
                    client = next((c for c in GlobalState.clients if c.id == client_id), None)
                    name = f"{client.last_name}, {client.name}" if client else "UNKNOWN"
                    entry_list.append(f"{time_slot} → {name} ({client_id})")

            if entry_list:
                header = f"{employee.last_name}, {employee.name} ({emp_id})"
                result[header] = entry_list

        return result