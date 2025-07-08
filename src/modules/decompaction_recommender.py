import pandas as pd
from src.utils import LLM

class DecompactionRecommender():
    def __init__(self, decompaction_methods_path, system_prompt, user_prompt, api_key):
        self.decompaction_methods_data = pd.read_csv(decompaction_methods_path)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key = api_key)

    def get_optimal_moisture_range(self, sand, silt, clay):
        """
        Determine optimal moisture range for decompaction based on soil texture
        """
        # Classify soil texture
        if sand > 85:
            soil_type = "Sandy"
            optimal_moisture = (8, 12)
        elif sand > 70:
            soil_type = "Sandy Loam"
            optimal_moisture = (10, 14)
        elif clay > 40:
            soil_type = "Clay"
            optimal_moisture = (15, 22)
        elif clay > 27:
            soil_type = "Clay Loam"
            optimal_moisture = (14, 20)
        elif silt > 80:
            soil_type = "Silt"
            optimal_moisture = (12, 18)
        elif silt > 50:
            soil_type = "Silt Loam"
            optimal_moisture = (12, 18)
        else:
            soil_type = "Loam"
            optimal_moisture = (12, 18)
        
        return soil_type, optimal_moisture

    def check_subsoiling_feasibility(self, sand, silt, clay, soil_moisture, bulk_density, penetration_resistance):
        """
        Check if subsoiling is feasible based on soil conditions
        """
        soil_type, optimal_moisture = self.get_optimal_moisture_range(sand, silt, clay)
        
        # Check moisture conditions
        moisture_suitable = optimal_moisture[0] <= soil_moisture <= optimal_moisture[1]
        
        # Check compaction severity
        if sand > 70:  # Sandy soils
            compaction_severe = bulk_density > 1.6
        elif clay > 30:  # Clay soils
            compaction_severe = bulk_density > 1.3
        else:  # Loamy soils
            compaction_severe = bulk_density > 1.4
        
        # Check penetration resistance
        penetration_severe = penetration_resistance > 2.0
        
        subsoiling_recommended = moisture_suitable and (compaction_severe or penetration_severe)
        
        return {
            "soil_type": soil_type,
            "optimal_moisture_range": optimal_moisture,
            "current_moisture_suitable": moisture_suitable,
            "compaction_severe": compaction_severe,
            "penetration_severe": penetration_severe,
            "subsoiling_recommended": subsoiling_recommended
        }

    def filter_decompaction_methods(self, crop_type, soil_type):
        """
        Filter available decompaction methods based on crop and soil type
        """
        data = self.decompaction_methods_data
        
        # First try to find crop-specific methods
        crop_methods = data[data["Crop"] == crop_type]
        if crop_methods.empty:
            crop_methods = data[data["Crop"] == "General"]
        
        # Filter by soil type compatibility
        suitable_methods = crop_methods[
            (crop_methods["Suitable_Soil_Types"].str.contains(soil_type, na=False)) |
            (crop_methods["Suitable_Soil_Types"] == "All")
        ]
        
        return suitable_methods[['Method', 'Optimal_Moisture_Min', 'Optimal_Moisture_Max', 
                                'Effectiveness_Rating', 'Implementation_Notes']].to_dict(orient='records')

    def recommend(self, crop_type, sand, silt, clay, soil_moisture, bulk_density, 
                  penetration_resistance, organic_matter, soil_depth, traffic_intensity, 
                  compaction_history):
        """
        Generate decompaction recommendations
        """
        # Get soil type and moisture analysis
        soil_type, optimal_moisture = self.get_optimal_moisture_range(sand, silt, clay)
        
        # Check subsoiling feasibility
        subsoiling_analysis = self.check_subsoiling_feasibility(
            sand, silt, clay, soil_moisture, bulk_density, penetration_resistance
        )
        
        # Get available methods
        available_methods = self.filter_decompaction_methods(crop_type, soil_type)
        
        # Prepare inputs for LLM
        inputs = {
            "crop_type": crop_type,
            "sand": sand,
            "silt": silt,
            "clay": clay,
            "soil_moisture": soil_moisture,
            "bulk_density": bulk_density,
            "penetration_resistance": penetration_resistance,
            "organic_matter": organic_matter,
            "soil_depth": soil_depth,
            "traffic_intensity": traffic_intensity,
            "compaction_history": compaction_history
        }
        
        self.user_prompt = self.user_prompt.format(**inputs)
        return self.llm.generate(self.system_prompt, self.user_prompt)
        
        # Return combined analysis
        # return {
        #     "soil_analysis": subsoiling_analysis,
        #     "available_methods": available_methods,
        #     "llm_recommendation": llm_response
        # }

    def get_moisture_recommendation(self, sand, silt, clay):
        """
        Get specific moisture recommendations for decompaction timing
        """
        soil_type, optimal_moisture = self.get_optimal_moisture_range(sand, silt, clay)
        
        return {
            "soil_type": soil_type,
            "optimal_moisture_range": f"{optimal_moisture[0]}-{optimal_moisture[1]}%",
            "subsoiling_timing": "Implement subsoiling when soil moisture is within optimal range",
            "avoid_conditions": "Avoid when soil is too wet (above range) or too dry (below range)"
        }