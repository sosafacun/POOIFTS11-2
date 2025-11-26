from .base_service import BaseService
from repository.models.client import Client
from utils.rich_ui import RichUI as ui
from utils.global_state import GlobalState

class ClientService(BaseService):

    field_map = [
        ("id", "Client ID"),
        ("name", "First Name"),
        ("last_name", "Last Name"),
        ("dob", "Birthdate (YYYY-MM-DD)"),
        ("phone", "Phone Number")
    ]

    def __init__(self):
        super().__init__("clients", Client)
