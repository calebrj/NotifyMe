import json
import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ==== Load and Parse Data ====
with open("CarTravelTimeData - Snow - Beyond.json", "r") as file:
    data = json.load(file)

data_array = np.array([[entry["time"], entry["dow"], entry["currentt"], entry["currentp"],
                        entry["startvert"], entry["starthori"], entry["endvert"], entry["endhori"],
                        entry["traveltime"]] for entry in data])

# ==== Balance Dataset ====
bins = [[] for _ in range(12)]
for row in data_array:
    idx = min(int(row[8] // 5), 11)
    bins[idx].append(row)

smallest = min(len(bin) for bin in bins if bin) # find the smallest time range bin 
balanced_data = [bin[:smallest] for bin in bins if len(bin) >= smallest] # take the 'smallest' amount of data from each bin to balace
data_array_bal = np.vstack(balanced_data)

# ==== Feature/Target Split ====
X, Y = data_array[:, :-1], data_array[:, -1]
Xs, Ys = data_array_bal[:, :-1], data_array_bal[:, -1]

# ==== Train/Val/Test Split ====
def split_data(X, Y):
    X_temp, X_test, y_temp, y_test = train_test_split(X, Y, test_size=0.2, random_state=42) # 80% Train/Val + 20% Testing
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42) # 60% train + 20 % Val
    return X_train, X_val, X_test, y_train, y_val, y_test

X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, Y)
Xs_train, Xs_val, Xs_test, ys_train, ys_val, ys_test = split_data(Xs, Ys)

def tune_model(X_train, y_train, X_val, y_val):
    best_model = None
    best_score = float("inf")
    best_params = None

    print(" Tuning Random Forest on validation set...\n")
    print(f"{'n_estimators':<15} {'max_depth':<10} {'MAE':<10} {'MSE':<12} {'RMSE':<10} {'R²':<10}")
    print("-" * 65)

    for n_estimators in [50, 100, 150]:
        for max_depth in [5, 10, 20, None]:
            model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
            model.fit(X_train, y_train)
            preds = model.predict(X_val)

            # Calculate metrics
            mae = mean_absolute_error(y_val, preds)
            mse = mean_squared_error(y_val, preds)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_val, preds)

            print(f"{n_estimators:<15} {str(max_depth):<10} {mae:<10.2f} {mse:<12.2f} {rmse:<10.2f} {r2:<10.2f}")

            if mae < best_score:
                best_score = mae
                best_model = model
                best_params = (n_estimators, max_depth)

    print(f"\n Best model: n_estimators={best_params[0]}, max_depth={best_params[1]}, MAE={best_score:.2f}\n")
    return best_model


# Tune both models
model_best = tune_model(X_train, y_train, X_val, y_val)
model_bal_best = tune_model(Xs_train, ys_train, Xs_val, ys_val)

# ==== Final Test Evaluation ====
def eval_model(y_true, y_pred):
    return [
        mean_absolute_error(y_true, y_pred),
        mean_squared_error(y_true, y_pred),
        np.sqrt(mean_squared_error(y_true, y_pred)),
        r2_score(y_true, y_pred)
    ]

test_orig = eval_model(y_test, model_best.predict(X_test))
test_bal = eval_model(ys_test, model_bal_best.predict(Xs_test))

# ==== Save Best Models ====
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Models"))
os.makedirs(MODEL_DIR, exist_ok=True)

with open(os.path.join(MODEL_DIR, "travel_time_model.pkl"), "wb") as f:
    pickle.dump(model_best, f)

with open(os.path.join(MODEL_DIR, "travel_time_model_balanced.pkl"), "wb") as f:
    pickle.dump(model_bal_best, f)

# ==== Print Final Test Metrics ====
metrics_df = pd.DataFrame({
    "Metric": ["MAE", "MSE", "RMSE", "R²"],
    "Test (Original)": test_orig,
    "Test (Balanced)": test_bal
})
print("\n Final Test Set Performance:")
print(metrics_df.to_string(index=False))

# ==== Prediction on Custom Input ====
custom_input = np.array([[10.00, 3, 0.0, 0.0,  43.6565, -79.3807,  43.68611, -79.61972]])
pred_orig = model_best.predict(custom_input)[0]
pred_bal = model_bal_best.predict(custom_input)[0]

print(f"\n Estimated Travel Time from Dundas to Pearson:")
print(f"   Original model: {pred_orig:.2f} minutes")
print(f"   Balanced model: {pred_bal:.2f} minutes")

# ==== Plot Actual vs Predicted ====
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.scatter(y_test, model_best.predict(X_test), alpha=0.5)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], 'r--', label="Ideal")
plt.title("Original Model (Best Tuned)")
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted")
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(ys_test, model_bal_best.predict(Xs_test), alpha=0.5, color="orange")
plt.plot([min(ys_test), max(ys_test)], [min(ys_test), max(ys_test)], 'r--', label="Ideal")
plt.title("Balanced Model (Best Tuned)")
plt.xlabel("Actual Travel Time")
plt.ylabel("Predicted")
plt.legend()

plt.suptitle("Test Set: Actual vs Predicted Travel Time (Best Models)")
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
