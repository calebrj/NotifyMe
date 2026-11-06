import requests
import random
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env")

api_key = os.environ.get("GoogleMapAPI")

#Function that makes an APi request to google
def get_travel_time(origin, destination):
    mode='driving'
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': f"{origin[0]},{origin[1]}",  # Latitude, Longitude of Origin
        'destinations': f"{destination[0]},{destination[1]}",  # Latitude, Longitude of Destination
        'mode': mode,  # Travel mode: driving, walking, bicycling, or transit
        'key': api_key
    }
    # Send the API request
    response = requests.get(url,params)
    print (response)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print (data)
  

origin =  43.656071, -79.380280
destination = 43.677128, -79.633453
get_travel_time(origin, destination)