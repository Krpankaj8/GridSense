import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score
from flask import Flask, render_template, request, jsonify
import os
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI rendering
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Global variables
linear_model = None
logistic_model = None
scaler = None
df = None
drivers = None
constructors = None
circuits = None

# Function to load and preprocess data
def load_and_preprocess_data(data_dir='data'):
    try:
        results = pd.read_csv(os.path.join(data_dir, 'results.csv'))
        drivers = pd.read_csv(os.path.join(data_dir, 'drivers.csv'))
        races = pd.read_csv(os.path.join(data_dir, 'races.csv'))
        constructors = pd.read_csv(os.path.join(data_dir, 'constructors.csv'))
        circuits = pd.read_csv(os.path.join(data_dir, 'circuits.csv'))
        
        df = results.merge(races[['raceId', 'year', 'circuitId']], on='raceId', how='left')
        df = df.merge(drivers[['driverId', 'driverRef']], on='driverId', how='left')
        df = df.merge(constructors[['constructorId', 'name']], on='constructorId', how='left')
        
        df = df[['raceId', 'driverId', 'constructorId', 'circuitId', 'grid', 'positionOrder', 'points', 'year', 'name']]
        df['grid'] = df['grid'].replace(0, df['grid'].median())
        df = df.dropna(subset=['positionOrder'])
        
        df['historical_points'] = df.groupby('driverId')['points'].cumsum() - df['points']
        df = pd.get_dummies(df, columns=['constructorId'], prefix='constructor')
        df['podium'] = (df['positionOrder'] <= 3).astype(int)
        
        return df, drivers[['driverId', 'driverRef', 'forename', 'surname']], constructors[['constructorId', 'name']], circuits[['circuitId', 'name']]
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}. Ensure 'results.csv', 'drivers.csv', 'races.csv', 'constructors.csv', 'circuits.csv' are in '{data_dir}'.")
        raise

# Function to train models
def train_models(df):
    features = ['grid', 'historical_points'] + [col for col in df.columns if col.startswith('constructor_')]
    X = df[features]
    y_reg = df['positionOrder']
    y_clf = df['podium']
    
    scaler = StandardScaler()
    X_scaled = X.copy()
    X_scaled[['grid', 'historical_points']] = scaler.fit_transform(X[['grid', 'historical_points']])
    
    X_train, X_test, y_train_reg, y_test_reg = train_test_split(X_scaled, y_reg, test_size=0.2, random_state=42)
    X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(X_scaled, y_clf, test_size=0.2, random_state=42)
    
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train_reg)
    
    y_pred_reg = linear_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
    r2 = r2_score(y_test_reg, y_pred_reg)
    print(f"Linear Regression - RMSE: {rmse:.2f}, R²: {r2:.2f}")
    
    logistic_model = LogisticRegression(max_iter=2000, class_weight='balanced')
    logistic_model.fit(X_train_clf, y_train_clf)
    
    y_pred_clf = logistic_model.predict(X_test_clf)
    accuracy = accuracy_score(y_test_clf, y_pred_clf)
    precision = precision_score(y_test_clf, y_pred_clf)
    recall = recall_score(y_test_clf, y_pred_clf)
    print(f"Logistic Regression - Accuracy: {accuracy:.2f}, Precision: {precision:.2f}, Recall: {recall:.2f}")
    
    return linear_model, logistic_model, scaler

# Initialize data and models
try:
    df, drivers, constructors, circuits = load_and_preprocess_data()
    linear_model, logistic_model, scaler = train_models(df)
except Exception as e:
    print(f"Startup error: {e}")
    exit(1)

@app.route('/')
def index():
    driver_options = drivers[['driverRef', 'forename', 'surname']].to_dict('records')
    return render_template('index.html', 
                         driver_options=driver_options, 
                         constructors=constructors['name'].tolist(),
                         circuits=circuits['name'].tolist(),
                         latest_season=int(df['year'].max()))

