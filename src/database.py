"""
Database operations for Fertilizer Recommendation System
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent.parent / "data" / "fertilizer_db.sqlite"

class FertilizerDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_all_crops(self) -> List[Dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crops")
        crops = [dict(row) for row in cursor.fetchall()]
        for crop in crops:
            if crop["growth_stages"]:
                crop["growth_stages"] = json.loads(crop["growth_stages"])
        conn.close()
        return crops
    
    def get_crop_by_name(self, crop_name: str) -> Optional[Dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crops WHERE LOWER(crop_name) = LOWER(?)", (crop_name,))
        row = cursor.fetchone()
        if row:
            crop = dict(row)
            if crop["growth_stages"]:
                crop["growth_stages"] = json.loads(crop["growth_stages"])
            conn.close()
            return crop
        conn.close()
        return None
    
    def get_all_soils(self) -> List[Dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soils")
        soils = [dict(row) for row in cursor.fetchall()]
        for soil in soils:
            if soil["characteristics"]:
                soil["characteristics"] = json.loads(soil["characteristics"])
        conn.close()
        return soils
    
    def get_soil_by_type(self, soil_type: str) -> Optional[Dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soils WHERE LOWER(soil_type) = LOWER(?)", (soil_type,))
        row = cursor.fetchone()
        if row:
            soil = dict(row)
            if soil["characteristics"]:
                soil["characteristics"] = json.loads(soil["characteristics"])
            conn.close()
            return soil
        conn.close()
        return None
    
    def get_all_fertilizers(self) -> List[Dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fertilizers ORDER BY price_per_kg")
        fertilizers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return fertilizers
    
    def test_connection(self) -> bool:
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


    def get_database_stats(self):
        """Get statistics about database contents"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM crops")
        stats['crops_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM soils")
        stats['soils_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fertilizers")
        stats['fertilizers_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recommendations")
        stats['recommendations_count'] = cursor.fetchone()[0]
        
        conn.close()
        return stats

if __name__ == "__main__":
    print("Testing Database Connection")
    print("=" * 50)
    db = FertilizerDatabase()
    if db.test_connection():
        print("Connection successful!")
        crops = db.get_all_crops()
        print(f"Found {len(crops)} crops:")
        for crop in crops:
            print(f"  - {crop['crop_name']}")
    else:
        print("Connection failed")
