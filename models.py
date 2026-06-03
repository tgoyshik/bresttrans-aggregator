from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class BusRecordModel(BaseModel):
    time: str
    currentStop: str = Field(..., min_length=2)
    nextStop: str = Field(..., min_length=2)
    peopleAtStop: str
    entered: str
    exited: str
    latitude: str
    longitude: str
    weather: str
    student: Optional[str] = None

    @field_validator('time')
    @classmethod
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(f'Format error: {v}')

    @field_validator('peopleAtStop', 'entered', 'exited')
    @classmethod
    def validate_numbers(cls, v):
        if not v.isdigit():
            raise ValueError(f'Not a number: {v}')
        return v
