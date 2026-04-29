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

##____________"crud user"_______________________


@app.post("/users/")
def create_user(user: User):
    users = read_csv("users.csv")
    users.append(user.dict())
    write_csv("users.csv", users, user.dict().keys())
    return user

@app.get("/users/")
def get_users():
    return read_csv("users.csv")

@app.get("/users/{user_id}")
def get_user(user_id: int):
    users = read_csv("users.csv")
    for u in users:
        if int(u["id"]) == user_id:
            return u
    raise HTTPException(404, "User not found")

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    users = read_csv("users.csv")
    new_users = [u for u in users if int(u["id"]) != user_id]
    write_csv("users.csv", new_users, ["id", "username", "email"])
    return {"msg": "User deleted"}