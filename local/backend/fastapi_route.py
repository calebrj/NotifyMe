from fastapi import FastAPI
import requests
import json
import os
import logging
import datetime  
#from dotenv import load_dotenv

# uvicorn fastapi_route:app --host 0.0.0.0 --port 8002

app = FastAPI()  # Create a FastAPI instance

# Using environment variables for security
# load_dotenv(dotenv_path="../.env")
TOMTOM_API_KEY = os.environ.get("TOMTOM_API_KEY")

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Folder to store all route data in JSON files
SAVE_FOLDER = "routes_data"

# Ensure the folder for the data exists
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)  # Creates the folder if it doesn't exist
    logging.info(f"Created folder: {SAVE_FOLDER}")

def save_route_to_file(data):
    """ Saves the TomTom API response to a new JSON file inside 'routes_data/'."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Generate a unique timestamp, so each file is different
    filename = os.path.join(SAVE_FOLDER, f"route_{timestamp}.json")  # Save file inside folder

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)  # Saves the JSON route data with indentation

    logging.info(f"Route data saved to {filename}")  # Logging the saved file


@app.post("/route")
async def get_route(data: dict):    
    """ Receives frontend request, fetch route from TomTom API and return formatted route points for the frontend."""
    logging.info(f"Received route request: {data}")

    start = data.get("start")
    end = data.get("end")

    logging.info (f"Start : {start}, End : {end}")

    if not start or not end:
        return {"error": "Missing start or end location"}

    # Construct API URL to get TomTom API response for route details
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start['lat']},{start['lng']}:{end['lat']},{end['lng']}/json?key={TOMTOM_API_KEY}&routeType=fastest&instructionsType=text&traffic=true&travelMode=car"

    logging.info (f"URL: {url}")

    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"TomTom API Error: {response.status_code}")
        return {"error": "Failed to fetch route"}

    route_data = response.json()  # Converts response to JSON

    # Saves the full TomTom API response in the 'routes_data/' folder
    save_route_to_file(route_data)  

    logging.info(f"TomTom API Response: {route_data}")

    if "routes" not in route_data or not route_data["routes"]:
        logging.warning("No route found in API response")
        return {"error": "No route found"}

    try:
        # Extract and format route points
        route_points = [
            {"lat": point["latitude"], "lng": point["longitude"]}
            for point in route_data["routes"][0]["legs"][0]["points"]
        ]

        logging.info(f"Formatted Route Points: {route_points}")
        return {"route": route_points}

    except (KeyError, IndexError) as e:
        logging.error(f"Error parsing route: {e}")
        return {"error": "Invalid route data format"}
