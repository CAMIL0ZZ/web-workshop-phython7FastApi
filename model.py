from pydantic import BaseModel, Field
from typing import List, Optional


class User(BaseModel):
    id: int = Field(..., example=1)
    username: str = Field(..., min_length=3, max_length=20, example="tuner123")
    email: str = Field(..., example="user@email.com")



class Car(BaseModel):
    id: int = Field(..., example=1)
    brand: str = Field(..., example="Toyota")
    model: str = Field(..., example="Supra")
    year: int = Field(..., ge=1900, le=2026, example=2020)
    base_hp: float = Field(..., gt=0, example=200.0)
    owner_id: int = Field(..., example=1)



class Modification(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Turbo Kit")
    hp_gain: float = Field(..., gt=0, example=50.0)



class CarModification(BaseModel):
    id: int = Field(..., example=1)
    car_id: int = Field(..., example=1)
    modification_id: int = Field(..., example=1)



class CarWithHP(BaseModel):
    car_id: int
    estimated_hp: float


class ComparisonResult(BaseModel):
    car1_hp: float
    car2_hp: float
    winner: str