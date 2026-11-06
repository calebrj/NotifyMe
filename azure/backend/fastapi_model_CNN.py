from fastapi import FastAPI
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler  # ✅ you can keep this!
from tensorflow.keras.models import load_model

app = FastAPI()

# Load model
model = load_model("Models/BalancedCNNModel.h5", compile=False)

#  Load fitted scaler (trained on training data)
with open("Models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

@app.post("/predict_cnn")
def predict(data: dict):
    features = np.array(data["features"]).reshape(1, -1)
    features = scaler.transform(features)         # Apply trained scaling
    features = features.reshape(1, 8, 1)           # Reshape for CNN input
    prediction = model.predict(features)          # Predict
    return {"prediction": float(prediction[0][0])}
