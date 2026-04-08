# EcoPackAI – AI-Powered Sustainable Packaging Recommendation System

EcoPackAI is a comprehensive platform designed to help businesses transition to eco-friendly packaging materials using Machine Learning and Business Intelligence.

## Features
- **AI Recommendation Engine**: Ranks materials based on product requirements, sustainability scores, and industry standards.
- **Predictive Analytics**: Uses Random Forest and XGBoost to predict material costs and CO2 footprints.
- **BI Sustainability Dashboard**: Enhanced with Plotly.js to show CO₂ reduction, cost savings, and recommendation trends.
- **Sustainability Reports**: Export material analytics and sustainability metrics to PDF and Excel formats.
- **Data-Driven Insights**: Derived metrics like CO2 Impact Index and Cost Efficiency Score.

## Project Structure
- `app.py`: Flask API entry point.
- `database.py`: Database connection and initialization.
- `models/`: ML models (cost and CO2 prediction).
- `templates/`: HTML templates for the UI and dashboard.
- `static/`: Static assets (CSS, JS, images).
- `data/`: Raw and processed material datasets.
- `scripts/`: Data generation and training scripts.

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Data & Train Models
```bash
python scripts/generate_data.py
python scripts/train_models.py

```

### 3. Run the Backend & Dashboard
```bash
python app.py
```

### 4. Experience the Dashboard
- Navigate to the **Sustainability Dashboard** to view live analytics.
- Use the **Export Report** button to download sustainability insights.

## Deployment
The application is pre-configured for deployment on **Render** or **Heroku**:
1. Connect your repository to the platform.
2. Set up a **PostgreSQL** cloud instance (e.g., Render PostgreSQL).
3. Set the `DATABASE_URL` environment variable to your PostgreSQL connection string.
4. The `Procfile` and `runtime.txt` are already included for seamless deployment.

## Technologies Used
- **Backend**: Python (Flask, Pandas, FPDF, Openpyxl)
- **Machine Learning**: Scikit-Learn, XGBoost, Joblib
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript (Plotly.js)
- **Database**: PostgreSQL (Production) / SQLite (Local)
- **Deployment**: Gunicorn, Render/Heroku support
