import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random as rand

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import regularizers

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras import datasets, layers, models, Input

#Opening data file
with open("CarTravelTimeData - Snow - Beyond.json", "r") as file:
    data = json.load(file)
print("TensorFlow version:", tf.__version__)
#Scaler object
scaler = StandardScaler()
scalerimba = StandardScaler()

#Converting the data array in a massive numpy array of [N,9] dimensions
data_array = np.array([[entry["time"], entry["dow"], entry["currentt"], entry["currentp"],entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"], entry["traveltime"]] for entry in data])
#data_array = np.array([[entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"], entry["traveltime"]] for entry in data])

#Purging points with value of 1, that have a crazy high euclidian, these were wrong returns from the API
print(len(data_array))
start = data_array[:, [4, 5]]  # startvert, starthori
end = data_array[:, [6, 7]]    # endvert, endhori

# Compute Euclidean distance
dist = np.linalg.norm(end - start, axis=1)

# Keep only rows where NOT (travel_time == 1 AND distance > 0.02)
mask = ~((data_array[:, 8] == 1) & (dist > 0.01))
data_array = data_array[mask]
print(len(data_array))

#Checking which travel time data we have, trying to balance it out a little bit for an even distribution
#Dataset is currently highly biased towards 20 min otherwise
bet0and5 = []
bet5and10 = []
bet10and15 = []
bet15and20 = []
bet20and25 = []
bet25and30 = []
bet30and35 = []
bet35and40 = []
bet40and45 = []
bet45and50 = []
bet50and55 = []
bet55and60 = []
for i in range(len(data_array)):
    if data_array[i][8] < 5:
        bet0and5.append(data_array[i])
    elif data_array[i][8] >= 5 and data_array[i][8] < 10:
        bet5and10.append(data_array[i])
    elif data_array[i][8] >= 10 and data_array[i][8] < 15:
        bet10and15.append(data_array[i])
    elif data_array[i][8] >= 15 and data_array[i][8] < 20:
        bet15and20.append(data_array[i])
    elif data_array[i][8] >= 20 and data_array[i][8] < 25:
        bet20and25.append(data_array[i])
    elif data_array[i][8] >= 25 and data_array[i][8] < 30:
        bet25and30.append(data_array[i])
    elif data_array[i][8] >= 30 and data_array[i][8] < 35:
        bet30and35.append(data_array[i])
    elif data_array[i][8] >= 35 and data_array[i][8] < 40:
        bet35and40.append(data_array[i])
    elif data_array[i][8] >= 40 and data_array[i][8] < 45:
        bet40and45.append(data_array[i])
    elif data_array[i][8] >= 45 and data_array[i][8] < 50:
        bet45and50.append(data_array[i])
    elif data_array[i][8] >= 50 and data_array[i][8] < 55:
        bet50and55.append(data_array[i])
    elif data_array[i][8] >= 55 and data_array[i][8] < 60:
        bet55and60.append(data_array[i])

bet0and5copy = bet0and5.copy()
bet5and10copy = bet5and10.copy()
bet10and15copy = bet10and15.copy()
bet15and20copy = bet15and20.copy()
bet20and25copy = bet20and25.copy()
bet25and30copy = bet25and30.copy()
bet30and35copy = bet30and35.copy()
bet35and40copy = bet35and40.copy()
bet40and45copy = bet40and45.copy()
bet45and50copy = bet45and50.copy()
bet50and55copy = bet50and55.copy()
bet55and60copy = bet55and60.copy()

print("Datasets distribution by intervals of 5 min, from 0 to 60:")
print(len(bet0and5)," ",len(bet5and10)," ",len(bet10and15)," ",len(bet15and20)," ",len(bet20and25)," ",len(bet25and30)," ",len(bet30and35)," ",len(bet35and40)," ",len(bet40and45)," ",len(bet45and50)," ",len(bet50and55)," ",len(bet55and60))
print("Alternate balanced dataset distrbution:")
print("0-10 min: ",len(bet0and5) + len(bet5and10),"10-15 min: ",len(bet10and15),"15-20 min: ",len(bet15and20),"20-25 min: ",len(bet20and25),"25-30 min: ",len(bet25and30),"30-40 min: ",len(bet30and35)+len(bet35and40),"40-60 min: ",len(bet40and45)+len(bet45and50)+len(bet50and55)+len(bet55and60))

#Making a more balanced dataset with equal number of data for each travel time estimate
data_array2 = []
smallestset = min(len(bet0and5),len(bet5and10),len(bet10and15),len(bet15and20),len(bet20and25),len(bet25and30),len(bet30and35),len(bet35and40),len(bet40and45),len(bet45and50),len(bet50and55),len(bet55and60))
print(smallestset)
for i in range(smallestset):
    selected = rand.randint(0,len(bet0and5)-1)
    data_array2.append(bet0and5[selected])
    del bet0and5[selected]
    selected = rand.randint(0,len(bet5and10)-1)
    data_array2.append(bet5and10[selected])
    del bet5and10[selected]
    selected = rand.randint(0,len(bet10and15)-1)
    data_array2.append(bet10and15[selected])
    del bet10and15[selected]
    selected = rand.randint(0,len(bet15and20)-1)
    data_array2.append(bet15and20[selected])
    del bet15and20[selected]
    selected = rand.randint(0,len(bet20and25)-1)
    data_array2.append(bet20and25[selected])
    del bet20and25[selected]
    selected = rand.randint(0,len(bet25and30)-1)
    data_array2.append(bet25and30[selected])
    del bet25and30[selected]
    selected = rand.randint(0,len(bet30and35)-1)
    data_array2.append(bet30and35[selected])
    del bet30and35[selected]
    selected = rand.randint(0,len(bet35and40)-1)
    data_array2.append(bet35and40[selected])
    del bet35and40[selected]
    selected = rand.randint(0,len(bet40and45)-1)
    data_array2.append(bet40and45[selected])
    del bet40and45[selected]
    selected = rand.randint(0,len(bet45and50)-1)
    data_array2.append(bet45and50[selected])
    del bet45and50[selected]
    selected = rand.randint(0,len(bet50and55)-1)
    data_array2.append(bet50and55[selected])
    del bet50and55[selected]
    selected = rand.randint(0,len(bet55and60)-1)
    data_array2.append(bet55and60[selected])
    del bet55and60[selected]

data_array3 = []
bet0and10 = bet0and5copy + bet5and10copy
bet30and40 = bet30and35copy + bet35and40copy
bet40and60 = bet40and45copy + bet45and50copy + bet50and55copy + bet55and60copy
smallestset = min(len(bet0and10),len(bet10and15copy),len(bet15and20copy),len(bet20and25copy),len(bet25and30copy),len(bet30and40),len(bet40and60))
print(smallestset)
for i in range(smallestset):
    selected = rand.randint(0,len(bet0and10)-1)
    data_array3.append(bet0and10[selected])
    del bet0and10[selected]
    selected = rand.randint(0,len(bet10and15copy)-1)
    data_array3.append(bet10and15copy[selected])
    del bet10and15copy[selected]
    selected = rand.randint(0,len(bet15and20copy)-1)
    data_array3.append(bet15and20copy[selected])
    del bet15and20copy[selected]
    selected = rand.randint(0,len(bet20and25copy)-1)
    data_array3.append(bet20and25copy[selected])
    del bet20and25copy[selected]
    selected = rand.randint(0,len(bet25and30copy)-1)
    data_array3.append(bet25and30copy[selected])
    del bet25and30copy[selected]
    selected = rand.randint(0,len(bet30and40)-1)
    data_array3.append(bet30and40[selected])
    del bet30and40[selected]
    selected = rand.randint(0,len(bet40and60)-1)
    data_array3.append(bet40and60[selected])
    del bet40and60[selected]

print(len(data_array))
print(len(data_array2))
print(len(data_array3))

data_array2 = np.array(data_array2)
data_array3 = np.array(data_array3)
data_array_balanced = data_array2[:,:-1]
data_array_alldata = data_array[:,:-1]
data_array_alt_balancing = data_array3[:,:-1]
data_array_alldata = scalerimba.fit_transform(data_array_alldata)
data_array_balanced = scaler.fit_transform(data_array_balanced)
data_array_alt_balancing = scaler.fit_transform(data_array_alt_balancing)

#Selecting columns for features and target output vector for balanced dataset
Y_balanced = data_array2[:,-1]
X_balanced = data_array_balanced

#Selecting columns for features and target output vector for alt balanced dataset
Y_alt_balanced = data_array3[:,-1]
X_alt_balanced = data_array_alt_balancing

#Selecting columns for features and target output vector for all data
Y_all = data_array[:,-1]
X_all = data_array_alldata

#Reshaping specifically for CNN
X_balanced = X_balanced.reshape(len(X_balanced),8,1)
X_all = X_all.reshape(len(X_all),8,1)
X_alt_balanced = X_alt_balanced.reshape(len(X_alt_balanced),8,1)

#Spliting dataset into training and testing, using all data points
X_train_all, X_test_all, y_train_all, y_test_all = train_test_split(X_all, Y_all, test_size=0.2, random_state=42)

#Spliting dataset into training and testing
X_train_balanced, X_test_balanced, y_train_balanced, y_test_balanced = train_test_split(X_balanced, Y_balanced, test_size=0.2, random_state=42)

#Spliting dataset into training and testing
X_train_alt_balanced, X_test_alt_balanced, y_train_alt_balanced, y_test_alt_balanced = train_test_split(X_alt_balanced, Y_alt_balanced, test_size=0.2, random_state=42)

#Below is a 1D CNN model for both datasets
def create_model():
    model = keras.Sequential([
        layers.Conv1D(filters=32, kernel_size=1, activation='relu', input_shape=(8, 1)),
        layers.Conv1D(filters=64, kernel_size=1, activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu',kernel_regularizer=regularizers.l2(0.01)),
        layers.Dropout(0.3), 
        layers.Dense(32, activation='relu',kernel_regularizer=regularizers.l2(0.01)),
        layers.Dense(1) 
    ])
    optimizer = keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    return model

model_balanced = create_model()
history_balanced = model_balanced.fit(X_train_balanced, y_train_balanced, epochs=100, batch_size=32, validation_data=(X_test_balanced, y_test_balanced))
model_alt_balanced = create_model()
history_alt_balanced = model_alt_balanced.fit(X_train_alt_balanced, y_train_alt_balanced, epochs=22, batch_size=32, validation_data=(X_test_alt_balanced, y_test_alt_balanced)) #23
model_all = create_model()
history_unbalanced = model_all.fit(X_train_all, y_train_all, epochs=15, batch_size=32, validation_data=(X_test_all, y_test_all)) #15


travel_time_estimate_balanced = model_balanced.predict(X_test_balanced)
travel_time_estimate_all = model_all.predict(X_test_all)
travel_time_estimate_alt_balanced = model_alt_balanced.predict(X_test_alt_balanced)

# Coordinates for Dundas Station (Toronto) → Pearson Airport
test_input = np.array([[15,4,5,0,43.6565,-79.3807, 43.68611,-79.61972]])
test_input = scaler.transform(test_input)  # Apply same transformation
test_input = test_input.reshape(1, 8, 1)

# Predict travel time
predicted_travel_time = model_balanced.predict(test_input)
print(f"Estimated Travel Time Using Balanced Model: {predicted_travel_time[0][0]:.2f} minutes")

test_input = np.array([[15,4,5,0,43.6565,-79.3807, 43.68611,-79.61972]])
test_input = scalerimba.transform(test_input)  # Apply same transformation
test_input = test_input.reshape(1, 8, 1)
predicted_travel_time = model_all.predict(test_input)
print(f"Estimated Travel Time Using Unbalanced Model: {predicted_travel_time[0][0]:.2f} minutes")

test_input = np.array([[15,4,5,0,43.6565,-79.3807, 43.68611,-79.61972]])
test_input = scalerimba.transform(test_input)  # Apply same transformation
test_input = test_input.reshape(1, 8, 1)
predicted_travel_time = model_alt_balanced.predict(test_input)
print(f"Estimated Travel Time Using Alternatively Balanced Model: {predicted_travel_time[0][0]:.2f} minutes")

history_dict = history_balanced.history

import pickle
import os

# Create directory if not exists
os.makedirs("Models", exist_ok=True)

# Save the trained CNN model
model_balanced.save("Models/BalancedCNNModel.h5")
model_alt_balanced.save("Models/AltBalancedCNNModel.h5")
model_all.save("Models/UnbalancedCNNModel.h5")

# Save the StandardScalers
with open("Models/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("Models/scalerimba.pkl", "wb") as f:
    pickle.dump(scalerimba, f)

print(" Models and scalers saved in the 'Models/' folder.")


final_mse = history_dict['loss'][-1]
final_mae = history_dict['mae'][-1]
final_val_mse = history_dict['val_loss'][-1]
final_val_mae = history_dict['val_mae'][-1]

print(f"Final Training MSE: {final_mse:.4f}")
print(f"Final Validation MSE: {final_val_mse:.4f}")
print(f"Final Training MAE: {final_mae:.4f}")
print(f"Final Validation MAE: {final_val_mae:.4f}")

#Displaying results of the balanced model
plt.scatter(y_test_balanced, travel_time_estimate_balanced)
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted Travel Time")
plt.title("Actual vs Predicted Travel Time Using Balanced 1D CNN Model")
plt.show() 

plt.plot(history_balanced.history['mae'], label='MAE Training')
plt.plot(history_balanced.history['val_mae'], label='MAE Validation Set', linestyle='dashed')
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error (MAE)')
plt.legend()
plt.title('Training vs. MAE')
plt.show()

plt.plot(history_balanced.history['loss'], label='MSE Training')
plt.plot(history_balanced.history['val_loss'], label='MSE Validation Set', linestyle='dashed')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error (MSE)')
plt.legend()
plt.title('Training vs. MSE')
plt.show()

#Displaying results of the unbalanced model
plt.scatter(y_test_all, travel_time_estimate_all)
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted Travel Time")
plt.title("Actual vs Predicted Travel Time Using Unbalanced 1D CNN Model")
plt.show() 

plt.plot(history_unbalanced.history['mae'], label='MAE Training')
plt.plot(history_unbalanced.history['val_mae'], label='MAE Validation Set', linestyle='dashed')
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error (MAE)')
plt.legend()
plt.title('Training vs. MAE')
plt.show()

plt.plot(history_unbalanced.history['loss'], label='MSE Training')
plt.plot(history_unbalanced.history['val_loss'], label='MSE Validation Set', linestyle='dashed')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error (MSE)')
plt.legend()
plt.title('Training vs. MSE')
plt.show()

#Displaying results of the alternatively balanced model
plt.scatter(y_test_alt_balanced, travel_time_estimate_alt_balanced)
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted Travel Time")
plt.title("Actual vs Predicted Travel Time Using Alternatively Balanced 1D CNN Model")
plt.show() 

plt.plot(history_alt_balanced.history['mae'], label='MAE Training')
plt.plot(history_alt_balanced.history['val_mae'], label='MAE Validation Set', linestyle='dashed')
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error (MAE)')
plt.legend()
plt.title('Training vs. MAE')
plt.show()

plt.plot(history_alt_balanced.history['loss'], label='MSE Training')
plt.plot(history_alt_balanced.history['val_loss'], label='MSE Validation Set', linestyle='dashed')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error (MSE)')
plt.legend()
plt.title('Training vs. MSE')
plt.show()

