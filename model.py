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

##_____________"crud bulds"_________________


@app.post("/builds/")
def create_build(build: CarBuild):
    builds = read_csv("builds.csv")
    builds.append(build.dict())
    write_csv("builds.csv", builds, build.dict().keys())
    return build

@app.get("/builds/")
def get_builds():
    return read_csv("builds.csv")

@app.get("/builds/{build_id}")
def get_build(build_id: int):
    builds = read_csv("builds.csv")
    for b in builds:
        if int(b["id"]) == build_id:
            return b
    raise HTTPException(404, "Build not found")

@app.delete("/builds/{build_id}")
def delete_build(build_id: int):
    builds = read_csv("builds.csv")
    new_builds = [b for b in builds if int(b["id"]) != build_id]
    write_csv("builds.csv", new_builds, ["id", "owner_id", "brand", "model", "year", "hp"])
    return {"msg": "Build deleted"}


