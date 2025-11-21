# src/lfmsystem/tools.py
import datetime
import random

# Note: We don't verify/register here. We just define pure Python logic.
# This makes testing these functions incredibly easy.

def get_current_time() -> str:
    """
    Get the current local time.
    """
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def get_weather(city: str) -> str:
    """
    Get the current weather for a specific city.
    """
    # Simulating external API
    conditions = ["Sunny", "Rainy", "Cloudy", "Snowing"]
    temp = random.randint(-5, 35)
    return f"Weather in {city}: {random.choice(conditions)}, {temp}°C"

def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """
    Calculate Body Mass Index given weight in kg and height in meters.
    """
    try:
        bmi = weight_kg / (height_m ** 2)
        return f"BMI is {bmi:.2f}"
    except ZeroDivisionError:
        return "Error: Height cannot be zero."