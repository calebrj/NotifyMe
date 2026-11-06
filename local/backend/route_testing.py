import requests

# FastAPI server URL (Update if running on a different port)
FASTAPI_URL = "http://localhost:8000/api/get-route"

# Testing 
test_data = {
    "start": {"lat": 40.7128, "lng": -74.0060},  # New York City
    "end": {"lat": 34.0522, "lng": -118.2437}   # Los Angeles
}

def test_get_route():
    """ Sends a test request to the FastAPI get-route endpoint """
    try:
        response = requests.post(FASTAPI_URL, json=test_data)

        if response.status_code == 200:
            print("Request Successful!")
            print("Response JSON:")
            print(response.json())  # Print route points
        else:
            print(f"Request Failed! Status Code: {response.status_code}")
            print("Response:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_get_route()
