from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load trained pipeline
pipeline = joblib.load('uploads/diabetes_model.pkl')
class_mapping = {0: 'Non-diabetic', 1: 'Diabetic', 2: 'Prediabetic'}
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocessing function to compute engineered features
def add_features(df):
    df = df.copy()
    df['TG_HDL'] = df['TG'] / df['HDL']
    df['LDL_HDL'] = df['LDL'] / df['HDL']
    df['Chol_HDL'] = df['Chol'] / df['HDL']
    df['Obese'] = (df['BMI'] >= 30).astype(int)
    df['High_HbA1c'] = (df['HbA1c'] >= 6.5).astype(int)
    df['Age_BMI'] = df['AGE'] * df['BMI']
    df['HbA1c_Chol'] = df['HbA1c'] * df['Chol']
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # CSV upload
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if not allowed_file(file.filename):
                return jsonify({"error": "Only CSV files allowed."}), 400
            data = pd.read_csv(file)
            data = add_features(data)

        # Manual entry
        else:
            data_dict = request.form.to_dict()
            # Convert all values to float for a single patient
            for k, v in data_dict.items():
                data_dict[k] = [float(v)]
            data = pd.DataFrame(data_dict)
            data = add_features(data)

        # Ensure feature order matches pipeline
        pipeline_features = pipeline.named_steps['scaler'].feature_names_in_
        missing_cols = [col for col in pipeline_features if col not in data.columns]
        if missing_cols:
            return jsonify({"error": f"Missing columns: {missing_cols}"}), 400

        X = data[pipeline_features]

        # Predict
        preds = pipeline.predict(X)
        data['Diagnosis_Result'] = [class_mapping[p] for p in preds]

        # Force response to only include raw features + Diagnosis_Result
        RAW_FEATURES = ['AGE','Urea','Cr','HbA1c','Chol','TG','HDL','LDL','VLDL','BMI']
        data_for_response = data[RAW_FEATURES + ['Diagnosis_Result']].round(2)

        # Build response
        response = []
        for _, row in data_for_response.iterrows():
            response.append(row.to_dict())

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
