import json
import os
from dataclasses import fields

from utils.data_gateway import DataGateway
from repository.models.schedule import Schedule
from repository.models.client import Client
from repository.models.employee import Employee

class GlobalState:
    _initialized = False

    clients = []
    employees = []
    schedule = None

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        gateway = DataGateway()

        cls.clients = gateway.load("clients.csv")
        cls.employees = gateway.load("employees.csv")

        cls.clients = [
            cls.hydrate(Client, row) if isinstance(row, dict) else row
            for row in cls.clients
        ]

        cls.employees = [
            cls.hydrate(Employee, row) if isinstance(row, dict) else row
            for row in cls.employees
        ]

        schedule_path = "./repository/data/schedule.json"
        cls.schedule = {}

        if os.path.exists(schedule_path):
            try:
                with open(schedule_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    cls.schedule = json.loads(content) if content else {}
            except json.JSONDecodeError:
                cls.schedule = {}

        cls._initialized = True

    @classmethod
    def save(cls):
        gateway = DataGateway()

        if cls.clients:
            gateway.save("clients.csv", cls.clients)

        if cls.employees:
            gateway.save("employees.csv", cls.employees)

        schedule_path = "./repository/data/schedule.json"
        temp_path = schedule_path + ".tmp"

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(cls.schedule, f, indent=2)

        os.replace(temp_path, schedule_path)

        
        cls._initialized = False
        cls.initialize()

    @staticmethod
    def hydrate(model, row):
        ordered = {}
        for f in fields(model):
            if f.init and f.name in row:
                ordered[f.name] = row[f.name]
        return model(**ordered)