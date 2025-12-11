import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import joblib

MODEL_PATH = "data/cpu_forecast_model.pkl"

def train_forecast_model(csv_path="data/history.csv"):
    df = pd.read_csv(csv_path)

    if len(df) < 30:
        raise Exception("Not enough data to train CPU forecast model")

    df["cpu_next"] = df["cpu"].shift(-1)
    df = df.dropna()

    X = df[["cpu", "memory"]]
    y = df["cpu_next"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LinearRegression()
    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)

    return model, model.score(X_test, y_test)
    def load_forecast_model():
    try:
        return joblib.load(MODEL_PATH)
    except:
        return None


def predict_future_cpu(model, current_cpu, current_mem):
    if model is None:
        return None

    prediction = model.predict([[current_cpu, current_mem]])
    return round(float(prediction[0]), 2)

