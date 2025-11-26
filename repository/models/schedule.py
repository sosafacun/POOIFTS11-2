from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import Dict, List

@dataclass
class Schedule:
    employees: List[str]
    slots: List[str]
    data: Dict[str, Dict[str, Dict[str, str]]] = field(default_factory=dict)
    
    def ensure_day(self, target_date: date):
        d = target_date.isoformat()

        if d not in self.data:
            self.data[d] = {
                employee: {slot: "free" for slot in self.slots}
                for employee in self.employees
            }

    def get_day(self, target_date: date):
        self.ensure_day(target_date)
        return self.data[target_date.isoformat()]

    def get_employee_slots(self, target_date: date, employee: str):
        return self.get_day(target_date)[employee]

    def is_slot_free(self, target_date: date, employee: str, slot: str):
        return self.get_day(target_date)[employee][slot] == "free"

    def set_slot(self, target_date: date, employee: str, slot: str, value: str):
        self.get_day(target_date)[employee][slot] = value

    def __contains__(self, target_date: date):
        return target_date.isoformat() in self.data