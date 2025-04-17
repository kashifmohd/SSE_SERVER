# sse_calculator.py
import requests
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

# 1. Create an MCP server instance
mcp = FastMCP("SSE Calculator and Weather")

# Calculator Tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtracts the second number from the first."""
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers."""
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divides the first number by the second."""
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return a / b

# Weather Tool
def get_weather_for_city(city: str) -> str:
    """Gets the current weather for a given city using wttr.in (HTTP)."""
    print("WARNING: Disabling SSL verification due to geopy issues. This is a security risk!")
    try:
        # Use HTTP to make the initial geocoding request
        geolocator = Nominatim(user_agent="weather_app", scheme="http")
        location = geolocator.geocode(city)
        if location:
            lat, lon = location.latitude, location.longitude
        else:
            return f"Could not find location for {city}."

        # Use HTTP instead of HTTPS for wttr.in
        url = f"http://wttr.in/{lat},{lon}?format=%C+%t"
        # Warning: This disables SSL verification! Only use this in controlled environments.
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except GeocoderUnavailable:
        return "Geocoder service is unavailable."
    except GeocoderTimedOut:
        return "Geocoder service timed out."

@mcp.tool()
def get_weather(city: str) -> str:
    """Gets the current weather for a given city."""
    weather_info = get_weather_for_city(city)
    return weather_info

# 3. Create a Starlette ASGI application
app = Starlette()

# 4. Mount the FastMCP SSE application to the Starlette app
app.mount('/', app=mcp.sse_app())

# 5. Run the server using uvicorn when the script is executed
if __name__ == "__main__":
    print("Starting SSE Calculator and Weather server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

