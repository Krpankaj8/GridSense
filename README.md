# GridSense — Formula 1 Race Intelligence

A Flask application that estimates a driver's finishing position and podium probability from historical Formula 1 data. The interface presents the prediction workflow, model evaluation metrics, and clearly marked planned analytics modules.

---

## 📸 Overview

The app uses two ML models trained on historical F1 race data:

- **Linear Regression** — Predicts the finishing position based on grid position, historical performance, and constructor.
- **Logistic Regression** — Predicts the probability of a podium finish (top 3).

Users select a driver, constructor, circuit, and starting grid position, then receive an instant prediction with a visual chart.

---

## Features

- **Race position estimate** — Linear regression using grid position, historical driver points, and constructor.
- **Podium probability** — Logistic regression estimates the probability of a top-three finish.
- **Prediction visualization** — Matplotlib chart presents position and probability on separate, labeled scales.
- **Model performance** — The interface fetches regression RMSE/R² and classification accuracy/precision/recall from `/metrics`. MAE, F1-score, and ROC-AUC are identified as not calculated by the current backend.
- **Dataset context** — The dashboard identifies the latest season present in the loaded results data.
- **Planned analytics** — Driver, constructor, and circuit analytics are explicitly marked as planned rather than represented with placeholder data.

The circuit selection is included in the prediction summary, but is not currently used as a model feature. The backend does not currently accept season or race selection.

---

## 🛠️ Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python, Flask                       |
| ML Models   | scikit-learn (Linear & Logistic Regression) |
| Data        | pandas, NumPy                       |
| Charting    | Matplotlib                          |
| Frontend    | HTML, CSS, vanilla JavaScript       |
| Typography  | System sans-serif stack             |

---

## 📁 Project Structure

```
Formula-1---Podium-Position-Predictor/
├── app.py                  # Flask app with ML model training & API routes
├── requirements.txt        # Python dependencies
├── data/                   # F1 historical datasets (CSV)
│   ├── circuits.csv
│   ├── constructors.csv
│   ├── drivers.csv
│   ├── races.csv
│   ├── results.csv
│   └── ...                 # Additional F1 data files
├── templates/
│   └── index.html          # Main web page (Jinja2 template)
├── static/
│   ├── css/
│   │   └── style.css       # GridSense design system and responsive layout
│   ├── js/
│   │   └── app.js          # Prediction form and metrics interactions
│   └── images/
│       └── backgroundf1.jpg
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/prakhar-sonii/Formula-1---Podium-Position-Predictor.git
   cd Formula-1---Podium-Position-Predictor
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python app.py
   ```

5. **Open in browser**

   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Model Performance

The dashboard loads evaluation values at runtime from `/metrics`; it does not hard-code scores. The current endpoint returns RMSE, R², accuracy, precision, and recall. Other requested metrics remain unavailable until they are added to the backend evaluation.

---

## 🔌 API Endpoints

| Method | Endpoint    | Description                          |
|--------|-------------|--------------------------------------|
| GET    | `/`         | Main prediction page                 |
| GET    | `/metrics`  | Returns model evaluation metrics (JSON) |
| POST   | `/predict`  | Returns predicted position & podium probability (JSON) |

---

## 📝 How It Works

1. **Data Loading** — Reads F1 datasets (results, drivers, races, constructors, circuits) from `data/`.
2. **Preprocessing** — Merges tables, engineers features (historical points, constructor one-hot encoding, podium flag).
3. **Model Training** — Fits Linear Regression (position prediction) and Logistic Regression (podium classification) with `StandardScaler` normalization.
4. **Prediction** — Accepts user input via the web form, transforms it with the trained scaler, and runs it through both models.
5. **Visualization** — Generates a Matplotlib chart with independent scales for predicted position and podium probability. Circuit selection is currently contextual and does not affect the model output.

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🙏 Acknowledgments

- [Ergast Developer API](http://ergast.com/mrd/) — Source of F1 historical data
