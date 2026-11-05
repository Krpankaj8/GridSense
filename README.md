# GridSense – Formula 1 Race Intelligence

**GridSense** is a machine learning-powered web application designed to explore Formula 1 race performance and predict a driver's finishing position and probability of achieving a podium finish.

The project uses historical Formula 1 racing data to train predictive models and presents their results through an interactive web interface.

## About the Project

Formula 1 race results depend on several factors, including starting grid position, driver performance and constructor performance.

GridSense uses historical race data to build machine learning models that estimate race outcomes. Users can select a driver, constructor, circuit and starting grid position to generate predictions.

The main objective is to combine data analysis, machine learning and web development in one practical application.

## Features

- **Finishing Position Prediction:** Estimates a driver's finishing position using Linear Regression.
- **Podium Probability:** Uses Logistic Regression to estimate the probability of a top-three finish.
- **Interactive Prediction Interface:** Allows users to provide race-related inputs and view predictions.
- **Visual Results:** Displays prediction results through charts generated using Matplotlib.
- **Model Evaluation:** Presents available regression and classification evaluation metrics.
- **Historical F1 Data:** Uses multiple datasets containing information about drivers, constructors, circuits, races and results.
- **Responsive Interface:** Provides a web interface built using HTML, CSS and JavaScript.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Data Visualization | Matplotlib |
| Frontend | HTML, CSS, JavaScript |
| Dataset | Historical Formula 1 CSV datasets |

## Machine Learning Approach

GridSense currently uses two machine learning algorithms.

### 1. Linear Regression

Linear Regression is used to estimate the driver's finishing position.

The model uses available historical performance information, including grid position, driver points and constructor-related features.

### 2. Logistic Regression

Logistic Regression is used to estimate the probability of a driver finishing in the top three positions.

The output represents the model's estimated podium probability, not a guaranteed race result.

### Model Evaluation

The application retrieves available evaluation metrics from its backend.

**Regression metrics**
- Root Mean Squared Error (RMSE)
- R-squared (R²)

**Classification metrics**
- Accuracy
- Precision
- Recall

Metrics that are not currently calculated by the backend are not presented as measured results.

## Dataset

The project uses historical Formula 1 datasets stored locally in the `data/` directory.

The datasets contain information about:

- Drivers
- Constructors
- Circuits
- Race schedules and results
- Driver standings
- Constructor standings
- Qualifying results
- Lap times
- Pit stops
- Sprint results

Keeping the datasets locally available allows the application to load historical records without depending on a live external data API.

## Project Structure

```text
GridSense/
│
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
│
├── data/
│   ├── circuits.csv
│   ├── constructors.csv
│   ├── drivers.csv
│   ├── races.csv
│   ├── results.csv
│   ├── lap_times.csv
│   ├── pit_stops.csv
│   └── ...
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Installation and Setup

Follow these steps to run GridSense on your local machine.

### Prerequisites

- Python 3.10 or later
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Krpankaj8/GridSense.git
cd GridSense
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open GridSense

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Use the port displayed in your terminal if your application is configured to run on a different port.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Loads the main application interface |
| GET | `/metrics` | Retrieves available model evaluation metrics |
| POST | `/predict` | Generates finishing position and podium probability predictions |

## Future Improvements

Some areas that can be explored in future versions include:

- Additional machine learning algorithms.
- More comprehensive driver performance analysis.
- Constructor and circuit performance comparisons.
- Historical race trend visualizations.
- Improved model evaluation and validation.
- More advanced race outcome prediction features.

## Project Purpose

GridSense was developed as a practical project to apply concepts from Python programming, data preprocessing, machine learning, data visualization and Flask-based web development.

It demonstrates how historical sports data can be transformed into an interactive predictive analytics application.

## Repository

**GitHub:** https://github.com/Krpankaj8/GridSense

---

*GridSense – Turning Formula 1 historical data into race insights.*
