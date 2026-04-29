from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import csv
import os

app = FastAPI()


class User(BaseModel):
    id: int
    username: str
    email: str

class CarBuild(BaseModel):
    id: int
    owner_id: int
    brand: str
    model: str
    year: int
    hp: int

class Modification(BaseModel):
    id: int
    car_id: int
    category: str
    part_name: str
    price: float