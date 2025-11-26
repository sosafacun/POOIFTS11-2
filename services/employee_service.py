from .base_service import BaseService
from repository.models.employee import Employee
from utils.rich_ui import RichUI as ui
from utils.global_state import GlobalState

class EmployeeService(BaseService):

    field_map = [
        ("id", "Employee ID"),
        ("name", "First Name"),
        ("last_name", "Last Name"),
        ("dob", "Birthdate (YYYY-MM-DD)"),
        ("phone", "Phone Number")
    ]

    def __init__(self):
        super().__init__("employees", Employee)
