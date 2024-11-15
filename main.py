from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import uvicorn

app = FastAPI()

class PowerPlant(BaseModel):
    name: str
    type: str
    efficiency: float
    pmax: float
    pmin: float

class Fuel(BaseModel):
    gas: float = Field(alias='gas(euro/MWh)')
    kerosine: float = Field(alias='kerosine(euro/MWh)')
    co2: float = Field(alias='co2(euro/ton)')
    wind: float = Field(alias='wind(%)')

class ProductionPlanInput(BaseModel):
    load: float
    fuels: Fuel
    powerplants: List[PowerPlant]

class PowerPlantOutput(BaseModel):
    name: str
    p: float

def calculate_cost(plant: PowerPlant, fuels: Fuel) -> float:
    if plant.type == "windturbine":
        return 0
    elif plant.type == "gasfired":
        return (fuels.gas / plant.efficiency)
    elif plant.type == "turbojet":
        return (fuels.kerosine / plant.efficiency)

def calculate_production_plan(request: ProductionPlanInput) -> List[PowerPlantOutput]:
    """Calculate the optimal production plan based on merit order."""
    # Calculate available wind power
    windparks = [p for p in request.powerplants if p.type == "windturbine"]
    remaining_load = request.load
    result = []
    
    # First calculate wind power because it's free
    if request.fuels.wind > 0:
        for plant in windparks:
            power = min(plant.pmax * request.fuels.wind / 100, remaining_load)
            power = round(power, 1)
            if power > 0:
                result.append(PowerPlantOutput(name=plant.name, p=power))
                remaining_load -= power

    # Sort other plants by cost
    other_plants = [p for p in request.powerplants if p.type != "windturbine"]
    plants_with_cost = [(p, calculate_cost(p, request.fuels)) for p in other_plants]
    plants_with_cost.sort(key=lambda x: x[1])

    # Allocate remaining load to other plants based on merit order
    for plant, _ in plants_with_cost:
        if remaining_load <= 0:
            result.append(PowerPlantOutput(name=plant.name, p=0))
            continue
        if plant.pmin <= remaining_load <= plant.pmax:
            power = remaining_load
        elif remaining_load > plant.pmax:
            power = plant.pmax
        else:
            result.append(PowerPlantOutput(name=plant.name, p=0))
            continue
        
        power = round(power, 1)
        result.append(PowerPlantOutput(name=plant.name, p=power))
        remaining_load -= power

    # Check the load if it matches the input. There can be a small difference due to rounding
    total_power = sum(output.p for output in result)
    if abs(total_power - request.load) > 0.1:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to match load exactly. Total output: {total_power}, Required load: {request.load}"
        )

    # Sort result to match the original order of plants in input
    name_to_output = {output.name: output for output in result}
    sorted_result = [name_to_output[plant.name] for plant in request.powerplants]
    
    return sorted_result

@app.post("/productionplan")
async def production_plan(request: ProductionPlanInput) -> List[PowerPlantOutput]:
    try:
        return calculate_production_plan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)