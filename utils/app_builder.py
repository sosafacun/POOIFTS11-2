from utils.rich_ui import RichUI as ui
from utils.global_state import GlobalState

from datetime import datetime

from utils.year_builder import ensure_year_file
from services.client_service import ClientService
from services.employee_service import EmployeeService
from services.schedule_service import ScheduleService

from controllers.CRUD_controller import CRUDController


class AppBuilder:
    def __init__(self):
        self._controllers = {}

    def build(self):
        client_service = ClientService()
        employee_service = EmployeeService()

        
        SLOTS = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30"
        ]

        schedule_service = ScheduleService(
            employees=[e.internal_id for e in employee_service.items],
            slots=SLOTS
        )

        GlobalState.schedule_service = schedule_service

        self._controllers = {
            "1": CRUDController("Clients", client_service, ui),
            "2": CRUDController("Employees", employee_service, ui),
            "3": CRUDController("Schedule", schedule_service, ui),
        }

        return self._controllers

    def get_controllers(self):
        return self._controllers