@app.route('/metrics')
def metrics():
    features = ['grid', 'historical_points'] + [col for col in df.columns if col.startswith('constructor_')]
    X = df[features].copy()
    X[['grid', 'historical_points']] = scaler.transform(X[['grid', 'historical_points']])
    y_reg = df['positionOrder']
    y_clf = df['podium']
    
    X_train, X_test, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    y_pred_reg = linear_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
    r2 = r2_score(y_test_reg, y_pred_reg)
    
    X_train, X_test, y_train_clf, y_test_clf = train_test_split(X, y_clf, test_size=0.2, random_state=42)
    y_pred_clf = logistic_model.predict(X_test)
    accuracy = accuracy_score(y_test_clf, y_pred_clf)
    precision = precision_score(y_test_clf, y_pred_clf)
    recall = recall_score(y_test_clf, y_pred_clf)
    
    return jsonify({
        'rmse': round(rmse, 2),
        'r2': round(r2, 2),
        'accuracy': round(accuracy, 2),
        'precision': round(precision, 2),
        'recall': round(recall, 2)
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        driver = request.form.get('driver', '').strip()
        constructor = request.form.get('constructor', '').strip()
        circuit = request.form.get('circuit', '').strip()
        grid_value = request.form.get('grid', '').strip()

        if not drivers['driverRef'].eq(driver).any():
            return jsonify({'error': 'Select a driver from the available list.'}), 400
        if not constructors['name'].eq(constructor).any():
            return jsonify({'error': 'Select a constructor from the available list.'}), 400
        if not circuits['name'].eq(circuit).any():
            return jsonify({'error': 'Select a circuit from the available list.'}), 400
        try:
            grid = int(grid_value)
        except ValueError:
            return jsonify({'error': 'Starting grid position must be a whole number between 1 and 22.'}), 400
        if not 1 <= grid <= 22:
            return jsonify({'error': 'Starting grid position must be between 1 and 22.'}), 400
        
        driver_id = drivers[drivers['driverRef'] == driver]['driverId'].iloc[0]
        constructor_id = constructors[constructors['name'] == constructor]['constructorId'].iloc[0]
        
        historical_points = df[df['driverId'] == driver_id]['historical_points'].mean()
        
        input_data = pd.DataFrame({
            'grid': [grid],
            'historical_points': [historical_points]
        })
        
        # Use only constructor columns present in training data
        trained_constructor_cols = [col for col in df.columns if col.startswith('constructor_')]
        constructor_df = pd.DataFrame(0, index=input_data.index, columns=trained_constructor_cols)
        if f'constructor_{constructor_id}' in trained_constructor_cols:
            constructor_df[f'constructor_{constructor_id}'] = 1
        input_data = pd.concat([input_data, constructor_df], axis=1)
        
        input_data_scaled = input_data.copy()
        input_data_scaled[['grid', 'historical_points']] = scaler.transform(input_data[['grid', 'historical_points']])
        
        position_pred = linear_model.predict(input_data_scaled)[0]
        podium_prob = logistic_model.predict_proba(input_data_scaled)[0][1]
        
        # Keep position and probability on separate scales so neither is misleading.
        fig, (position_ax, probability_ax) = plt.subplots(1, 2, figsize=(9, 3.8))
        background = '#17191c'
        text_color = '#e8e9eb'
        muted_color = '#a4a8ae'
        grid_color = '#35383d'

        position_ax.barh(['Finish estimate'], [position_pred], color='#e10600', height=0.42)
        position_ax.set_xlim(0, max(22, np.ceil(position_pred) + 1))
        position_ax.set_title('Predicted finishing position', color=text_color, loc='left', pad=12)
        position_ax.set_xlabel('Position · lower is better', color=muted_color)
        position_ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        position_ax.text(position_pred, 0, f'  {position_pred:.2f}', va='center', color=text_color)

        podium_percent = podium_prob * 100
        probability_ax.barh(['Podium chance'], [podium_percent], color='#d7d9dc', height=0.42)
        probability_ax.set_xlim(0, 100)
        probability_ax.set_title('Podium probability', color=text_color, loc='left', pad=12)
        probability_ax.set_xlabel('Probability (%)', color=muted_color)
        probability_ax.set_xticks([0, 25, 50, 75, 100])
        probability_ax.text(min(podium_percent + 2, 86), 0, f'{podium_percent:.1f}%', va='center', color=text_color)

        for axis in (position_ax, probability_ax):
            axis.set_facecolor(background)
            axis.tick_params(colors=muted_color, length=0)
            axis.set_axisbelow(True)
            axis.grid(axis='x', color=grid_color, linewidth=0.7)
            for spine in axis.spines.values():
                spine.set_visible(False)

        fig.set_facecolor(background)
        fig.tight_layout(pad=2)

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=background, dpi=160)
        buf.seek(0)
        chart_image = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        
        return jsonify({
            'position': round(position_pred, 2),
            'podium_prob': round(podium_prob * 100, 2),
            'chart': chart_image,
            'driver': driver
        })
    except Exception as e:
        print(f"Predict error: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)