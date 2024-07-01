from fastapi import FastAPI
from fastapi.responses import JSONResponse
from requests import get
import python_weather
import asyncio

ip = get("https://api.ipify.org").text
app = FastAPI()


def get_city():
    ip_address = ip
    response = get(f"https://ipapi.co/{ip_address}/json/").json()
    city = response.get("city")
    return city


async def get_weather(city: str) -> int:
    try:
        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            weather = await client.get(city)
            return weather.temperature
    except python_weather.exceptions.BadResponseError:
        # Handle bad response from weather API
        return None
    except python_weather.exceptions.BadQueryError:
        # Handle bad query to weather API
        return None
    except Exception as e:
        # Handle other exceptions
        return None


@app.get("/")
def read_root():
    return {"Server": "Live :)"}


@app.get("/api/hello")
def read_hello(visitor_name: str):
    city = get_city()
    weather = asyncio.run(get_weather(city=city))
    
    if weather is None:
        # Handle weather retrieval error
        return JSONResponse(content={"error": "Failed to retrieve weather information."})
    
    return JSONResponse(
        content={
            "client_ip": ip,
            "location": f"{city}",
            "greeting": f"Hello, {visitor_name}! The temperature is {weather} degrees Celsius in {city}",
        }
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)