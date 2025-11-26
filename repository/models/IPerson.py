from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

#omg, i didn't know dataclasses were a thing. They are so fucking goated to work with.
@dataclass
class IPerson(ABC):
    id: str
    name: str
    last_name: str
    dob: str
    phone: str

    #this makes a dataclass field nnot required for a constructor.
    age: int = field(init=False, repr=False)
    is_bday_gift_active: bool = field(init=False, repr=False)
    prefix: str = field(init=False, default="")
    internal_id: str = field(init=False)

    def __post_init__(self):
        self.age = self._get_age()
        self.is_bday_gift_active = self._set_bday_gift()  
        self.internal_id = self.prefix + self.id

    def _get_age(self):
        birthdate = datetime.strptime(self.dob, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birthdate.year -((today.month, today.day) < (birthdate.month, birthdate.day)) #stackoverflow
    
    def _set_bday_gift(self): 
        today = datetime.today().date() 
        birthdate = datetime.strptime(self.dob, "%Y-%m-%d").date() 
        birthday_this_year = birthdate.replace(year=today.year) 
        end_window = birthday_this_year.replace(year=today.year) + timedelta(days=13) 

        return birthday_this_year <= today <= end_window
    
    def card_header(self):
        return (f"{self.name} {self.last_name}", f"{self.internal_id}") 

    def card_body(self):
        return [
            ("Phone", self.phone),
            ("Age", f"{self.age} [dim]({self.dob})[/dim]"),
            ("Birthday Gift", "Active" if self.is_bday_gift_active else "Inactive")
        ]
    
    @abstractmethod
    def card_color(self):
        pass
