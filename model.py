import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_load_env

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Falta la variable de entorno DATABASE_URL")

# Configuración de SQLAlchemy para Neon (PostgreSQL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="Car Builds API con Neon DB")

# -------------------------------------------------------------
# MODELOS DE BASE DE DATOS (SQLAlchemy)
# -------------------------------------------------------------

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

class CarBuildModel(Base):
    __tablename__ = "car_builds"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    brand = Column(String, index=True, nullable=False)
    model = Column(String, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)

class ModificationModel(Base):
    __tablename__ = "modifications"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey("car_builds.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, index=True, nullable=False)
    part_name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)

# Crear las tablas en Neon si no existen
Base.metadata.create_all(bind=engine)

# -------------------------------------------------------------
# ESQUEMAS DE VALIDACIÓN (Pydantic)
# -------------------------------------------------------------
# Nota: Quitamos el 'id' en la creación (Create) porque Neon lo auto-incrementa.

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class CarBuildCreate(BaseModel):
    owner_id: int
    brand: str
    model: str
    year: int
    hp: int

class CarBuildResponse(BaseModel):
    id: int
    owner_id: int
    brand: str
    model: str
    year: int
    hp: int
    class Config:
        from_attributes = True

class ModificationCreate(BaseModel):
    car_id: int
    category: str
    part_name: str
    price: float

class ModificationResponse(BaseModel):
    id: int
    car_id: int
    category: str
    part_name: str
    price: float
    class Config:
        from_attributes = True

# -------------------------------------------------------------
# DEPENDENCIA PARA LA CONEXIÓN A LA DB
# -------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------
# CRUD: USERS
# -------------------------------------------------------------

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserModel(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

@app.get("/users/search/", response_model=List[UserResponse])
def search_users(username: Optional[str] = None, email: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(UserModel)
    if username:
        query = query.filter(UserModel.username.ilike(f"%{username}%"))
    if email:
        query = query.filter(UserModel.email.ilike(f"%{email}%"))
    return query.all()

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"msg": "User deleted"}

# -------------------------------------------------------------
# CRUD: CAR BUILDS
# -------------------------------------------------------------

@app.post("/builds/", response_model=CarBuildResponse)
def create_build(build: CarBuildCreate, db: Session = Depends(get_db)):
    # Opcional: Validar si el owner_id existe
    owner_exists = db.query(UserModel).filter(UserModel.id == build.owner_id).first()
    if not owner_exists:
        raise HTTPException(status_code=400, detail="Owner ID does not exist")
        
    db_build = CarBuildModel(**build.dict())
    db.add(db_build)
    db.commit()
    db.refresh(db_build)
    return db_build

@app.get("/builds/", response_model=List[CarBuildResponse])
def get_builds(db: Session = Depends(get_db)):
    return db.query(CarBuildModel).all()

@app.get("/builds/search/", response_model=List[CarBuildResponse])
def search_builds(brand: Optional[str] = None, model: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CarBuildModel)
    if brand:
        query = query.filter(CarBuildModel.brand.ilike(f"%{brand}%"))
    if model:
        query = query.filter(CarBuildModel.model.ilike(f"%{model}%"))
    return query.all()

@app.get("/builds/{build_id}", response_model=CarBuildResponse)
def get_build(build_id: int, db: Session = Depends(get_db)):
    build = db.query(CarBuildModel).filter(CarBuildModel.id == build_id).first()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build

@app.delete("/builds/{build_id}")
def delete_build(build_id: int, db: Session = Depends(get_db)):
    build = db.query(CarBuildModel).filter(CarBuildModel.id == build_id).first()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    db.delete(build)
    db.commit()
    return {"msg": "Build deleted"}

# -------------------------------------------------------------
# CRUD: MODIFICATIONS
# -------------------------------------------------------------

@app.post("/mods/", response_model=ModificationResponse)
def create_mod(mod: ModificationCreate, db: Session = Depends(get_db)):
    # Opcional: Validar si el car_id existe
    car_exists = db.query(CarBuildModel).filter(CarBuildModel.id == mod.car_id).first()
    if not car_exists:
        raise HTTPException(status_code=400, detail="Car Build ID does not exist")

    db_mod = ModificationModel(**mod.dict())
    db.add(db_mod)
    db.commit()
    db.refresh(db_mod)
    return db_mod

@app.get("/mods/", response_model=List[ModificationResponse])
def get_mods(db: Session = Depends(get_db)):
    return db.query(ModificationModel).all()

@app.get("/mods/search/", response_model=List[ModificationResponse])
def search_mods(category: Optional[str] = None, part_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ModificationModel)
    if category:
        query = query.filter(ModificationModel.category.ilike(f"%{category}%"))
    if part_name:
        query = query.filter(ModificationModel.part_name.ilike(f"%{part_name}%"))
    return query.all()

@app.get("/mods/{mod_id}", response_model=ModificationResponse)
def get_mod(mod_id: int, db: Session = Depends(get_db)):
    mod = db.query(ModificationModel).filter(ModificationModel.id == mod_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Mod not found")
    return mod

@app.delete("/mods/{mod_id}")
def delete_mod(mod_id: int, db: Session = Depends(get_db)):
    mod = db.query(ModificationModel).filter(ModificationModel.id == mod_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Mod not found")
    db.delete(mod)
    db.commit()
    return {"msg": "Mod deleted"}