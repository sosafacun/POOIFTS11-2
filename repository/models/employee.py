from dataclasses import dataclass, field
from repository.models.IPerson import IPerson

@dataclass
class Employee(IPerson):
    prefix: str = field(init=False, default="02-")

    def card_color(self):
        return "cyan"