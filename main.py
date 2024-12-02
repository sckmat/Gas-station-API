from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List
from enum import Enum
from datetime import date

app = FastAPI()


class FuelType(str, Enum):
    ai92 = "АИ92"
    ai95 = "АИ95"
    ai98 = "АИ98"
    diesel = "ДТ"


tanks = []


class Tank(BaseModel):
    id: int
    fuel_type: FuelType
    capacity: float
    current_volume: float
    last_refill_date: date

    @field_validator("current_volume")
    def validate_current_volume(cls, value, info):
        capacity = info.data.get("capacity")
        if capacity is not None and value > capacity:
            raise ValueError(f"Current volume ({value}) cannot exceed capacity ({capacity})")
        return value

    @field_validator("last_refill_date")
    def validate_last_refill_date(cls, value):
        if value > date.today():
            raise ValueError("Last refill date cannot be in the future")
        return value


@app.post("/tanks/", response_model=Tank)
def create_tank(tank: Tank):
    if any(existing_tank.id == tank.id for existing_tank in tanks):
        raise HTTPException(status_code=400, detail=f"Tank with ID {tank.id} already exists")
    tanks.append(tank)
    return tank


@app.get("/tanks/", response_model=List[Tank])
def read_tanks():
    return tanks


@app.get("/tanks/{tank_id}", response_model=Tank)
def read_tank(tank_id: int):
    for tank in tanks:
        if tank.id == tank_id:
            return tank
    raise HTTPException(status_code=404, detail="Tank not found")


@app.put("/tanks/{tank_id}", response_model=Tank)
def update_tank(tank_id: int, updated_tank: Tank):
    for i, tank in enumerate(tanks):
        if tank.id == tank_id:
            if any(existing_tank.id == updated_tank.id and existing_tank.id != tank_id for existing_tank in tanks):
                raise HTTPException(status_code=400, detail=f"Tank with ID {updated_tank.id} already exists")
            tanks[i] = updated_tank
            return updated_tank
    raise HTTPException(status_code=404, detail="Tank not found")


@app.delete("/tanks/{tank_id}")
def delete_tank(tank_id: int):
    for i, tank in enumerate(tanks):
        if tank.id == tank_id:
            del tanks[i]
            return {"message": "Tank deleted"}
    raise HTTPException(status_code=404, detail="Tank not found")
