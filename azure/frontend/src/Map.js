import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./MapStyles.css"; // Ensure custom styles are applied

const graphhopperApiKey = process.env.REACT_APP_GRAPHHOPPER_API_KEY; // Load API key

const Map = () => {
    const mapContainerRef = useRef(null);
    const leafletMap = useRef(null);

    // State for departure search
    const [departureSearch, setDepartureSearch] = useState("");
    const [departureSuggestions, setDepartureSuggestions] = useState([]);
    const [departure, setDeparture] = useState(null);

    // State for destination search
    const [destinationSearch, setDestinationSearch] = useState("");
    const [destinationSuggestions, setDestinationSuggestions] = useState([]);
    const [destination, setDestination] = useState(null);

    // Route - array of coordinates 
    const [route, setRoute] = useState([]); // Stores the route as an array of coordinates

    // Button state
    const isSubmitDisabled = !departure || !destination;

    // State for received API response
    const [travelData, setTravelData] = useState(null);

    useEffect(() => {
        if (!mapContainerRef.current || leafletMap.current) return;

        const map = L.map(mapContainerRef.current, { zoomControl: true }).setView([43.6532, -79.3832], 13);
        leafletMap.current = map;

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: 'Map data © <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        }).addTo(map);

        return () => {
            if (leafletMap.current) {
                leafletMap.current.remove();
                leafletMap.current = null;
            }
        };
    }, []);
    
    //  Display Route on Map when `route` state updates
    useEffect(() => {
        if (!leafletMap.current || route.length === 0) return;

        // Remove existing route layers before adding a new one
        if (leafletMap.current.routeLayer) {
            leafletMap.current.removeLayer(leafletMap.current.routeLayer);
        }

        // Draw the new route on the map
        const routeLayer = L.polyline(route, { color: "blue", weight: 4 }).addTo(leafletMap.current);
        leafletMap.current.routeLayer = routeLayer;

        // Fit the map to show the full route
        leafletMap.current.fitBounds(routeLayer.getBounds());

    }, [route]); // Runs when `route` updates

    // const getBackendPort = async () => {
    //     try {
    //         const response = await fetch("http://localhost:5000/port");
    //         const data = await response.json();
    //         return data.port;
    //     } catch (error) {
    //         console.error("Error fetching backend port:", error);
    //         return 5000; // Fallback port
    //     }
    // };
    // Function to fetch location suggestions
    const fetchSuggestions = async (query, setSuggestions) => {
        if (!query || !graphhopperApiKey) {
            setSuggestions([]);
            return;
        }

        try {
            const response = await fetch(
                `https://graphhopper.com/api/1/geocode?q=${encodeURIComponent(query)}&limit=5&key=${graphhopperApiKey}`
            );
            const data = await response.json();

            if (data.hits) {
                setSuggestions(data.hits);
            }
        } catch (error) {
            console.error("Error fetching location suggestions:", error);
            setSuggestions([]);
        }
    };

    // Handle departure input changes
    const handleDepartureInputChange = (event) => {
        setDepartureSearch(event.target.value);
        fetchSuggestions(event.target.value, setDepartureSuggestions);
    };

    // Handle destination input changes
    const handleDestinationInputChange = (event) => {
        setDestinationSearch(event.target.value);
        fetchSuggestions(event.target.value, setDestinationSuggestions);
    };

    // Function to handle selecting a suggestion
    const handleSelectSuggestion = (selectedLocation, setType) => {
        if (setType === "departure") {
            setDepartureSearch(selectedLocation.name);
            setDeparture(selectedLocation);
            setDepartureSuggestions([]);
        } else {
            setDestinationSearch(selectedLocation.name);
            setDestination(selectedLocation);
            setDestinationSuggestions([]);
        }
        searchLocation(selectedLocation.point.lat, selectedLocation.point.lng, selectedLocation.name);
    };

    // Function to place markers on the map
    const searchLocation = (lat, lng, name) => {
        if (!leafletMap.current) return;

        const locationIcon = L.icon({
            iconUrl: "/red.png",
            iconSize: [15, 15],
            iconAnchor: [8, 7],
            popupAnchor: [0, 0]
        });

        const newMarker = L.marker([lat, lng], { icon: locationIcon }).addTo(leafletMap.current);

        const popup = L.popup({
            autoClose: false,
            closeOnClick: false
        }).setContent(`<b>${name}</b>`).setLatLng([lat, lng]);

        newMarker.bindPopup(popup).openPopup();
    };

    const displayTravelInfo = (data) => {
        setTravelData(data); // Update state to display data in UI
    };

    // Send data to backend
    const sendDataToBackend = async () => {
        if (!departure || !destination) {
            alert("No departure and destination selected");
            return;
        }

        const requestData = {
            departure: {
                name: departure.name,
                lat: departure.point.lat,
                lng: departure.point.lng
            },
            destination: {
                name: destination.name,
                lat: destination.point.lat,
                lng: destination.point.lng
            }
        };

        try {
            // // Fetch the backend port dynamically
            // const portResponse = await fetch("http://localhost:5001/port"); // Use default or known server port
            // const portData = await portResponse.json();
            // const backendPort = portData.port || 5000; // Fallback to default if port data is missing
        
            // Now send the request to the dynamically found backend port
            //const response = await fetch(`http://localhost:${backendPort}/api/save-locations`, {
            const response = await fetch(`https://notifyme.130.107.161.10.nip.io/api/save-locations`,{
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData),
            });
        
            const result = await response.json();
            console.log("Received response from backend:", result);
            const selectedFeatures = {
                temperature: result.temperature,
                precipitation: result.precipitation,
                estimated_travel_time: result.estimated_travel_time
            };            
            setTravelData(selectedFeatures); // Store API response data

            // Formatting Route 
            const formattedRoute = result.route.map(point => [point.lat, point.lng]); // Convert response to Leaflet-compatible format
            console.log("Formatted Route:", formattedRoute);
            setRoute(formattedRoute); // Update state with the new route
            
            // Display Travel Info 
            displayTravelInfo(selectedFeatures);

        } catch (error) {
            console.error("Error sending data:", error);
            alert("Failed to save locations.");
        }
        
    };

    return (
        <div>
            {/* Container for search boxes */}
            <div className="search-box-container">
                {/* Departure Box */}
                <div className="search-container">
                    <label><b>Departure:</b></label>
                    <input
                        type="text"
                        value={departureSearch}
                        onChange={handleDepartureInputChange}
                        placeholder="Search departure..."
                        className="geocoder-search-input"
                    />
                    {departureSuggestions.length > 0 && (
                        <ul className="suggestions-list">
                            {departureSuggestions.map((location, index) => (
                                <li key={index} onClick={() => handleSelectSuggestion(location, "departure")}>
                                    {location.name}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                {/* Destination Box */}
                <div className="search-container">
                    <label><b>Destination:</b></label>
                    <input
                        type="text"
                        value={destinationSearch}
                        onChange={handleDestinationInputChange}
                        placeholder="Search destination..."
                        className="geocoder-search-input"
                    />
                    {destinationSuggestions.length > 0 && (
                        <ul className="suggestions-list">
                            {destinationSuggestions.map((location, index) => (
                                <li key={index} onClick={() => handleSelectSuggestion(location, "destination")}>
                                    {location.name}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>

            {/* Submit Button */}
            <div className="button-container">
                <button
                    onClick={sendDataToBackend}
                    className="save-button"
                    disabled={isSubmitDisabled}
                >
                    Save Locations
                </button>
            </div>

            {travelData && (
                <div className="travel-info-box">
                    <h2>Estimated Travel Time: {Math.round(travelData.estimated_travel_time)} min</h2>
                    <h3>Temperature: {travelData.temperature}°C</h3>
                    <h3>Precipitation: {travelData.precipitation} mm</h3>
                </div>
            )}

            {/* Map Container */}
            <div ref={mapContainerRef} id="map"></div>
        </div>
    );

};

export default Map;
