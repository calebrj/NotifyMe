import requests
import random
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env")

api_key = os.environ.get("GoogleMapAPI")

#Function that makes an APi request to google
def get_travel_time(api_key, origin, destination, mode='driving'):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': f"{origin[0]},{origin[1]}",  # Latitude, Longitude of Origin
        'destinations': f"{destination[0]},{destination[1]}",  # Latitude, Longitude of Destination
        'mode': mode,  # Travel mode: driving, walking, bicycling, or transit
        'key': api_key
    }
    # Send the API request
    response = requests.get(url,params)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        try:
            # Extract distance and duration
            duration = data['rows'][0]['elements'][0]['duration']['text']
            return duration
        except (IndexError, KeyError):
            return "Error: Could not find travel time"
    else:
        return f"Error: {response.status_code}"

# Function using Open-Meteo API to get weather data
def get_weather_data(latitude, longitude):
    apiUrl = "https://api.open-meteo.com/v1/forecast"
    apiParams = {
        "latitude": latitude,       # Location's latitude
        "longitude": longitude,     # Location's longitude
        "current": "temperature_2m,precipitation,precipitation_probability",    # Current weather data request
    }

    try:
        response = requests.get(apiUrl, params=apiParams)
        if response.status_code == 200: # Successful request
            data = response.json()  # API returned data

            # Extract the current weather data
            current_weather = data.get("current", {})
            current_temp = current_weather.get("temperature_2m", "N/A")  # Temperature in degrees Celsius
            current_precip = current_weather.get("precipitation", 0)     # Precipitation in mm
            current_precip_prob = current_weather.get("precipitation_probability", "N/A")  # Current precipitation percentage

            return {
                "temperature": current_temp,
                "precipitation": current_precip,
                "current_precipitation_probability": current_precip_prob,
            }
        else:   # If the request fails
            print(f"Failed to get weather data. Error status code = {response.status_code}. \nError text: {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

#Function writes + saves our collected feature/travel time data to a JSON file
def write_var_to_json( time, dow, currentt, currentp, startvert, starthori, endvert, endhori, traveltime ,output_file):
    data = {
        "time": time,
        "dow": dow,
        "currentt": currentt,
        "currentp": currentp,
        "startvert": startvert,
        "starthori": starthori,
        "endvert": endvert,
        "endhori": endhori,
        "traveltime": traveltime,
    }
    # Check if the file exists
    if os.path.exists(output_file):
        # Read existing data
        with open(output_file, 'r') as json_file:
            try:
                existing_data = json.load(json_file)
                # Ensure it's a list
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                # If the file is empty or invalid, start with an empty list
                existing_data = []
    else:
        # If the file does not exist, start with an empty list
        existing_data = []
    # Append the new data
    existing_data.append(data)

    # Write the updated data back to the file
    with open(output_file, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

    print(f"Data successfully written to {output_file}")

def runscript(times):
    for i in range(times):
        #First aqquuiring all of the input features
        #Time: hour.minute formatting
        currenttime = datetime.now()
        time = currenttime.hour + currenttime.minute/100

        #Day of the week: 1 = Monday, 7 = Sunday
        dow = currenttime.weekday() + 1

        #Destination Coordinates and Starting Coordinates Generation, Coordinates Format [Vertical, Horizontal] (Google maps is wierdly inverted to the classic x,y formatting you would expect)
        #Boundaries for our project are: BR = [43.62744, -79.34394] BL = [43.62744, -79.61280] TL = [43.73308, -79.61280] TR = [43.73308,-79.34394]
        #Horizontal effectively ranges from -7934394 to -7961280
        #Vertical effectively ranges from 4362744 to 4373308
        #Generating random starting coordinates
        starthori = random.randint(7934394,7961280)
        starthori = (starthori / 10**5) * (-1) #converting to the google maps horizontal 5 decimal point float
        startvert = random.randint(4362744,4373308)
        startvert = (startvert / 10**5)

        #Generating random destination coordinates
        endhori = random.randint(7934394,7961280)
        endhori = (endhori / 10**5) * (-1) #converting to the google maps horizontal 5 decimal point float
        endvert = random.randint(4362744,4373308)
        endvert = (endvert / 10**5)

        #Making API request to Google to aqquire travel time between the two randomly generated coordinates
        origin = (startvert,starthori)
        destination = (endvert, endhori)
        travel_time = get_travel_time(api_key, origin, destination, mode="driving")
        if travel_time == "Error: Could not find travel time":
            travel_time = 9999
        travel_time = int(travel_time.split()[0]) #extracting the time value in seconds from the response and converting to min
        print(f"Travel Time: {travel_time}")

        #API Request for the current weather temperature and precipitation in the Toronto area
        current_weather = get_weather_data(startvert,starthori)
        currentt = current_weather["temperature"] #temperature in degrees celcius
        currentp = current_weather["precipitation"] #volume of precipitation

        #Saving the features and the resulting/corresponding travel time to a JSON file
        output_file = "CarTravelTimeSlidingOnSnow.json"
        write_var_to_json(time, dow, currentt, currentp, startvert, starthori, endvert, endhori, travel_time ,output_file)

runscript(55)