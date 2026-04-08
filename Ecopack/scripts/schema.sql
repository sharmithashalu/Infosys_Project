-- Database Schema for EcoPackAI

-- Create Materials Table
CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    material VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    strength INT,
    weight_capacity FLOAT,
    biodegradability INT,
    co2_emission FLOAT,
    recyclability INT,
    cost FLOAT,
    durability INT,
    industry VARCHAR(100),
    co2_impact_index FLOAT,
    cost_efficiency_index FLOAT,
    suitability_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Products Table (for historical recommendations or user input tracking)
CREATE TABLE IF NOT EXISTS product_requests (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    weight_kg FLOAT,
    fragility INT, -- 1 to 10
    shipping_distance_km FLOAT,
    recommended_material_id INT REFERENCES materials(id),
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
