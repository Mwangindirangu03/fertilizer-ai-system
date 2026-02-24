"""
IMPROVED Fertilizer Recommendation Engine
Uses realistic application rates
"""
from typing import Dict, List
import sys
sys.path.insert(0, 'src')
from database import FertilizerDatabase

class FertilizerRecommender:
    def __init__(self):
        self.db = FertilizerDatabase()
        
        # Standard application rates (kg per acre) for different fertilizer types
        self.standard_rates = {
            "DAP": 50,      # Basal application
            "CAN": 50,      # Top dressing
            "NPK": 50,      # Balanced fertilizer
            "Urea": 50,     # Top dressing
            "TSP": 50,      # Phosphorus source
            "Manure": 2000, # Organic - needs more
            "Compost": 2000 # Organic - needs more
        }
    
    def get_fertilizer_rate(self, fertilizer_name: str, farm_size_acres: float) -> float:
        """Get realistic application rate based on fertilizer type"""
        # Determine rate based on fertilizer name
        rate_per_acre = 50  # Default
        
        for key, rate in self.standard_rates.items():
            if key.upper() in fertilizer_name.upper():
                rate_per_acre = rate
                break
        
        return rate_per_acre * farm_size_acres
    
    def score_fertilizer(self, crop: Dict, fertilizer: Dict, budget_per_kg: float = None) -> float:
        """Score fertilizer based on NPK match and budget"""
        score = 100.0
        
        # Calculate NPK matching (60% of score)
        crop_n_ratio = crop["nitrogen_requirement"] / (crop["nitrogen_requirement"] + crop["phosphorus_requirement"] + crop["potassium_requirement"])
        crop_p_ratio = crop["phosphorus_requirement"] / (crop["nitrogen_requirement"] + crop["phosphorus_requirement"] + crop["potassium_requirement"])
        crop_k_ratio = crop["potassium_requirement"] / (crop["nitrogen_requirement"] + crop["phosphorus_requirement"] + crop["potassium_requirement"])
        
        total_npk = fertilizer["nitrogen_content"] + fertilizer["phosphorus_content"] + fertilizer["potassium_content"]
        if total_npk > 0:
            fert_n_ratio = fertilizer["nitrogen_content"] / total_npk
            fert_p_ratio = fertilizer["phosphorus_content"] / total_npk
            fert_k_ratio = fertilizer["potassium_content"] / total_npk
            
            ratio_diff = abs(crop_n_ratio - fert_n_ratio) + abs(crop_p_ratio - fert_p_ratio) + abs(crop_k_ratio - fert_k_ratio)
            npk_penalty = ratio_diff * 30
            score -= min(npk_penalty, 60)
        
        # Budget consideration (40% of score)
        if budget_per_kg:
            if fertilizer["price_per_kg"] > budget_per_kg:
                price_diff = fertilizer["price_per_kg"] - budget_per_kg
                price_penalty = (price_diff / budget_per_kg) * 40
                score -= min(price_penalty, 40)
        
        return max(score, 0)
    
    def get_recommendation(self, crop_name: str, soil_type: str, farm_size_acres: float, budget_total: float = None) -> Dict:
        """Get fertilizer recommendation with realistic quantities"""
        
        # Get crop and soil info
        crop = self.db.get_crop_by_name(crop_name)
        soil = self.db.get_soil_by_type(soil_type)
        
        if not crop:
            return {"error": f"Crop {crop_name} not found"}
        if not soil:
            return {"error": f"Soil {soil_type} not found"}
        
        # Get all fertilizers
        all_fertilizers = self.db.get_all_fertilizers()
        
        # Calculate budget per kg if provided
        budget_per_kg = None
        if budget_total and farm_size_acres:
            estimated_kg = 50 * farm_size_acres  # Assume 50kg per acre average
            budget_per_kg = budget_total / estimated_kg
        
        # Score and calculate for each fertilizer
        scored_fertilizers = []
        for fert in all_fertilizers:
            # Use realistic application rate
            application_rate = self.get_fertilizer_rate(fert["product_name"], farm_size_acres)
            total_cost = application_rate * fert["price_per_kg"]
            
            # Score the fertilizer
            score = self.score_fertilizer(crop, fert, budget_per_kg)
            
            scored_fertilizers.append({
                "fertilizer": fert,
                "score": score,
                "application_rate_kg": application_rate,
                "total_cost": round(total_cost, 2),
                "cost_per_acre": round(total_cost / farm_size_acres, 2)
            })
        
        # Sort by score (highest first)
        scored_fertilizers.sort(key=lambda x: x["score"], reverse=True)
        
        # Filter by budget if provided
        affordable = scored_fertilizers
        if budget_total:
            affordable = [f for f in scored_fertilizers if f["total_cost"] <= budget_total]
        
        if not affordable:
            # If nothing is affordable, show cheapest options
            scored_fertilizers.sort(key=lambda x: x["total_cost"])
            affordable = scored_fertilizers[:3]
        
        # Get top recommendation
        top_choice = affordable[0]
        
        # Get alternatives
        alternatives = affordable[1:4] if len(affordable) > 1 else scored_fertilizers[1:4]
        
        # Build response
        return {
            "crop": crop["crop_name"],
            "soil": soil["soil_type"],
            "farm_size_acres": farm_size_acres,
            "budget_total": budget_total,
            "primary_recommendation": {
                "fertilizer_name": top_choice["fertilizer"]["product_name"],
                "npk": f"{top_choice['fertilizer']['nitrogen_content']}-{top_choice['fertilizer']['phosphorus_content']}-{top_choice['fertilizer']['potassium_content']}",
                "quantity_kg": top_choice["application_rate_kg"],
                "quantity_bags": round(top_choice["application_rate_kg"] / 50, 1),
                "total_cost": top_choice["total_cost"],
                "cost_per_acre": top_choice["cost_per_acre"],
                "price_per_kg": top_choice["fertilizer"]["price_per_kg"],
                "score": round(top_choice["score"], 1),
                "application_notes": top_choice["fertilizer"]["application_notes"]
            },
            "alternatives": [
                {
                    "fertilizer_name": alt["fertilizer"]["product_name"],
                    "npk": f"{alt['fertilizer']['nitrogen_content']}-{alt['fertilizer']['phosphorus_content']}-{alt['fertilizer']['potassium_content']}",
                    "quantity_kg": alt["application_rate_kg"],
                    "total_cost": alt["total_cost"],
                    "cost_per_acre": alt["cost_per_acre"]
                }
                for alt in alternatives
            ],
            "within_budget": top_choice["total_cost"] <= budget_total if budget_total else True
        }

if __name__ == "__main__":
    print("Testing IMPROVED Recommender")
    print("=" * 60)
    
    recommender = FertilizerRecommender()
    
    # Test: Maize, 2 acres, KES 10,000
    rec = recommender.get_recommendation("Maize", "Loam", 2, 10000)
    
    if "error" not in rec:
        print(f"\nCrop: {rec['crop']}")
        print(f"Farm: {rec['farm_size_acres']} acres")
        print(f"Budget: KES {rec['budget_total']:,}")
        print(f"\nTOP RECOMMENDATION:")
        print(f"  {rec['primary_recommendation']['fertilizer_name']}")
        print(f"  Quantity: {rec['primary_recommendation']['quantity_kg']} kg ({rec['primary_recommendation']['quantity_bags']} bags)")
        print(f"  Total Cost: KES {rec['primary_recommendation']['total_cost']:,}")
        print(f"  Within Budget: {'YES ✓' if rec['within_budget'] else 'NO ✗'}")
        
        print(f"\nALTERNATIVES:")
        for i, alt in enumerate(rec['alternatives'][:3], 1):
            print(f"  {i}. {alt['fertilizer_name']}: {alt['quantity_kg']} kg @ KES {alt['total_cost']:,}")
