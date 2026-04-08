# EcoPackAI - Technical Documentation

## Overview
EcoPackAI is a data-driven sustainability platform that recommends eco-friendly packaging materials. The system integrates machine learning models for predictive analytics and a business intelligence (BI) dashboard for real-time sustainability monitoring.

## 1. Analytics & BI Dashboard
The BI dashboard provides deep insights into the environmental and economic impact of material choices.

### Key Metrics
- **CO₂ Reduction %**: Calculated by comparing current material footprints against a standardized baseline (500kg).
- **Cost Savings %**: Measured by comparing the average material cost to a baseline cost ($50).
- **Material Usage Trends**: Historical visualization of material recommendations over time, powered by Plotly.js for interactive time-series analysis.
- **Emission & Cost Distribution**: High-resolution charts (Bar & Pie) showing averages across material categories and industries.

### Export Functionality
- **Excel Export**: Uses `Pandas` and `Openpyxl` to generate formatted material reports.
- **PDF Report**: Uses `fpdf2` to create detailed sustainability summaries with material scores and metrics.

## 2. Deployment on Render/Heroku
The project is configured for cloud deployment with a production-ready architecture.

### Database Migration
- **PostgreSQL Integration**: The backend automatically detects the `DATABASE_URL` environment variable for cloud databases (like Render PostgreSQL).
- **SQLite Support**: Falls back to SQLite for local development for ease of use.

### Procfile & Environment
- **Web Server**: Uses `Gunicorn` as a high-performance HTTP server.
- **Procfile**: `web: gunicorn --chdir backend app:app` ensures the application starts correctly on cloud platforms.
- **Requirements**: Optimized dependency list for production environments.

## 3. Data Flow & Intelligence
1. **User Requirement Input**: Users specify product name, industry, weight, and durability needs.
2. **AI Recommendation**: The system ranks materials using a multi-factor suitability score (Industry Match + Strength Fit + Eco Score).
3. **Database Logging**: Every recommendation is logged into `product_requests` for historical trend analysis.
4. **Analytics Pipeline**: The BI engine aggregates data from `materials` and `product_requests` to update live dashboard metrics.

## 4. Maintenance & Support
- **Adding Materials**: New materials can be added via the database schema or by updating the core CSV dataset and re-training.
- **Dashboard Refresh**: The dashboard employs an automated 60-second polling mechanism to ensure data is synchronized with the latest requests.
