from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import joblib
import os
import io
from sqlalchemy import text
from fpdf import FPDF
from datetime import datetime

from .database import get_db_connection, DB_PATH, COST_MODEL_PATH, CO2_MODEL_PATH, BASE_DIR, init_db, load_data_to_db

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'), 
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

@app.route('/')
@app.route('/index.html')
def index():
    return send_file(os.path.join(BASE_DIR, 'templates', 'index.html'))

@app.route('/dashboard')
@app.route('/dashboard.html')
def dashboard():
    return send_file(os.path.join(BASE_DIR, 'templates', 'dashboard.html'))

# Global models
cost_model = None
co2_model = None

def load_resources():
    global cost_model, co2_model
    if os.path.exists(COST_MODEL_PATH):
        cost_model = joblib.load(COST_MODEL_PATH)
    if os.path.exists(CO2_MODEL_PATH):
        co2_model = joblib.load(CO2_MODEL_PATH)

# Load model resources when the app module is imported by Gunicorn
load_resources()


def ensure_database_ready():
    """Create missing tables and seed the materials table if needed."""
    init_db()

    try:
        conn = get_db_connection()
        materials_count = conn.execute(text("SELECT COUNT(*) FROM materials")).scalar()
        conn.close()
    except Exception as e:
        print(f"Database readiness check failed: {e}")
        materials_count = 0

    if not materials_count:
        load_data_to_db()


ensure_database_ready()

def get_materials_from_db():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM materials", conn)
    conn.close()
    return df

@app.route('/api/materials', methods=['GET'])
def get_materials():
    try:
        df = get_materials_from_db()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    weight = data.get('weight_kg', 1)
    durability = data.get('durability_needed', 5)
    industry = data.get('industry', 'General')
    product_name = data.get('product_name', 'Unnamed Product')
    
    try:
        materials_df = get_materials_from_db()
    except Exception as e:
        return jsonify({"error": "Failed to load materials from database"}), 500
    
    filtered_df = materials_df.copy()
    if industry != 'General':
        filtered_df['industry_match'] = filtered_df['industry'].str.lower().apply(lambda x: 3 if x == industry.lower() else 1)
    else:
        filtered_df['industry_match'] = 1
        
    filtered_df['weight_fit'] = (filtered_df['weight_capacity'] >= weight).astype(int) * 4
    filtered_df['durability_fit'] = (filtered_df['durability'] >= durability).astype(int) * 4
    
    filtered_df['final_rank'] = (
        filtered_df['industry_match'] + 
        filtered_df['weight_fit'] + 
        filtered_df['durability_fit'] + 
        filtered_df['suitability_score'] / 10.0
    )
    
    recommendations = filtered_df.sort_values(by='final_rank', ascending=False)
    recommendations = recommendations.groupby('material').head(1).head(5)
    
    # Log request to database
    if not recommendations.empty:
        best_id = int(recommendations.iloc[0]['id']) if 'id' in recommendations.columns else None
        try:
            query = text(
                "INSERT INTO product_requests (product_name, category, weight_kg, recommended_material_id) "
                "VALUES (:product_name, :category, :weight_kg, :recommended_material_id)"
            )
            with get_db_connection() as conn:
                conn.execute(query, {
                    'product_name': product_name,
                    'category': industry,
                    'weight_kg': weight,
                    'recommended_material_id': best_id
                })
                conn.commit()
        except Exception as e:
            print(f"Failed to log request: {e}")

    return jsonify({
        "status": "success",
        "recommendations": recommendations.to_dict(orient='records')
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        materials_df = get_materials_from_db()
        conn = get_db_connection()
        requests_df = pd.read_sql_query("SELECT * FROM product_requests", conn)
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
    # Existing Metrics
    avg_co2 = materials_df.groupby('material')['co2_emission'].mean().round(2).to_dict()
    avg_co2 = dict(sorted(avg_co2.items(), key=lambda x: x[1])[:5])

    avg_cost = materials_df.groupby('industry')['cost'].mean().round(2).to_dict()
    avg_cost = dict(sorted(avg_cost.items(), key=lambda x: x[1])[:5])
    
    total_avg_cost = round(materials_df['cost'].mean(), 2)
    baseline_co2 = 500
    current_avg_co2 = materials_df['co2_emission'].mean()
    co2_reduction = round(((baseline_co2 - current_avg_co2) / baseline_co2) * 100, 1)

    # New BI Metrics
    # Cost Savings: Assuming a baseline material cost of $50
    baseline_cost = 50.0
    cost_savings = round(((baseline_cost - total_avg_cost) / baseline_cost) * 100, 1)

    # Material Usage Trends (from product_requests)
    if not requests_df.empty:
        requests_df['request_date'] = pd.to_datetime(requests_df['request_date'])
        trends = requests_df.groupby(requests_df['request_date'].dt.date).size().to_dict()
        # Convert keys to strings
        trends = {str(k): v for k, v in trends.items()}
    else:
        # Mock trend data if empty
        trends = {str(datetime.now().date()): 5, "2024-03-25": 3, "2024-03-24": 8}

    return jsonify({
        "avg_co2_by_type": avg_co2,
        "avg_cost_by_industry": avg_cost,
        "total_materials": len(materials_df),
        "total_avg_cost": total_avg_cost,
        "co2_reduction": co2_reduction,
        "cost_savings": cost_savings,
        "usage_trends": trends
    })

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    try:
        df = get_materials_from_db()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Materials')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='Sustainability_Report.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    try:
        df = get_materials_from_db()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "EcoPackAI Sustainability Report", 0, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Table Header
        pdf.set_font("Arial", 'B', 10)
        cols = ['material', 'industry', 'co2_emission', 'cost', 'suitability_score']
        for col in cols:
            pdf.cell(38, 10, col.replace('_', ' ').title(), 1)
        pdf.ln()

        # Table Rows (Top 20)
        pdf.set_font("Arial", '', 9)
        for _, row in df.head(20).iterrows():
            for col in cols:
                pdf.cell(38, 10, str(row[col])[:18], 1)
            pdf.ln()

        pdf_output = pdf.output(dest='S')
        return send_file(io.BytesIO(pdf_output), as_attachment=True, download_name='Sustainability_Report.pdf', mimetype='application/pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_resources()
    from .database import init_db, load_data_to_db
    is_postgres = os.environ.get('DATABASE_URL') is not None
    if not is_postgres:
        if not os.path.exists(DB_PATH):
            init_db()
            load_data_to_db()
    else:
        # For cloud, we might want to init db every time or handle differently
        init_db()
    
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
