from pydantic import BaseModel, Field, validator
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

    @validator('time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(f'Format error: {v}')

    @validator('peopleAtStop', 'entered', 'exited')
    def validate_numbers(cls, v):
        if not v.isdigit():
            raise ValueError(f'Not a number: {v}')
        return v
