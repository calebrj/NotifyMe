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

const DEFAULT_PORT = parseInt(process.env.SERVER_PORT || 5000);
portfinder.basePort = DEFAULT_PORT;
const model_port = 8001;
const route_port = 8002;

// 1) Start FastAPI_Model Automatically 
/*
console.log("starting fastAPI ML model server...");
const fastApiModel = exec(`uvicorn fastapi_model:app --host 0.0.0.0 --port ${model_port}`, (error, stdout, stderr) => {
    if (error)
        console.error(`FastAPI failed to start: ${error.message}`);
    if (stderr)
        console.error(`FastAPI stderr: ${stderr}`);
    console.log(`FastAPI Server Output:\n${stdout}`);
});
*/

// 2) Start FastAPI Route Fetching Server
/*
console.log("Starting FastAPI Route API server...");
const fastApiRoute = exec(`uvicorn fastapi_route:app --host 0.0.0.0 --port ${route_port}`, (error, stdout, stderr) => {
    if (error)
        console.error(`FastAPI Route API Error: ${error.message}`);
    if (stderr)
        console.error(`FastAPI Route API stderr: ${stderr}`);
    console.log(`FastAPI Route API Output:\n${stdout}`);
});
*/

// Automatically find an available port
portfinder.getPort((err, port) => {
    if (err) {
        console.error("Error finding an available port:", err);
        process.exit(1); // Exit if no port is available
    }

    app.listen(port, () => {
        console.log(`Server is running on http://localhost:${port}`);
    });
    app.get("/port", (req, res) => {
        res.json({ port });
    });
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

// Simple health check endpoint for React
app.get("/api", (req, res) => {
    res.json({ message: "Backend server is running!" });
});


// API to save locations and get travel time prediction
app.post("/api/save-locations", async (req, res) => {
    const { departure, destination } = req.body;

    if (!departure || !destination) {
        return res.status(400).json({ message: "Departure and Destination are required" });
    }

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

        const routeFeature = {
            start: departure,
            end: destination
        };
        console.log("routeFeature:", routeFeature);

        // Model Prediction  
        const response = await axios.post(`http://model:${model_port}/predict`, { features });
        const prediction = response.data.prediction;
        console.log("Prediction:", prediction);

        // Get - Route
        const routeResponse = await axios.post(`http://route:${route_port}/route`, routeFeature);
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
