from dataclasses import dataclass
from enum import Enum
from typing import Any


class enum_type(str, Enum):
    teacher: str = "Teacher"
    assistant: str = "Assistant"


@dataclass
class Teacher:
    id: int
    name: str
    school: str
    entity_type: enum_type
    salary: int
    classes: list[str]

    def __post_init__(self):
        if self.entity_type not in list(enum_type):
            print(self.entity_type)
            raise ValueError(
                f"entity_type {self.entity_type} not a valid value, please use teacher or student"
            )


teacher1 = Teacher(
    id=1,
    name="Jane Smith",
    school="Eastvail High",
    entity_type="teacher",
    salary=85000,
    classes=["Math", "Science"],
)

# inheritance
@dataclass
class Student(Teacher):
    classes_taking: list[str]
