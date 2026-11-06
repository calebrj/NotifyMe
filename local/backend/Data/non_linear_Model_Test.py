import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

# Opening data file
with open("CarTravelTimeData.json", "r") as file:
    data = json.load(file)

# Scaler object
scaler = StandardScaler()

# Converting data to numpy array (Using only coordinate-based features)
data_array = np.array([[entry["time"],entry["dow"], entry["currentt"],entry["currentp"],entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"], entry["traveltime"]] for entry in data])
#, 

# Splitting travel times into bins (to balance dataset)
travel_time_bins = [[], [], [], [], [], [], [], [], [], [], [], []]

for i in range(len(data_array)):
    travel_time = data_array[i][8]
    bin_index = min(int(travel_time // 5), 11)  # Binning travel times in 5-minute intervals
    travel_time_bins[bin_index].append(data_array[i])

# Finding smallest bin size for balance
smallest_set = min(len(bin) for bin in travel_time_bins if len(bin) > 0)

# Creating a balanced dataset
data_array2 = []
for bin in travel_time_bins:
    if len(bin) >= smallest_set:
        data_array2.extend(bin[:smallest_set])  # Equal sampling

data_array2 = np.array(data_array2)

# Standardizing the data
# data_standardized = scaler.fit_transform(data_array)

# Selecting features (X) and target (Y)
Y = data_array[:, -1]  # Travel time
Ys = data_array2[:, -1]
X = data_array[:, :-1]
Xs = data_array2[:, :-1]

# Splitting dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
Xs_train, Xs_test, ys_train, ys_test = train_test_split(Xs,Ys,test_size=0.2,random_state=42)

# **Random Forest Model**
model = RandomForestRegressor(n_estimators=100, random_state=42)  # 100 trees
modelS = RandomForestRegressor(n_estimators=100,random_state=42 )

# Training the model
model.fit(X_train, y_train)
modelS.fit(Xs_train, ys_train)

# Making predictions
travel_time_estimate = model.predict(X_test)

# Evaluating performance
mae = mean_absolute_error(y_test, travel_time_estimate)
mse = mean_squared_error(y_test, travel_time_estimate)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, travel_time_estimate)

print(f"Mean Absolute Error: {mae:.2f} min")
print(f"Mean Squared Error: {mse:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f} min")
print(f"R² Score: {r2:.2f}")

# Coordinates for Dundas Station (Toronto) → Pearson Airport
test_input = np.array([[13.45, 5, -4, 0.0,  43.6565, -79.3807,  43.68611, -79.61972]])
# Predict travel time
predicted_travel_time = model.predict(test_input)
print(f"Estimated Travel Time from Dundas to Pearson: {predicted_travel_time[0]:.2f} minutes")

#Balanced inputs 
predicted_travel_time_bal = modelS.predict(test_input)
print(f"Estimated Travel Time from Dundas to Pearson (balanced inputs): {predicted_travel_time_bal[0]:.2f} minutes")

# **Plot: Actual vs Predicted**
plt.scatter(y_test, travel_time_estimate, alpha=0.5)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label="Ideal Prediction")
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted Travel Time")
plt.legend()
plt.title("Random Forest: Actual vs Predicted Travel Time")
plt.show()