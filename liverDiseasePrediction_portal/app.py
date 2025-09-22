from flask import Flask, request, render_template, jsonify
import pandas as pd
import joblib
from sklearn.base import BaseEstimator, TransformerMixin

app = Flask(__name__)

class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        X = X.copy()
        X["BMI_Age_Ratio"] = X["BMI"] / (X["Age"] + 1)
        X["HeavyDrinker"] = (X["AlcoholConsumption"] > 14).astype(int)
        X["Risk_Smoke_Alcohol"] = X["Smoking"] * X["AlcoholConsumption"]
        return X

MODEL_PATH = "best_liver_model_joblib.pkl"
pipeline = joblib.load(MODEL_PATH)

FEATURE_COLS = [
    "Age", "Gender", "BMI", "AlcoholConsumption", "Smoking",
    "GeneticRisk", "PhysicalActivity", "Diabetes", "Hypertension",
    "LiverFunctionTest"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_manual', methods=['POST'])
def predict_manual():
    try:
        input_data = {}
        for col in FEATURE_COLS:
            value = request.form.get(col)
            if value is None or value.strip() == '':
                return jsonify({"error": f"Missing input for {col}"}), 400
            input_data[col] = [float(value)]

        X = pd.DataFrame(input_data)
        prediction = int(pipeline.predict(X)[0])

        return jsonify({"prediction": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
