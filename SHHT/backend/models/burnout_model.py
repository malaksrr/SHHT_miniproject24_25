import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Get base project root (SHHT folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Define paths from project root
DATA_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'burnout_data.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'backend', 'models', 'burnout_predictor.pkl')

def train_burnout_model():
    """Train and save the burnout prediction model (regression version)"""
    try:
        # Load data
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        df = pd.read_csv(DATA_PATH)
        
        # Verify required columns exist
        required_cols = ['study_hours', 'sleep_hours', 'break_frequency', 'concentration_level', 'burnout_risk']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("CSV is missing required columns")
            
        # Prepare features and target
        X = df[["study_hours", "sleep_hours", "break_frequency", "concentration_level"]]
        y = df["burnout_risk"]  # Now this is a continuous value
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train regression model
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        print("\nModel Evaluation:")
        print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.2f}")
        print(f"R2 Score: {r2_score(y_test, y_pred):.2f}")
        
        # Save model
        joblib.dump(model, MODEL_PATH)
        print(f"\nModel saved to {MODEL_PATH}")
        
        return model
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise

def load_burnout_model():
    """Load the pre-trained model with error handling"""
    try:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def predict_burnout(input_data):
    """Make predictions with input validation (pure regression version)"""
    try:
        model = load_burnout_model()
        
        # Validate input
        required_fields = ['study_hours', 'sleep_hours', 'break_frequency', 'concentration_level']
        if not all(field in input_data for field in required_fields):
            raise ValueError("Missing required input fields")
            
        # Prepare input
        input_df = pd.DataFrame([{
            'study_hours': float(input_data['study_hours']),
            'sleep_hours': float(input_data['sleep_hours']),
            'break_frequency': int(input_data['break_frequency']),
            'concentration_level': int(input_data['concentration_level'])
        }])
        
        # Predict
        risk_score = model.predict(input_df)[0]
        
        return {
            "risk_score": float(risk_score),  # The continuous prediction (0-100)
            "model_version": "2.1"  # Pure regression version
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return {
            "error": str(e),
            "risk_score": None
        }

if __name__ == "__main__":
    print("Training new burnout prediction model (regression version)...")
    trained_model = train_burnout_model()
    
    # Test prediction
    test_data = {
        'study_hours': 12,
        'sleep_hours': 4,
        'break_frequency': 10,
        'concentration_level': 1
    }
    print("\nTest Prediction:", predict_burnout(test_data))