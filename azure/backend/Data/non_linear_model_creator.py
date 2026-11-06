import json
import os
import numpy as np
import pandas as pd
import pickle  # For saving the model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Load dataset
with open("CarTravelTimeData.json", "r") as file:
    data = json.load(file)

# Convert data to numpy array (Using only coordinate-based features)
data_array = np.array([[entry["time"], entry["dow"], entry["currentt"], entry["currentp"], entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"], entry["traveltime"]] for entry in data])

# Split travel times into bins (to balance dataset)
travel_time_bins = [[] for _ in range(12)]  # 12 bins

for i in range(len(data_array)):
    travel_time = data_array[i][8]
    bin_index = min(int(travel_time // 5), 11)  # Binning travel times in 5-minute intervals
    travel_time_bins[bin_index].append(data_array[i])

# Balance the dataset
smallest_set = min(len(bin) for bin in travel_time_bins if len(bin) > 0)
data_array_balanced = [bin[:smallest_set] for bin in travel_time_bins if len(bin) >= smallest_set]
data_array_balanced = np.vstack(data_array_balanced)

# Extract features and target variable
Y = data_array[:, -1]  # Travel time
Ys = data_array_balanced[:, -1]
X = data_array[:, :-1]
Xs = data_array_balanced[:, :-1]

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
Xs_train, Xs_test, ys_train, ys_test = train_test_split(Xs, Ys, test_size=0.2, random_state=42)

# Train the Random Forest Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model_balanced = RandomForestRegressor(n_estimators=100, random_state=42)

model.fit(X_train, y_train)
model_balanced.fit(Xs_train, ys_train)

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Models"))

# Save the trained models in the Models directory
model_path = os.path.join(MODEL_DIR, "travel_time_model.pkl")
model_balanced_path = os.path.join(MODEL_DIR, "travel_time_model_balanced.pkl")

with open(model_path, "wb") as file:
    pickle.dump(model, file)

with open(model_balanced_path, "wb") as file:
    pickle.dump(model_balanced, file)
    
# Evaluate the model
travel_time_estimate = model.predict(X_test)
mae = mean_absolute_error(y_test, travel_time_estimate)
mse = mean_squared_error(y_test, travel_time_estimate)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, travel_time_estimate)

print(f"Model Training Complete")
print(f"Mean Absolute Error: {mae:.2f} min")
print(f"Mean Squared Error: {mse:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f} min")
print(f"R² Score: {r2:.2f}")

print(f"Models saved as 'travel_time_model.pkl' and 'travel_time_model_balanced.pkl'")
