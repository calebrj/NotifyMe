// lsof -i :8001
// kill -9 10222

const express = require("express");
const cors = require("cors");
const axios = require("axios");
const portfinder = require("portfinder"); // Auto-finds an available port
const { exec } = require("child_process"); // exec import

const app = express();
app.use(cors());
app.use(express.json()); // Enable JSON body parsing

const port = 8000;
const model_port_forest = 8001;
const route_port = 8002;
//portfinder.basePort = DEFAULT_PORT; // Start searching from this port

// // 1) Start FastAPI_Model Automatically
// console.log("starting fastAPI ML model server...");
// const fastApiModel = exec(`uvicorn fastapi_model:app --host 0.0.0.0 --port ${model_port}`, (error, stdout, stderr) => {
//   if (error)
//     console.error(`FastAPI failed to start: ${error.message}`);
//   if (stderr)
//     console.error(`FastAPI stderr: ${stderr}`);
//   console.log(`FastAPI Server Output:\n${stdout}`);
// });

// // 2) Start FastAPI Route Fetching Server
// console.log("Starting FastAPI Route API server...");
// const fastApiRoute = exec(`uvicorn fastapi_route:app --host 0.0.0.0 --port ${route_port}`, (error, stdout, stderr) => {
//   if (error)
//     console.error(`FastAPI Route API Error: ${error.message}`);
//   if (stderr)
//     console.error(`FastAPI Route API stderr: ${stderr}`);
//   console.log(`FastAPI Route API Output:\n${stdout}`);
// });

// // Automatically find an available port
// portfinder.getPort((err, port) => {
//   if (err) {
//     console.error("Error finding an available port:", err);
//     process.exit(1); // Exit if no port is available
//   }

app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on ${port}`);
});
app.get("/port", (req, res) => {
  res.json({ port });
});



const WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast";

// Function to fetch weather data from Open-Meteo API
async function getWeatherData(latitude, longitude) {
  try {
    const response = await axios.get(WEATHER_API_URL, {
      params: {
        latitude: latitude,
        longitude: longitude,
        current: "temperature_2m,precipitation",
      },
    });

    if (response.status === 200) {
      const currentWeather = response.data.current || {};
      return {
        temperature: currentWeather.temperature_2m || "N/A",
        precipitation: currentWeather.precipitation || 0,
      };
    } else {
      console.error(`Failed to get weather data. Status: ${response.status}`);
      return null;
    }
  } catch (error) {
    console.error(`Error fetching weather data: ${error.message}`);
    return null;
  }
}

// Function to get current time and day of the week
function getTimeFeatures() {
  const currentTime = new Date();
  const time = currentTime.getHours() + currentTime.getMinutes() / 100; // Format: HH.MM
  const dow = currentTime.getDay() === 0 ? 7 : currentTime.getDay(); // Sunday=7, Monday=1
  return { time, dow };
}

// API to save locations and get travel time prediction
app.post("/api/save-locations", async (req, res) => {

  // 1) Fetch departure & destination data from req
  const { departure, destination } = req.body;

  if (!departure || !destination) {
    return res.status(400).json({ message: "Departure and Destination are required" });
  }

  // 2) Fetch Weather & Time data
  try {
    // Fetch weather data for the departure location
    const weatherData = await getWeatherData(departure.lat, departure.lng);

    // Get time-based features
    const { time, dow } = getTimeFeatures();

    // Prepare input features in the correct order
    const features = [
      time,  // Current time (HH.MM format)
      dow,  // Day of the week (1=Monday, 7=Sunday)
      weatherData.temperature,  // Temperature (°C)
      weatherData.precipitation,  // Precipitation (mm)
      departure.lat,  // Departure latitude
      departure.lng,  // Departure longitude
      destination.lat,  // Destination latitude
      destination.lng   // Destination longitude
    ];
    console.log("features:", features);


    const routeFeature = {
      start: departure,
      end: destination
    };
    console.log("routeFeature:", routeFeature);

    // 3) Model Prediction
    //const response = await axios.post(`10.0.180.15:8001/predict`, { features });
    // Forest
    const response = await axios.post("http://fastapi-model-forest-service:8001/predict_forest", { features });
    let prediction_forest = response.data.prediction;
    console.log("Prediction_Forest:", prediction_forest);

    // If it's an array, get the first element
    if (Array.isArray(prediction_forest)) {
      prediction_forest = prediction_forest[0];
    }

    // CNN
    const response2 = await axios.post("http://fastapi-model-cnn-service:8003/predict_cnn", { features });
    const prediction_cnn = response2.data.prediction;
    console.log("Prediction_CNN:", prediction_cnn);

    // 4) calculate average btw forest & cnn
    const prediction = (prediction_forest + prediction_cnn) / 2;
    console.log("Avg Prediction: ", prediction);


    // Get - Route
    //const routeResponse = await axios.post(`10.0.87.180:8002/route`, routeFeature);
    const routeResponse = await axios.post("http://fastapi-route-service:8002/route", routeFeature);

    // console.log("RouteResponse: ", routeResponse);
    if (!routeResponse.data.route) {
      return res.status(404).json({ message: "No route found" });
    }
    const route_points = routeResponse.data.route;
    console.log("Route:", route_points);

    res.json({
      temperature: weatherData.temperature,
      precipitation: weatherData.precipitation,
      estimated_travel_time: prediction,
      route: route_points
    });

  } catch (error) {
    console.error("Error fetching data:", error.message);
    res.status(500).json({ message: "Error fetching data", error: error.message });
  }


});
