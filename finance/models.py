from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Category:
    id: int
    name: str
    type: str 

@dataclass
class Transaction:
    id: int
    date: date
    description: Optional[str]
    amount: float
    category_id: int
    type: str

@dataclass
class Budget:
    id: int
    category_id: int
    monthly_limit: float
