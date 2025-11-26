import csv
import os
from typing import List, Union
from dataclasses import fields, is_dataclass

class DataGateway:

    def __init__(self, base_path="./repository/data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def load(self, filename: str):
        path = os.path.join(self.base_path, filename)

        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def save(self, filename, items):
        cleaned = []

        for obj in items:
            if is_dataclass(obj):
                allowed = {f.name for f in fields(obj) if f.init}
                row = {k: getattr(obj, k) for k in allowed}
            else:
                row = obj

            cleaned.append(row)
        
        path = f"./repository/data/{filename}"
        with open(path, "w", encoding="utf-8", newline="") as f:
            field_order = [f.name for f in fields(obj.__class__) if f.init]
            writer = csv.DictWriter(f, fieldnames=field_order)
            writer.writeheader()
            writer.writerows(cleaned)
