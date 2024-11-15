# Power Plant Production Plan API - Engie Coding Challenge

This API calculates how much power each of a multitude of different powerplants need to produce (a.k.a. the production-plan) when the load is given and takes into account the cost of the underlying energy sources (gas, kerosine) and the Pmin and Pmax of each powerplant.  

I chose to use the FastAPI framework for Python because it's modern, fast and easy to use.  

## Requirements

### Running Locally
- Python 3.8 or higher
- pip (Python package installer)

### Running with Docker
- Docker

## Installation

### Local Installation

1. Clone this repository or download the source code

2. Create a virtual environment (recommended):
```bash
python -m venv venv_pp # or any other name you want
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

### Docker Installation

1. Build the Docker image:
```bash
docker build -t powerplant-api .
```

## Running the API

### Running Locally

Start the API server by running:
```bash
python main.py
```

### Running with Docker

Run the container:
```bash
docker run -p 8888:8888 powerplant-api
```

The API will be available at `http://localhost:8888`

## API Endpoint

### POST /productionplan

Calculates the optimal production plan for the given power plants.

**Request Format:**
```json
{
  "load": float,
  "fuels": {
    "gas(euro/MWh)": float,
    "kerosine(euro/MWh)": float,
    "co2(euro/ton)": float,
    "wind(%)": float
  },
  "powerplants": [
    {
      "name": string,
      "type": string,
      "efficiency": float,
      "pmin": float,
      "pmax": float
    }
  ]
}
```

**Response Format:**
```json
[
  {
    "name": string,
    "p": float
  }
]
```

## Testing

You can test the API using the requests and json modules in Python:

```bash
import json
import requests

with open('payload3.json', 'r') as f:
    payload3 = json.load(f)

response = requests.post('http://0.0.0.0:8888/productionplan', json=payload3)
print(response.json())
```

Or use the built-in FastAPI documentation interface at `http://localhost:8888/docs`
