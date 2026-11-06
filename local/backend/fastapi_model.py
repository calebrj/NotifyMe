from fastapi import FastAPI
import pickle
import numpy as np

app = FastAPI()

with open("Models/travel_time_model_balanced.pkl", "rb") as f:
    model = pickle.load(f)

@app.post("/predict")
def predict(data: dict):
    features = np.array(data["features"]).reshape(1, -1)
    prediction = model.predict(features).tolist()
    return {"prediction": prediction}

