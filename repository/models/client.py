from dataclasses import dataclass, field
from repository.models.IPerson import IPerson

@dataclass
class Client(IPerson):
    prefix: str = field(init=False, default="01-")

    def card_color(self):
        return "bright_green"