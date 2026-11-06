import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

#Opening data file
with open("CarTravelTimeData.json", "r") as file:
    data = json.load(file)

#Scaler object
scaler = StandardScaler()

#Converting the data array in a massive numpy array of [N,9] dimensions
#data_array = np.array([[entry["time"], entry["dow"], entry["currentt"], entry["currentp"],entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"], entry["traveltime"]] for entry in data])
data_array = np.array([[entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"], entry["traveltime"]] for entry in data])

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
    if data_array[i][4] < 5:
        bet0and5.append(data_array[i])
    elif data_array[i][4] >= 5 and data_array[i][4] < 10:
        bet5and10.append(data_array[i])
    elif data_array[i][4] >= 10 and data_array[i][4] < 15:
        bet10and15.append(data_array[i])
    elif data_array[i][4] >= 15 and data_array[i][4] < 20:
        bet15and20.append(data_array[i])
    elif data_array[i][4] >= 20 and data_array[i][4] < 25:
        bet20and25.append(data_array[i])
    elif data_array[i][4] >= 25 and data_array[i][4] < 30:
        bet25and30.append(data_array[i])
    elif data_array[i][4] >= 30 and data_array[i][4] < 35:
        bet30and35.append(data_array[i])
    elif data_array[i][4] >= 35 and data_array[i][4] < 40:
        bet35and40.append(data_array[i])
    elif data_array[i][4] >= 40 and data_array[i][4] < 45:
        bet40and45.append(data_array[i])
    elif data_array[i][4] >= 45 and data_array[i][4] < 50:
        bet45and50.append(data_array[i])
    elif data_array[i][4] >= 50 and data_array[i][4] < 55:
        bet50and55.append(data_array[i])
    elif data_array[i][4] >= 55 and data_array[i][4] < 60:
        bet55and60.append(data_array[i])

print("Datasets distribution by intervals of 5 min, from 0 to 60:")
print(len(bet0and5)," ",len(bet5and10)," ",len(bet10and15)," ",len(bet15and20)," ",len(bet20and25)," ",len(bet25and30)," ",len(bet35and40)," ",len(bet40and45)," ",len(bet45and50)," ",len(bet50and55)," ",len(bet55and60))

#Making a more balanced dataset with equal number of data for each travel time estimate
data_array2 = []
smallestset = min(len(bet0and5),len(bet5and10),len(bet10and15),len(bet15and20),len(bet20and25),len(bet25and30),len(bet30and35),len(bet35and40),len(bet40and45),len(bet45and50),len(bet50and55),len(bet55and60))
print(smallestset)
for i in range(smallestset):
    #data_array2.append(bet0and5[i])
    data_array2.append(bet5and10[i])
    data_array2.append(bet10and15[i])
    data_array2.append(bet15and20[i])
    data_array2.append(bet20and25[i])
    data_array2.append(bet25and30[i])
    data_array2.append(bet30and35[i])
    data_array2.append(bet35and40[i])
    data_array2.append(bet40and45[i])
    data_array2.append(bet45and50[i])
    data_array2.append(bet50and55[i])
    data_array2.append(bet55and60[i])

    
data_array2 = np.array(data_array2)
print(len(data_array2))
data_standardized = scaler.fit_transform(data_array2)

#Selecting columns for features and target output vector
#X = data_array[:,:-1]
Y = data_array2[:,-1]
X_standardized = data_standardized[:,:-1]
#Y_standardized = data_standardized[:,-1]


#Spliting dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(X_standardized, Y, test_size=0.2, random_state=42)

model = LinearRegression()

model.fit(X_train,y_train)

traveltimeestimate = model.predict(X_test)

mae = mean_absolute_error(y_test, traveltimeestimate)
mse = mean_squared_error(y_test, traveltimeestimate)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, traveltimeestimate)
print("Intercept:", model.intercept_)
print("Coefficients:", model.coef_)
#for i in range(len(y_test) - 1, -1, -1):  # Loop from last index to first
#    if (traveltimeestimate[i] / y_test[i] * 100) > 120:  # >20% error
#        y_test = np.delete(y_test, i)
#        traveltimeestimate = np.delete(traveltimeestimate, i)

# Coordinates for Dundas Station (Toronto) → Pearson Airport
test_input = np.array([[ 43.6565, -79.3807,  43.68611, -79.61972]])
# Predict travel time
predicted_travel_time = model.predict(test_input)
print(f"Estimated Travel Time: {predicted_travel_time[0]:.2f} minutes")


plt.scatter(y_test, traveltimeestimate)
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted Travel Time")
plt.title("Actual vs Predicted Travel Time")
plt.show() 


model2 = LinearRegression()
y_test = np.array(y_test).reshape(-1,1)
model2.fit(y_test,traveltimeestimate)
estimate2 = model2.predict(y_test)

# Coordinates for Dundas Station (Toronto) → Pearson Airport
test_input = np.array([[43.6565, -79.3807,  43.68611, -79.61972]])
# Predict travel time
predicted_travel_time = model2.predict(test_input)
print(f"Estimated Travel Time: {predicted_travel_time[0]:.2f} minutes")


plt.plot(y_test,estimate2, color='red',label = "Regression Line")
plt.scatter(y_test, traveltimeestimate)
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted Travel Time")
plt.title("Actual vs Predicted Travel Time")
plt.show() 

