from flask import Flask, request, render_template, jsonify
import numpy as np
import pickle

# Initialize Flask app
app = Flask(__name__)

# Load models and scalers
try:
    model = pickle.load(open('models/model.pkl', 'rb'))
    sc = pickle.load(open('scalars/standscaler.pkl', 'rb'))
    mx = pickle.load(open('scalars/minmaxscaler.pkl', 'rb'))
    models_loaded = True
except Exception as e:
    print(f"Error loading models: {e}")
    models_loaded = False

# Crop dictionary
crop_dict = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 
    6: "Papaya", 7: "Orange", 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 
    11: "Grapes", 12: "Mango", 13: "Banana", 14: "Pomegranate", 15: "Lentil", 
    16: "Blackgram", 17: "Mungbean", 18: "Mothbeans", 19: "Pigeonpeas", 
    20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    if not models_loaded:
        return jsonify({'success': False, 'errors': {'general': 'Prediction models not available. Please try again later.'}}), 500

    errors = {}
    try:
        # Get form data
        N = request.form.get('Nitrogen', type=float)
        P = request.form.get('Phosporus', type=float)
        K = request.form.get('Potassium', type=float)
        temp = request.form.get('Temperature', type=float)
        humidity = request.form.get('Humidity', type=float)
        ph = request.form.get('pH', type=float)
        rainfall = request.form.get('Rainfall', type=float)

        # Check for missing fields
        if N is None:
            errors['Nitrogen'] = "Nitrogen is required."
        if P is None:
            errors['Phosporus'] = "Phosphorus is required."
        if K is None:
            errors['Potassium'] = "Potassium is required."
        if temp is None:
            errors['Temperature'] = "Temperature is required."
        if humidity is None:
            errors['Humidity'] = "Humidity is required."
        if ph is None:
            errors['pH'] = "Soil pH is required."
        if rainfall is None:
            errors['Rainfall'] = "Rainfall is required."

        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        # Validate ranges
        if not (0 <= N <= 140): errors['Nitrogen'] = "Value must be between 0 and 140 ppm."
        if not (0 <= P <= 145): errors['Phosporus'] = "Value must be between 0 and 145 ppm."
        if not (0 <= K <= 205): errors['Potassium'] = "Value must be between 0 and 205 ppm."
        if not (-10 <= temp <= 50): errors['Temperature'] = "Value must be between -10 and 50 °C."
        if not (0 <= humidity <= 100): errors['Humidity'] = "Value must be between 0 and 100%."
        if not (0 <= ph <= 14): errors['pH'] = "Value must be between 0 and 14."
        if rainfall < 0: errors['Rainfall'] = "Value cannot be negative."

        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        # Prepare features for prediction
        feature_list = [N, P, K, temp, humidity, ph, rainfall]
        single_pred = np.array(feature_list).reshape(1, -1)

        # Apply transformations and predict
        mx_features = mx.transform(single_pred)
        sc_mx_features = sc.transform(mx_features)
        prediction = model.predict(sc_mx_features)

        # Get crop recommendation
        crop = crop_dict.get(int(prediction[0]))
        if crop:
            result = f"{crop} is the best crop to be cultivated with these conditions"
            return jsonify({'success': True, 'crop': crop, 'result': result, 'prediction_code': int(prediction[0])})
        else:
            return jsonify({'success': False, 'errors': {'general': 'Could not determine the best crop with the provided data.'}}), 400

    except ValueError:
        return jsonify({'success': False, 'errors': {'general': 'Invalid input format. Please enter numerical values.'}}), 400
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'success': False, 'errors': {'general': 'An error occurred during prediction. Please try again.'}}), 500

@app.route('/api/crops', methods=['GET'])
def get_crops():
    """Return list of available crops"""
    return jsonify({'crops': crop_dict, 'total_crops': len(crop_dict)})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy' if models_loaded else 'models_not_loaded', 'models_loaded': models_loaded})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'errors': {'general': 'Endpoint not found'}}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'errors': {'general': 'Internal server error'}}), 500

if __name__ == "__main__":
    if models_loaded:
        print("All models loaded successfully!")
    else:
        print("Warning: Models failed to load. The application may not work properly.")
    app.run(debug=True)
