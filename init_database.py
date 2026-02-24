#!/usr/bin/env python3
"""
Database initialization script for Fertilizer Recommendation System
"""

import sqlite3
import json
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent / "data" / "fertilizer_db.sqlite"

def create_database():
    """Create database and all tables"""
    
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database (creates it if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Creating database tables...")
    
    # Create Crops table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crops (
            crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL UNIQUE,
            nitrogen_requirement INTEGER,
            phosphorus_requirement INTEGER,
            potassium_requirement INTEGER,
            growth_stages TEXT,
            description TEXT
        )
    """)
    
    # Create Soils table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soils (
            soil_id INTEGER PRIMARY KEY AUTOINCREMENT,
            soil_type TEXT NOT NULL UNIQUE,
            ph_range TEXT,
            water_retention TEXT,
            characteristics TEXT,
            description TEXT
        )
    """)
    
    # Create Fertilizers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fertilizers (
            fertilizer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            nitrogen_content REAL,
            phosphorus_content REAL,
            potassium_content REAL,
            price_per_kg REAL,
            availability TEXT,
            application_notes TEXT
        )
    """)
    
    # Create Recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_id INTEGER,
            soil_id INTEGER,
            fertilizer_id INTEGER,
            application_rate_kg_per_acre REAL,
            application_timing TEXT,
            method TEXT,
            notes TEXT,
            FOREIGN KEY (crop_id) REFERENCES crops(crop_id),
            FOREIGN KEY (soil_id) REFERENCES soils(soil_id),
            FOREIGN KEY (fertilizer_id) REFERENCES fertilizers(fertilizer_id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Tables created successfully!")

def insert_sample_data():
    """Insert sample agricultural data"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📝 Inserting sample data...")
    
    # Sample crops
    crops = [
        ("Maize", 120, 60, 60, json.dumps({
            "planting": "Apply basal fertilizer at planting",
            "3-4_weeks": "Top dress with CAN at 3-4 weeks",
            "6-8_weeks": "Second top dressing before tasseling"
        }), "Main staple cereal crop requiring high nitrogen"),
        
        ("Beans", 30, 40, 40, json.dumps({
            "planting": "Apply phosphorus at planting",
            "flowering": "Minimal nitrogen needed"
        }), "Legume crop that fixes nitrogen"),
        
        ("Potatoes", 150, 80, 180, json.dumps({
            "planting": "Apply complete NPK at planting",
            "hilling": "Side dress during hilling",
            "tuber_formation": "High potassium needed"
        }), "High nutrient demanding tuber crop"),
        
        ("Tomatoes", 140, 60, 180, json.dumps({
            "transplanting": "Apply basal fertilizer before transplanting",
            "vegetative": "Top dress 2-3 weeks after transplanting",
            "flowering_fruiting": "Increase potassium during fruiting"
        }), "Requires balanced nutrition with potassium emphasis"),
        
        ("Wheat", 100, 50, 50, json.dumps({
            "planting": "Apply NPK at planting",
            "tillering": "Top dress during tillering"
        }), "Cereal crop requiring moderate nitrogen"),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO crops 
        (crop_name, nitrogen_requirement, phosphorus_requirement, 
         potassium_requirement, growth_stages, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, crops)
    
    # Sample soils
    soils = [
        ("Clay", "6.0-7.5", "High", json.dumps({
            "drainage": "Poor drainage, holds water",
            "nutrients": "Good nutrient retention",
            "workability": "Heavy when wet"
        }), "Heavy soil with poor drainage but good fertility"),
        
        ("Loam", "6.0-7.0", "Medium", json.dumps({
            "drainage": "Good drainage",
            "nutrients": "Excellent nutrient balance",
            "workability": "Easy to work with"
        }), "Ideal agricultural soil"),
        
        ("Sandy", "5.5-7.0", "Low", json.dumps({
            "drainage": "Excellent drainage",
            "nutrients": "Poor nutrient retention",
            "workability": "Very easy to work"
        }), "Light soil, needs frequent fertilization"),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO soils 
        (soil_type, ph_range, water_retention, characteristics, description)
        VALUES (?, ?, ?, ?, ?)
    """, soils)
    
    # Sample fertilizers
    fertilizers = [
        ("DAP 18:46:0", 18.0, 46.0, 0.0, 120.0, "Widely available", 
         "Best for basal application. High phosphorus content."),
        
        ("CAN 26:0:0", 26.0, 0.0, 0.0, 90.0, "Widely available", 
         "For top dressing. Quick nitrogen release."),
        
        ("NPK 17:17:17", 17.0, 17.0, 17.0, 110.0, "Widely available", 
         "Balanced fertilizer for most crops."),
        
        ("NPK 23:23:0", 23.0, 23.0, 0.0, 115.0, "Common", 
         "Good for cereals. No potassium."),
        
        ("Urea 46:0:0", 46.0, 0.0, 0.0, 85.0, "Very common", 
         "High nitrogen. Apply carefully to avoid burning."),
        
        ("TSP 0:46:0", 0.0, 46.0, 0.0, 100.0, "Available", 
         "Pure phosphorus source. Excellent for legumes."),
        
        ("Manure", 1.5, 1.0, 1.5, 20.0, "Locally available", 
         "Organic option. Improves soil structure. Apply well-rotted."),
        
        ("Compost", 2.0, 1.5, 2.0, 15.0, "Can be made on-farm", 
         "Organic fertilizer. Improves soil health."),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO fertilizers 
        (product_name, nitrogen_content, phosphorus_content, potassium_content,
         price_per_kg, availability, application_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, fertilizers)
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data inserted successfully!")

def verify_database():
    """Verify database contents"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📊 Database Verification:")
    print("=" * 50)
    
    # Check crops
    cursor.execute("SELECT COUNT(*) FROM crops")
    crops_count = cursor.fetchone()[0]
    cursor.execute("SELECT crop_name FROM crops")
    crop_names = [row[0] for row in cursor.fetchall()]
    print(f"\n🌾 Crops ({crops_count}):")
    for name in crop_names:
        print(f"   - {name}")
    
    # Check soils
    cursor.execute("SELECT COUNT(*) FROM soils")
    soils_count = cursor.fetchone()[0]
    cursor.execute("SELECT soil_type FROM soils")
    soil_types = [row[0] for row in cursor.fetchall()]
    print(f"\n🏞️  Soil Types ({soils_count}):")
    for soil in soil_types:
        print(f"   - {soil}")
    
    # Check fertilizers
    cursor.execute("SELECT COUNT(*) FROM fertilizers")
    fert_count = cursor.fetchone()[0]
    cursor.execute("SELECT product_name, price_per_kg FROM fertilizers")
    fertilizers = cursor.fetchall()
    print(f"\n💊 Fertilizers ({fert_count}):")
    for name, price in fertilizers:
        print(f"   - {name} (KES {price}/kg)")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Database is ready for use!")

def main():
    """Main execution function"""
    print("🚀 Initializing Fertilizer Recommendation Database")
    print("=" * 60)
    
    try:
        create_database()
        insert_sample_data()
        verify_database()
        
        print("\n" + "=" * 60)
        print("✨ Database setup complete!")
        print(f"📁 Database location: {DB_PATH.absolute()}")
        print("\n🎯 Next Steps:")
        print("   1. Get your Google Gemini API key")
        print("   2. Add it to .env file")
        print("   3. Ready for Week 2!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
