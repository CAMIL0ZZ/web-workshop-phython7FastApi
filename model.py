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


##___________"manipulacion csv"_________________

def read_csv(file):
    if not os.path.exists(file):
        return []
    with open(file, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(file, data, fieldnames):
    with open(file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)