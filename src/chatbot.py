"""
AI Chatbot for Fertilizer Recommendations
Uses Google Gemini API
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import sys
sys.path.insert(0, 'src')
from database import FertilizerDatabase
from recommender import FertilizerRecommender

# Load environment variables
# Try Streamlit secrets first, then fall back to .env
try:
    import streamlit as st
    API_KEY = st.secrets.get("GOOGLE_API_KEY", None)
except:
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")

class FertilizerChatbot:
    def __init__(self):
        # Configure Gemini API
        if not API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        # Initialize database and recommender
        self.db = FertilizerDatabase()
        self.recommender = FertilizerRecommender()
        
        # Get available options
        self.crops = [c["crop_name"] for c in self.db.get_all_crops()]
        self.soils = [s["soil_type"] for s in self.db.get_all_soils()]
        
        # System prompt
        self.system_prompt = f"""You are a helpful agricultural assistant for Kenyan farmers.
Your role is to help farmers get fertilizer recommendations.

Available crops: {", ".join(self.crops)}
Available soil types: {", ".join(self.soils)}

When a farmer asks for help:
1. Ask what crop they want to plant (if not mentioned)
2. Ask what type of soil they have (if not mentioned)
3. Ask how many acres they want to plant (if not mentioned)
4. Ask their budget in KES (optional)

Be friendly, use simple language, and ask ONE question at a time.
When you have all info, say: "Let me calculate the best fertilizer for you!"

Keep responses SHORT (2-3 sentences max).
"""
        
        # Conversation history
        self.conversation_history = []
        self.user_data = {
            "crop": None,
            "soil": None,
            "acres": None,
            "budget": None
        }
    
    def extract_info(self, user_message: str):
        """Extract crop, soil, acres, budget from user message"""
        message_lower = user_message.lower()
        
        # Extract crop
        for crop in self.crops:
            if crop.lower() in message_lower:
                self.user_data["crop"] = crop
                break
        
        # Extract soil
        for soil in self.soils:
            if soil.lower() in message_lower:
                self.user_data["soil"] = soil
                break
        
        # Extract acres (look for numbers)
        words = message_lower.split()
        for i, word in enumerate(words):
            if word in ["acre", "acres", "ac"] and i > 0:
                try:
                    self.user_data["acres"] = float(words[i-1])
                except:
                    pass
        
        # Extract budget (look for numbers with KES or shillings)
        for i, word in enumerate(words):
            if word in ["kes", "ksh", "shillings", "bob"] and i > 0:
                try:
                    # Remove commas and convert
                    budget_str = words[i-1].replace(",", "")
                    self.user_data["budget"] = float(budget_str)
                except:
                    pass
    
    def check_ready_for_recommendation(self) -> bool:
        """Check if we have enough info for recommendation"""
        return (self.user_data["crop"] is not None and 
                self.user_data["soil"] is not None and 
                self.user_data["acres"] is not None)
    
    def get_recommendation_text(self) -> str:
        """Get formatted recommendation"""
        rec = self.recommender.get_recommendation(
            crop_name=self.user_data["crop"],
            soil_type=self.user_data["soil"],
            farm_size_acres=self.user_data["acres"],
            budget_total=self.user_data["budget"]
        )
        
        if "error" in rec:
            return f"Sorry, I encountered an error: {rec['error']}"
        
        prim = rec["primary_recommendation"]
        
        response = f"""Here is my recommendation for your {rec['crop']} farm:

BEST CHOICE: {prim['fertilizer_name']}
- Quantity needed: {prim['quantity_kg']} kg ({prim['quantity_bags']} bags of 50kg)
- Total cost: KES {prim['total_cost']:,.0f}
- Cost per acre: KES {prim['cost_per_acre']:,.0f}

APPLICATION: {prim['application_notes']}
"""
        
        if self.user_data["budget"]:
            if rec["within_budget"]:
                response += f"\n✓ This fits your budget of KES {self.user_data['budget']:,.0f}"
            else:
                response += f"\n⚠ This exceeds your budget of KES {self.user_data['budget']:,.0f}"
                if rec["alternatives"]:
                    alt = rec["alternatives"][0]
                    response += f"\n\nCHEAPER OPTION: {alt['fertilizer_name']}"
                    response += f"\n- Quantity: {alt['quantity_kg']} kg"
                    response += f"\n- Cost: KES {alt['total_cost']:,.0f}"
        
        return response
    
    def chat(self, user_message: str) -> str:
        """Main chat function"""
        # Extract any information from message
        self.extract_info(user_message)
        
        # Check if ready for recommendation
        if self.check_ready_for_recommendation():
            return self.get_recommendation_text()
        
        # Otherwise, continue conversation with AI
        # Build prompt with context
        context = f"""System: {self.system_prompt}

Current information collected:
- Crop: {self.user_data['crop'] or 'Not specified'}
- Soil: {self.user_data['soil'] or 'Not specified'}  
- Farm size: {self.user_data['acres'] or 'Not specified'} acres
- Budget: {self.user_data['budget'] or 'Not specified'} KES

User: {user_message}

Assistant (ask for missing info, be brief):"""
        
        try:
            response = self.model.generate_content(context)
            return response.text
        except Exception as e:
            return f"Sorry, I had trouble processing that. Error: {str(e)}"
    
    def reset(self):
        """Reset conversation"""
        self.user_data = {
            "crop": None,
            "soil": None,
            "acres": None,
            "budget": None
        }
        self.conversation_history = []

if __name__ == "__main__":
    print("Testing Fertilizer Chatbot")
    print("=" * 60)
    
    try:
        bot = FertilizerChatbot()
        print("✓ Chatbot initialized successfully!")
        print("✓ Connected to Google Gemini API")
        
        # Simulate conversation
        print("\n--- Test Conversation ---\n")
        
        messages = [
            "Hello, I need help with fertilizer",
            "I want to plant maize",
            "I have loam soil and 2 acres",
            "My budget is 8000 shillings"
        ]
        
        for msg in messages:
            print(f"Farmer: {msg}")
            response = bot.chat(msg)
            print(f"Bot: {response}")
            print()
            
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("Make sure your Google API key is in .env file!")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
